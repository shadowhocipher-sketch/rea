"""屏幕窗：矩形 / 圆形开窗，可选内侧台阶（用于压住保护玻璃或屏幕模组边框）。

局部坐标（见 :mod:`hwcad.frames`）：z = 0 为外表面，-Z 往壳内；窗口中心在原点。

* 透光开口 ``opening``：从外表面打穿整个壁厚，尺寸 = 屏幕可视区（VA）+ 每边 ``margin``。
* 台阶 ``step``：从**内表面**往外挖 ``step_depth`` 深的凹槽，尺寸 = 玻璃 / 模组外形 + 每边间隙。
  台阶之外剩下的壁（压边）厚度 = ``wall - step_depth``，必须 ≥ 工艺最小壁厚。
"""
from __future__ import annotations

from build123d import Align, Box, Cylinder, Location, Part, Plane, RectangleRounded, extrude

from .frames import Feature


def _profile_prism(shape: str, w: float, h: float, r: float, z_top: float, depth: float) -> Part:
    """局部坐标里，从 z_top 往 -Z 延伸 depth 的柱体（矩形或圆形截面）。"""
    if shape == "circle":
        return Cylinder(w / 2, depth, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Location((0, 0, z_top)))
    if shape != "rect":
        raise ValueError("shape 必须是 rect 或 circle")
    rr = min(r, min(w, h) / 2 - 1e-3)
    if rr <= 0.05:
        return Box(w, h, depth, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Location((0, 0, z_top)))
    return extrude(Plane.XY.offset(z_top - depth) * RectangleRounded(w, h, rr), amount=depth)


def screen_window(
    wall: float,
    shape: str = "rect",
    width: float = 30.0,
    height: float = 15.0,
    corner_radius: float = 1.0,
    margin: float = 0.0,
    step_width: float | None = None,
    step_height: float | None = None,
    step_depth: float = 0.0,
    step_clearance: float = 0.2,
    step_corner_radius: float = 0.5,
    min_wall: float | None = None,
    name: str = "screen_window",
) -> Feature:
    """屏幕窗特征。

    Args:
        wall: 所在面的壁厚，mm。
        shape: ``rect`` 或 ``circle``（圆形时 ``width`` 为直径，``height`` 忽略）。
        width, height: 可视区尺寸（局部 X / Y），mm。
        corner_radius: 矩形开口圆角，mm。
        margin: 开口每边比可视区大多少，mm（默认 0）。
        step_width, step_height: 玻璃 / 模组外形（局部 X / Y），mm；None 表示不做台阶。
            圆形时 ``step_width`` 为直径。
        step_depth: 台阶深度（从内表面往外），mm；0 = 不做台阶。
        step_clearance: 台阶每边间隙，mm（默认 0.2，按工艺 fit_clearance 调整）。
        step_corner_radius: 台阶圆角半径，mm（默认 0.5）。屏幕模组 / 玻璃通常是尖角，
            圆角 r 需满足 √2·(r - step_clearance) ≤ r，即 r ≤ 约 3.4 × step_clearance，否则角上干涉。
        min_wall: 工艺最小壁厚，mm；给出时检查压边剩余厚度。
        name: 特征名。

    Returns:
        :class:`~hwcad.frames.Feature`（只有 cut），``info`` 里有开口和台阶的实际尺寸与警告。
    """
    if shape == "circle":
        height = width
    ow, oh = width + 2 * margin, height + 2 * margin
    cut = _profile_prism(shape, ow, oh, corner_radius + margin, 1.0, wall + 2.0)
    info: dict = {"shape": shape, "opening": [round(ow, 3), round(oh, 3)], "warnings": []}
    has_step = step_depth > 0 and step_width is not None
    if has_step:
        sh = step_width if shape == "circle" else (step_height if step_height is not None else step_width)
        sw = step_width + 2 * step_clearance
        sh = sh + 2 * step_clearance
        if sw <= ow or sh <= oh:
            info["warnings"].append("台阶尺寸不大于开口，台阶无效")
        if step_depth >= wall:
            raise ValueError(f"step_depth={step_depth} 必须小于壁厚 {wall}")
        remain = wall - step_depth
        info["step"] = [round(sw, 3), round(sh, 3), step_depth]
        info["bezel_thickness"] = round(remain, 3)
        if min_wall is not None and remain + 1e-9 < min_wall:
            info["warnings"].append(f"压边厚度 {remain:.2f} mm < 工艺最小壁厚 {min_wall} mm")
        # 从内表面 (z=-wall) 往外到 z = -(wall - step_depth)，再往里多切 1 mm 保证切干净
        cut = cut + _profile_prism(shape, sw, sh, step_corner_radius, -remain, step_depth + 1.0)
    return Feature(name=name, cut=cut, info=info)
