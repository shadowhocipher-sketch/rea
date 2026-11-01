"""固定柱（螺丝柱）：自攻螺丝柱、热熔螺母柱、螺丝过孔柱 + 沉头孔。

局部坐标：柱子底面中心在原点，沿 +Z 生长到 ``height``；孔从柱顶（z = height）往下打。
摆放到外壳里时，由 :mod:`hwcad.enclosure` 把柱子"立"在下壳底板上，或"倒挂"在上壳顶板下。

尺寸来源（详见 cad/DFM.md）：

* 自攻螺丝：底孔 0.8 × d、柱外径 2.0 × d —— EJOT PT / DELTA PT 产品资料（DFM:FAST-1）。
  该比例针对注塑热塑性塑料；3D 打印件建议先打试样再调整 ``hole_factor``。
* 热熔螺母：M3 底孔 4.0 mm、嵌件长 5.8 mm、最小壁 1.8 mm —— Accu HTBI-M3-BR 商品页
  （DFM:FAST-2，B 级）。其他规格请按所用嵌件的数据填写。
* 过孔：公称直径 + 0.4 mm（DFM:FAST-3，待核实）。
"""
from __future__ import annotations

import re

from build123d import Align, Cylinder, Location, Part

from .process import (
    CLEARANCE_HOLE_EXTRA,
    HEAT_INSERT_TABLE,
    SELF_TAP_BOSS_FACTOR,
    SELF_TAP_HOLE_FACTOR,
)

_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


def thread_diameter(thread: str | float) -> float:
    """``"M3"`` -> 3.0；数字原样返回（mm）。"""
    if isinstance(thread, (int, float)):
        return float(thread)
    m = re.fullmatch(r"[Mm](\d+(?:\.\d+)?)", thread.strip())
    if not m:
        raise ValueError(f"无法解析螺纹规格 {thread!r}，请写成 M3 / M2.5 或直接给直径")
    return float(m.group(1))


def boss(outer_d: float, hole_d: float, height: float, hole_depth: float | None = None) -> Part:
    """通用圆柱固定柱。

    Args:
        outer_d: 柱外径，mm。
        hole_d: 孔径，mm（0 表示实心）。
        height: 柱高，mm。
        hole_depth: 孔深（从柱顶往下），mm；None = 打穿整根柱子。

    Returns:
        底面中心在原点、沿 +Z 的实体。
    """
    if outer_d <= hole_d:
        raise ValueError("外径必须大于孔径")
    if height <= 0:
        raise ValueError("height 必须为正")
    body = Cylinder(outer_d / 2, height, align=_BOTTOM)
    if hole_d > 0:
        depth = height + 0.02 if hole_depth is None else min(hole_depth, height + 0.02)
        hole = Cylinder(hole_d / 2, depth, align=_BOTTOM).moved(Location((0, 0, height - depth + 0.01)))
        body = body - hole
    return body


def self_tap_boss(
    screw: str | float = "M3",
    height: float = 8.0,
    hole_factor: float = SELF_TAP_HOLE_FACTOR,
    outer_factor: float = SELF_TAP_BOSS_FACTOR,
    hole_depth: float | None = None,
) -> tuple[Part, dict]:
    """自攻螺丝柱。

    Args:
        screw: 螺纹规格（"M3"）或公称直径 mm。
        height: 柱高，mm（默认 8）。
        hole_factor: 底孔 / 公称直径（默认 0.8，EJOT PT）。
        outer_factor: 柱外径 / 公称直径（默认 2.0，EJOT PT）。
        hole_depth: 孔深，mm；None = 打穿。EJOT 建议拧入深度 ≥ 2 × d。

    Returns:
        (实体, 设计数据 dict)
    """
    d = thread_diameter(screw)
    hole = hole_factor * d
    outer = outer_factor * d
    info = {
        "kind": "self_tap",
        "screw_d": d,
        "hole_d": round(hole, 3),
        "outer_d": round(outer, 3),
        "height": height,
        "min_engagement_recommended": 2 * d,
        "source": "DFM:FAST-1 EJOT PT（注塑件比例；打印件需试样）",
    }
    return boss(outer, hole, height, hole_depth), info


