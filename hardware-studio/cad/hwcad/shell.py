"""外壳主体：圆角盒、抽壳、按 Z 分模成两半、止口配合。

坐标约定见 :mod:`hwcad.frames`：X/Y 以外形中心为 0，Z = 0 为底面外表面。

止口（lip）的做法
-----------------
* 下壳（``lower``）在分模面以上多出一圈"止口环"：占据壁厚的内侧 ``lip_thickness``，
  高 ``lip_height``。
* 上壳（``upper``）在分模面以上 ``lip_height + lip_clearance`` 的范围内，把壁的内侧
  挖掉 ``lip_thickness + lip_clearance``，形成让位槽。
* 这样止口和让位槽之间水平、竖直方向都有 ``lip_clearance`` 的单边间隙，干涉为 0。
* 上壳在止口区剩下的壁厚 = ``wall - lip_thickness - lip_clearance``，必须 ≥ 工艺最小壁厚。
"""
from __future__ import annotations

from dataclasses import dataclass

from build123d import (
    Align,
    Axis,
    Box,
    Location,
    Part,
    Plane,
    RectangleRounded,
    extrude,
    fillet,
)

_MIN_R = 0.05  # 小于它的圆角当作尖角处理（mm）


def rounded_rect_prism(length: float, width: float, corner_radius: float, z0: float, height: float) -> Part:
    """XY 截面为圆角矩形的直柱体。

    Args:
        length: X 方向尺寸，mm。
        width: Y 方向尺寸，mm。
        corner_radius: 竖直棱的圆角半径，mm；≤0.05 时为尖角。
        z0: 底面 Z 坐标，mm。
        height: Z 方向高度，mm（>0）。

    Returns:
        以 XY 中心为原点、底面在 ``z0`` 的实体。
    """
    if length <= 0 or width <= 0 or height <= 0:
        raise ValueError(f"尺寸必须为正：{length=} {width=} {height=}")
    r = min(corner_radius, min(length, width) / 2 - 1e-3)
    if r <= _MIN_R:
        return Box(length, width, height, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, z0)))
    sk = Plane.XY.offset(z0) * RectangleRounded(length, width, r)
    return extrude(sk, amount=height)


def rounded_box(
    length: float,
    width: float,
    height: float,
    corner_radius: float = 3.0,
    edge_radius: float = 1.0,
) -> Part:
    """圆角盒（实心）。

    Args:
        length: X 外形，mm。
        width: Y 外形，mm。
        height: Z 外形，mm。
        corner_radius: 4 条竖直棱的圆角半径，mm（默认 3）。
        edge_radius: 顶面、底面一圈棱的圆角半径，mm（默认 1；0 表示不倒）。
            必须 ≤ corner_radius，且 < height/2。

    Returns:
        XY 居中、Z 从 0 到 height 的实体。
    """
    body = rounded_rect_prism(length, width, corner_radius, 0.0, height)
    if edge_radius > _MIN_R:
        if edge_radius > corner_radius + 1e-9 and corner_radius > _MIN_R:
            raise ValueError("edge_radius 不能大于 corner_radius")
        if edge_radius >= height / 2:
            raise ValueError("edge_radius 必须小于 height/2")
        zmin_edges = body.edges().group_by(Axis.Z)[0]
        zmax_edges = body.edges().group_by(Axis.Z)[-1]
        body = fillet(zmin_edges + zmax_edges, edge_radius)
    return body


def hollow_box(
    length: float,
    width: float,
    height: float,
    wall: float = 2.0,
    corner_radius: float = 3.0,
    edge_radius: float = 1.0,
) -> Part:
    """抽壳后的圆角盒（封闭空腔）。内腔圆角 = 外圆角 - 壁厚（不小于 0），保证壁厚均匀。

    Args:
        wall: 壁厚，mm（默认 2.0，FDM 默认值见 :mod:`hwcad.process`）。
        其余同 :func:`rounded_box`。
    """
    if wall * 2 >= min(length, width, height):
        raise ValueError("壁厚太大，内腔为空")
    outer = rounded_box(length, width, height, corner_radius, edge_radius)
    inner = rounded_box(
        length - 2 * wall,
        width - 2 * wall,
        height - 2 * wall,
        max(corner_radius - wall, 0.0),
        max(edge_radius - wall, 0.0),
    ).moved(Location((0, 0, wall)))
    return outer - inner


