"""悬臂卡扣 + 配对卡槽。

应变估算依据（详见 cad/DFM.md 的卡扣小节）
-----------------------------------------
* 等截面矩形悬臂梁：y = 0.67·ε·L²/t，即 ε = 1.5·t·y/L²
  （Bayer / Covestro《Snap-Fit Joints for Plastics》，DFM:SNAP-1；原文未能打开，经二手转述，待核实）。
* BASF《Snap-Fit Design Manual》指出经典梁公式低估根部应变，引入挠度放大系数 Q（DFM:SNAP-2）。
  本模块的 ``q`` 参数默认 1（经典公式），需要保守时按 BASF 手册取 Q < 1。
* 许用应变随材料而变（例如 Bayer 资料里 Bayblend 一次装配 2.5%），本库不给默认值，
  由调用者按材料数据填写 ``allowable_strain``。3D 打印件沿 Z 方向受弯的卡扣，第三方资料建议
  许用值再减半（DFM:SNAP-3，C 级，待核实）。

几何（"墙坐标系"，见 :func:`hwcad.frames.wall_plane`）
----------------------------------------------------
局部 +X = 墙的外法线，局部 +Z = 全局 +Z，原点在外表面、全局 z = 0。

* 下壳：在内壁以内 ``gap`` 处立一根悬臂梁，从分模面 ``split_z`` 往上长 ``length``；
  梁根部用一块"根座"连回下壳内壁（分模面以下）。梁顶端有向外（+X）凸出 ``undercut`` 的卡钩：
  上面是导入斜面（``lead_angle``，相对竖直方向），下面是平的止退面。
* 上壳：内壁上对应位置挖一个卡槽（盲槽，深度 = ``undercut - gap + clearance``）。
  装配时卡钩挠度 = ``undercut - gap``，用它估算根部应变。
"""
from __future__ import annotations

import math

from build123d import Align, Box, Location, Part, Plane, Polygon, extrude

from .buttons import cantilever_strain
from .frames import Feature


def snap_hook_profile(thickness: float, length: float, undercut: float, flat: float, lead_angle: float) -> list[tuple[float, float]]:
    """卡扣梁 + 卡钩的 XZ 截面（局部坐标，梁外侧面在 x = 0，根部在 z = 0）。"""
    ramp_h = undercut / math.tan(math.radians(lead_angle))
    hook_h = flat + ramp_h
    if hook_h >= length:
        raise ValueError("卡钩高度超过梁长，减小 undercut 或增大 lead_angle / length")
    z_hook = length - hook_h
    return [
        (-thickness, 0.0),
        (0.0, 0.0),
        (0.0, z_hook),
        (undercut, z_hook),
        (undercut, z_hook + flat),
        (0.0, length),
        (-thickness, length),
    ]


def cantilever_snap(
    length: float = 10.0,
    thickness: float = 1.2,
    width: float = 5.0,
    undercut: float = 0.8,
    flat: float = 0.6,
    lead_angle: float = 30.0,
) -> Part:
    """单独的卡扣梁 + 卡钩实体（局部：梁外侧面 x = 0，根部 z = 0，宽度沿 Y 居中）。

    Args:
        length: 梁长（根部到顶端），mm。
        thickness: 梁厚（X 方向，弯曲方向），mm。
        width: 梁宽（Y 方向），mm。
        undercut: 卡钩凸出量，mm。
        flat: 卡钩止退面以上的竖直平台高度，mm。
        lead_angle: 导入斜面与竖直方向的夹角，°（越小越好装）。
    """
    pts = snap_hook_profile(thickness, length, undercut, flat, lead_angle)
    return extrude(Plane.XZ * Polygon(*pts, align=None), amount=width / 2, both=True)


def snap_fit(
    wall: float,
    split_z: float,
    length: float = 10.0,
    thickness: float = 1.2,
    width: float = 5.0,
    undercut: float = 0.8,
    gap: float = 0.2,
    flat: float = 0.6,
    lead_angle: float = 30.0,
    clearance: float = 0.2,
    root_height: float = 3.0,
    q: float = 1.0,
    allowable_strain: float | None = None,
    min_wall: float | None = None,
    name: str = "snap",
) -> Feature:
    """外壳侧壁上的一对卡扣（下壳的梁 + 上壳的卡槽），局部为"墙坐标系"。

    Args:
        wall: 壁厚，mm。
        split_z: 分模面高度，mm。
        length, thickness, width, undercut, flat, lead_angle: 见 :func:`cantilever_snap`。
        gap: 梁外侧面与上壳内壁的间隙，mm（必须 < undercut）。
        clearance: 卡槽各方向的间隙，mm。
        root_height: 根座在分模面以下的高度，mm。
        q: 挠度放大系数 Q（BASF），默认 1。
        allowable_strain: 材料许用应变；给出时超出会警告。
        min_wall: 工艺最小壁厚；给出时检查卡槽处剩余壁厚。
        name: 特征名。

    Returns:
        Feature：add（梁 + 根座，归下壳），cut（卡槽，只切上壳），info（挠度、应变、剩余壁厚）。
    """
    if gap >= undercut:
        raise ValueError("gap 必须小于 undercut，否则卡钩钩不住")
    deflection = undercut - gap
    x_face = -(wall + gap)  # 梁外侧面
    beam = cantilever_snap(length, thickness, width, undercut, flat, lead_angle).moved(Location((x_face, 0, split_z)))
    root = Box(gap + thickness + 0.3, width, root_height, align=(Align.MAX, Align.CENTER, Align.MAX)).moved(
        Location((-wall + 0.3, 0, split_z + 0.01))
    )
    add = beam + root
    ramp_h = undercut / math.tan(math.radians(lead_angle))
    z_hook_bottom = split_z + length - flat - ramp_h
    pocket_depth = deflection + clearance  # 从上壳内壁往外
    pocket = Box(pocket_depth + 0.5, width + 2 * clearance, flat + ramp_h + 2 * clearance,
                 align=(Align.MAX, Align.CENTER, Align.MIN)).moved(
        Location((-wall + pocket_depth, 0, z_hook_bottom - clearance))
    )
    strain = cantilever_strain(length, thickness, deflection, q)
    remain = wall - pocket_depth
    info = {
        "deflection": round(deflection, 3),
        "root_strain_est": round(strain, 5),
        "strain_formula": "ε = 1.5·t·y/(L²·Q)（DFM:SNAP-1/2，估算）",
        "hook_z_range": [round(z_hook_bottom, 3), round(split_z + length, 3)],
        "pocket_depth_into_wall": round(pocket_depth, 3),
        "wall_remaining_at_pocket": round(remain, 3),
        "warnings": [],
    }
    if allowable_strain is not None and strain > allowable_strain:
        info["warnings"].append(f"根部应变估算 {strain:.2%} > 许用 {allowable_strain:.2%}")
    if min_wall is not None and remain + 1e-9 < min_wall:
        info["warnings"].append(f"卡槽处剩余壁厚 {remain:.2f} mm < 工艺最小壁厚 {min_wall} mm")
    return Feature(name=name, add=add, cut=pocket, add_to="lower", cut_from=("upper",), info=info)