def heat_insert_boss(
    thread: str = "M3",
    height: float = 8.0,
    insert_hole_d: float | None = None,
    insert_length: float | None = None,
    min_wall: float | None = None,
) -> tuple[Part, dict]:
    """热熔螺母（铜嵌件）柱。

    Args:
        thread: 螺纹规格，例如 "M3"。
        height: 柱高，mm（默认 8），必须 ≥ 孔深。
        insert_hole_d: 底孔直径，mm；None 时查 :data:`hwcad.process.HEAT_INSERT_TABLE`，
            查不到会报错，要求按嵌件数据手册填写。
        insert_length: 嵌件长度，mm；孔深 = 嵌件长 + 1.0 mm 余量（估算，给熔料留空间）。
        min_wall: 孔周最小壁厚，mm；柱外径 = 孔径 + 2 × min_wall。

    Returns:
        (实体, 设计数据 dict)
    """
    row = HEAT_INSERT_TABLE.get(thread.upper()) if isinstance(thread, str) else None
    if insert_hole_d is None or insert_length is None or min_wall is None:
        if row is None:
            raise ValueError(
                f"热熔螺母 {thread} 没有查到来源的默认尺寸，请在参数里给出 insert_hole_d / insert_length / min_wall"
            )
        insert_hole_d = row["hole_d"] if insert_hole_d is None else insert_hole_d
        insert_length = row["length"] if insert_length is None else insert_length
        min_wall = row["min_wall"] if min_wall is None else min_wall
    depth = insert_length + 1.0
    if depth > height:
        raise ValueError(f"柱高 {height} mm 小于孔深 {depth} mm（嵌件长 + 1 mm）")
    outer = insert_hole_d + 2 * min_wall
    info = {
        "kind": "heat_insert",
        "thread": thread,
        "hole_d": insert_hole_d,
        "hole_depth": depth,
        "outer_d": round(outer, 3),
        "height": height,
        "source": row["source"] if row else "参数给定",
        "note": "孔深 = 嵌件长 + 1.0 mm（估算余量）",
    }
    return boss(outer, insert_hole_d, height, depth), info


def clearance_post(
    screw: str | float = "M3",
    height: float = 5.0,
    clearance_d: float | None = None,
    outer_d: float | None = None,
) -> tuple[Part, dict]:
    """螺丝过孔柱（螺丝从这一侧穿过去，拧进另一半壳的螺丝柱）。

    Args:
        screw: 螺纹规格或直径。
        height: 柱高，mm。
        clearance_d: 过孔直径，mm；默认 d + 0.4（DFM:FAST-3，待核实）。
        outer_d: 柱外径，mm；默认 2.0 × d + 1.0（估算，保证孔周壁 ≥ 约 1.3 mm @M3）。
    """
    d = thread_diameter(screw)
    cd = d + CLEARANCE_HOLE_EXTRA if clearance_d is None else clearance_d
    od = 2.0 * d + 1.0 if outer_d is None else outer_d
    info = {"kind": "clearance_post", "screw_d": d, "hole_d": cd, "outer_d": od, "height": height,
            "source": "DFM:FAST-3（过孔 d+0.4，待核实）；外径为估算"}
    return boss(od, cd, height), info


def counterbore_cutter(
    screw: str | float = "M3",
    depth: float = 2.0,
    head_d: float | None = None,
    through_len: float = 30.0,
    clearance_d: float | None = None,
) -> Part:
    """沉头孔 + 过孔去料体（局部坐标：z = 0 为外表面，往 -Z 是往壳内）。

    Args:
        screw: 螺纹规格或直径。
        depth: 沉头孔深，mm（0 = 不做沉头）。
        head_d: 沉头孔直径，mm；默认 2.0 × d + 0.6（估算，按 ISO 4762 头径约 1.83d 留余量，待核实）。
        through_len: 过孔长度（往壳内），mm。
        clearance_d: 过孔直径，mm；默认 d + 0.4。
    """
    d = thread_diameter(screw)
    cd = d + CLEARANCE_HOLE_EXTRA if clearance_d is None else clearance_d
    hd = 2.0 * d + 0.6 if head_d is None else head_d
    cut = Cylinder(cd / 2, through_len + 1.0, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Location((0, 0, 1.0)))
    if depth > 0:
        cut = cut + Cylinder(hd / 2, depth + 1.0, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Location((0, 0, 1.0)))
    return cut