@dataclass
class ShellSpec:
    """外壳主体参数（全部 mm）。

    Attributes:
        length, width, height: 外形 X / Y / Z。
        wall: 壁厚。
        corner_radius: 竖直棱外圆角。
        edge_radius: 顶 / 底面棱外圆角（≤ corner_radius）。
        split_z: 分模面高度（从底面外表面量起）。
        lip_height: 止口高度；0 表示不做止口（平口对接）。
        lip_thickness: 止口厚度（占壁厚内侧）。
        lip_clearance: 止口单边配合间隙（工艺相关，见 :mod:`hwcad.process`）。
        style: ``top_bottom``（上下壳）或 ``front_back``（前后壳），只影响零件命名。
    """

    length: float = 80.0
    width: float = 50.0
    height: float = 25.0
    wall: float = 2.0
    corner_radius: float = 4.0
    edge_radius: float = 1.0
    split_z: float = 10.0
    lip_height: float = 2.0
    lip_thickness: float = 0.8
    lip_clearance: float = 0.3
    style: str = "top_bottom"

    @property
    def size(self) -> tuple[float, float, float]:
        return (self.length, self.width, self.height)

    def part_names(self) -> dict[str, str]:
        """内部名 lower/upper -> 对外名（bottom/top 或 back/front）。"""
        if self.style == "front_back":
            return {"lower": "back", "upper": "front"}
        return {"lower": "bottom", "upper": "top"}

    def validate(self, min_wall: float | None = None) -> list[str]:
        """检查参数自洽；返回问题列表（空 = 通过）。``min_wall`` 给出时同时检查工艺最小壁厚。"""
        errs: list[str] = []
        t = self.wall
        if self.style not in ("top_bottom", "front_back"):
            errs.append("style 必须是 top_bottom 或 front_back")
        if not (t + self.edge_radius <= self.split_z <= self.height - t - self.lip_height - self.lip_clearance - self.edge_radius):
            errs.append(
                f"split_z={self.split_z} 需在 [{t + self.edge_radius}, "
                f"{self.height - t - self.lip_height - self.lip_clearance - self.edge_radius}] 内（避开顶/底圆角和顶板）"
            )
        if self.lip_height > 0:
            remain = t - self.lip_thickness - self.lip_clearance
            if remain <= 0:
                errs.append("lip_thickness + lip_clearance 必须小于 wall")
            elif min_wall is not None and remain + 1e-9 < min_wall:
                errs.append(f"上壳止口区剩余壁厚 {remain:.2f} mm < 工艺最小壁厚 {min_wall} mm")
            if min_wall is not None and self.lip_thickness + 1e-9 < min_wall:
                errs.append(f"止口厚度 {self.lip_thickness} mm < 工艺最小壁厚 {min_wall} mm")
        if min_wall is not None and t + 1e-9 < min_wall:
            errs.append(f"壁厚 {t} mm < 工艺最小壁厚 {min_wall} mm")
        return errs


def _inset_prism(spec: ShellSpec, inset: float, z0: float, h: float) -> Part:
    return rounded_rect_prism(
        spec.length - 2 * inset,
        spec.width - 2 * inset,
        max(spec.corner_radius - inset, 0.0),
        z0,
        h,
    )


def make_shell(spec: ShellSpec) -> dict[str, Part]:
    """按 ``spec`` 生成两半外壳。

    Returns:
        ``{"lower": Part, "upper": Part}``。lower 含底板，upper 含顶板。
    """
    errs = spec.validate()
    if errs:
        raise ValueError("; ".join(errs))
    L, W, H, t = spec.length, spec.width, spec.height, spec.wall
    shell = hollow_box(L, W, H, t, spec.corner_radius, spec.edge_radius)
    big = 2 * max(L, W, H)
    below = Box(big, big, spec.split_z, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -0.0)))
    above = Box(big, big, H, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, spec.split_z)))
    lower = shell & below
    upper = shell & above
    if spec.lip_height > 0:
        ring = _inset_prism(spec, t - spec.lip_thickness, spec.split_z, spec.lip_height) - _inset_prism(
            spec, t, spec.split_z - 0.01, spec.lip_height + 0.02
        )
        lower = lower + ring
        groove = _inset_prism(
            spec,
            t - spec.lip_thickness - spec.lip_clearance,
            spec.split_z - 0.01,
            spec.lip_height + spec.lip_clearance + 0.01,
        )
        upper = upper - groove
    return {"lower": _as_part(lower), "upper": _as_part(upper)}


def _as_part(shape) -> Part:
    """布尔运算结果统一成 Part。"""
    if isinstance(shape, Part):
        return shape
    return Part(shape.wrapped)
