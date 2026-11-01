"""按键：圆孔 + 可选导向筒 + 按键帽零件；一体式悬臂按键。

局部坐标（见 :mod:`hwcad.frames`）：z = 0 为外表面，-Z 往壳内；按键中心在原点。
"""
from __future__ import annotations

from build123d import Align, Box, Cylinder, Location, Part

from .frames import Feature

_TOP = (Align.CENTER, Align.CENTER, Align.MAX)


def cantilever_strain(length: float, thickness: float, deflection: float, q: float = 1.0) -> float:
    """等截面矩形悬臂梁根部应变估算 ε = 1.5·t·y / (L²·Q)。

    与 Bayer/Covestro 卡扣手册的 y = 0.67·ε·L²/t 是同一公式（Q = 1）；
    BASF 卡扣手册引入放大系数 Q 修正根部应变（DFM:SNAP-1、SNAP-2）。

    Args:
        length: 悬臂长度 L，mm。
        thickness: 梁厚 t（弯曲方向），mm。
        deflection: 挠度 y，mm。
        q: 挠度放大系数 Q（默认 1，即经典梁公式）。

    Returns:
        应变（无量纲，0.01 = 1%）。
    """
    if length <= 0 or thickness <= 0:
        raise ValueError("length / thickness 必须为正")
    return 1.5 * thickness * deflection / (length ** 2 * q)


def button_hole(
    wall: float,
    diameter: float = 6.0,
    clearance: float = 0.3,
    sleeve_length: float = 0.0,
    sleeve_wall: float = 1.2,
    name: str = "button",
) -> Feature:
    """圆形按键孔，可选内侧导向筒。

    Args:
        wall: 壁厚，mm。
        diameter: 按键帽（柱）直径，mm（默认 6）。
        clearance: 帽与孔的单边间隙，mm（默认 0.3 = FDM fit_clearance）。
        sleeve_length: 导向筒从内表面往里伸出的长度，mm（0 = 不做）。
        sleeve_wall: 导向筒壁厚，mm（默认 1.2 = FDM 最小壁厚）。
        name: 特征名。

    Returns:
        Feature：cut = 孔（贯穿壁和导向筒），add = 导向筒（可为 None）。
    """
    bore = diameter + 2 * clearance
    cut = Cylinder(bore / 2, wall + sleeve_length + 2.0, align=_TOP).moved(Location((0, 0, 1.0)))
    add = None
    if sleeve_length > 0:
        add = Cylinder(bore / 2 + sleeve_wall, sleeve_length + 0.2, align=_TOP).moved(Location((0, 0, -wall + 0.2)))
    info = {"bore_d": round(bore, 3), "cap_d": diameter, "sleeve_length": sleeve_length, "wall": wall}
    return Feature(name=name, cut=cut, add=add, info=info)


def button_cap(
    wall: float,
    diameter: float = 6.0,
    protrusion: float = 1.0,
    sleeve_length: float = 0.0,
    flange_d: float | None = None,
    flange_t: float = 1.0,
    gap: float = 0.3,
    plunger_length: float = 1.0,
) -> Part:
    """与 :func:`button_hole` 配套的按键帽（独立零件，局部坐标，装配位置）。

    帽身从外表面凸出 ``protrusion``，穿过壁（和导向筒），在导向筒末端以内 ``gap`` 处有一圈法兰
    防止掉出，法兰下面再伸出 ``plunger_length`` 的压杆去按 PCB 上的轻触开关。

    Args:
        wall: 壁厚，mm。
        diameter: 帽身直径，mm。
        protrusion: 露出外表面的高度，mm。
        sleeve_length: 导向筒长度，mm（与孔一致）。
        flange_d: 法兰直径，mm；默认 diameter + 2.0（估算）。
        flange_t: 法兰厚，mm。
        gap: 法兰与壁 / 导向筒末端的间隙，mm。
        plunger_length: 压杆长度，mm。
    """
    fd = diameter + 2.0 if flange_d is None else flange_d
    stem_len = protrusion + wall + sleeve_length + gap
    cap = Cylinder(diameter / 2, stem_len, align=_TOP).moved(Location((0, 0, protrusion)))
    z_flange_top = -(wall + sleeve_length + gap)
    cap = cap + Cylinder(fd / 2, flange_t, align=_TOP).moved(Location((0, 0, z_flange_top)))
    if plunger_length > 0:
        cap = cap + Cylinder(min(diameter, fd) / 2 * 0.6, plunger_length, align=_TOP).moved(
            Location((0, 0, z_flange_top - flange_t))
        )
    return cap


def cantilever_button(
    wall: float,
    length: float = 12.0,
    width: float = 7.0,
    slot: float = 0.8,
    tongue_thickness: float | None = None,
    nub_d: float = 3.0,
    nub_height: float = 1.5,
    travel: float = 0.5,
    allowable_strain: float | None = None,
    name: str = "cantilever_button",
) -> Feature:
    """一体式悬臂按键：在壁上切 U 形槽，留下一条舌片，舌片内侧末端有凸点去按开关。

    舌片根部在局部 -X 端（u 负方向），自由端在 +X 端；舌片宽度沿局部 Y。

    Args:
        wall: 壁厚，mm。
        length: 舌片长度（根部到自由端），mm。
        width: 舌片宽度，mm。
        slot: U 形槽宽，mm（≥ 工艺最小间隙，FDM 建议 ≥ 0.5）。
        tongue_thickness: 舌片厚度，mm；None = 等于壁厚；小于壁厚时从内侧减薄。
        nub_d: 凸点直径，mm。
        nub_height: 凸点高度（从舌片内表面往里），mm。
        travel: 设计按压行程，mm（用于应变估算）。
        allowable_strain: 材料许用应变（0.02 = 2%）；给出时超过会写警告。
        name: 特征名。

    Returns:
        Feature：cut = U 形槽 + 减薄区；add = 凸点；info 含根部应变估算。
    """
    t = wall if tongue_thickness is None else tongue_thickness
    if t > wall:
        raise ValueError("tongue_thickness 不能大于壁厚")
    depth = wall + 2.0
    x0 = -length / 2  # 根部
    outer = Box(length + slot, width + 2 * slot, depth, align=(Align.MIN, Align.CENTER, Align.MAX)).moved(
        Location((x0, 0, 1.0))
    )
    tongue = Box(length, width, depth + 1, align=(Align.MIN, Align.CENTER, Align.MAX)).moved(Location((x0, 0, 1.5)))
    cut = outer - tongue
    if t < wall:
        thin = Box(length, width, wall - t + 1.0, align=(Align.MIN, Align.CENTER, Align.MAX)).moved(
            Location((x0, 0, -t))
        )
        cut = cut + thin
    nub_x = length / 2 - nub_d / 2 - 0.5
    add = Cylinder(nub_d / 2, nub_height + 0.1, align=_TOP).moved(Location((nub_x, 0, -t + 0.1)))
    cut = cut - add  # 先加后减时，减薄区不能把凸点切掉
    strain = cantilever_strain(length, t, travel)
    info = {
        "tongue": [length, width, t],
        "slot": slot,
        "travel": travel,
        "root_strain_est": round(strain, 5),
        "strain_formula": "ε = 1.5·t·y/L²（DFM:SNAP-1，估算，未计入 3D 打印层间强度下降）",
        "warnings": [],
    }
    if allowable_strain is not None and strain > allowable_strain:
        info["warnings"].append(f"根部应变估算 {strain:.2%} > 许用 {allowable_strain:.2%}，加长舌片或减薄")
    return Feature(name=name, cut=cut, add=add, info=info)
