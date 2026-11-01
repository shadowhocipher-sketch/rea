"""电池仓：软包 / 方形锂电池的定位围框 + 膨胀余量 + 走线口。

局部坐标：原点在电池仓中心、**下壳底板内表面**上（全局 z = wall）；+Z 朝上。
电池长 ``cell_length`` 沿局部 X，宽 ``cell_width`` 沿局部 Y，厚 ``cell_thickness`` 沿 Z。

参数来源（详见 cad/DFM.md 的电池小节 DFM:BAT-*）
-----------------------------------------------
* 膨胀余量 ``swell``：没有统一标准，各电芯厂自定（DFM:BAT-1）。电池包厂商 Epec 的页面写
  "部分软包电芯寿命期内可能膨胀 10% 或更多"（C 级，待核实）。默认 0.10（厚度方向 +10%）是
  **估算**，应以所用电芯规格书的循环寿命末期厚度为准。
* 平面方向间隙 ``xy_clearance`` 默认 0.5 mm：**估算**（FDM 单边公差 0.3 mm + 软包封边尺寸波动）。
* 设计要点（DFM:BAT-1）：膨胀要有空间、避免点压力（不要让螺丝柱、元件脚顶在电池表面）。
"""
from __future__ import annotations

from build123d import Align, Box, Location, Part

from .frames import Feature

_SIDES = ("+x", "-x", "+y", "-y")


def swollen_thickness(cell_thickness: float, swell: float = 0.10) -> float:
    """膨胀后厚度 = 厚度 × (1 + swell)，mm。"""
    return cell_thickness * (1.0 + swell)


def battery_bay(
    cell_length: float,
    cell_width: float,
    cell_thickness: float,
    swell: float = 0.10,
    xy_clearance: float = 0.5,
    rib_thickness: float = 1.2,
    rib_height: float = 3.0,
    wire_side: str = "+x",
    wire_slot_width: float = 4.0,
    top_gap: float = 0.3,
    name: str = "battery",
) -> Feature:
    """电池仓特征（局部坐标，摆放时原点对到底板内表面上的电池中心）。

    Args:
        cell_length, cell_width, cell_thickness: 电芯标称尺寸（含封边 / 极耳折弯区），mm。
        swell: 厚度方向膨胀余量比例（默认 0.10，估算，见模块说明）。
        xy_clearance: 平面方向单边间隙，mm（默认 0.5，估算）。
        rib_thickness: 围框筋厚，mm（默认 1.2 = FDM 最小壁厚）。
        rib_height: 围框高度，mm（不超过膨胀后厚度）。
        wire_side: 走线口在哪一边：``+x`` / ``-x`` / ``+y`` / ``-y``。
        wire_slot_width: 走线口宽度，mm。
        top_gap: 膨胀后电池顶面到上方零件的最小间隙，mm（估算）。
        name: 特征名。

    Returns:
        Feature：add = 围框（plane=None 时为局部坐标，enclosure 负责平移）；
        envelopes = {"<name>_cell_swollen": 膨胀后电池包络（含 top_gap）}；
        info = 各尺寸与 ``required_height``（底板内表面以上需要的净高）。
    """
    if wire_side not in _SIDES:
        raise ValueError(f"wire_side 必须是 {_SIDES} 之一")
    t_sw = swollen_thickness(cell_thickness, swell)
    rh = min(rib_height, t_sw)
    il = cell_length + 2 * xy_clearance
    iw = cell_width + 2 * xy_clearance
    ol, ow = il + 2 * rib_thickness, iw + 2 * rib_thickness
    frame = Box(ol, ow, rh + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, -0.01))) - Box(
        il, iw, rh + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)
    ).moved(Location((0, 0, -1)))
    # 走线口：在指定边的围框上开槽
    if wire_side in ("+x", "-x"):
        sx = (il / 2 + rib_thickness / 2) * (1 if wire_side == "+x" else -1)
        slot = Box(rib_thickness + 2, wire_slot_width, rh + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((sx, 0, -1))
        )
    else:
        sy = (iw / 2 + rib_thickness / 2) * (1 if wire_side == "+y" else -1)
        slot = Box(wire_slot_width, rib_thickness + 2, rh + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((0, sy, -1))
        )
    frame = frame - slot
    cell = Box(cell_length, cell_width, t_sw + top_gap, align=(Align.CENTER, Align.CENTER, Align.MIN))
    info = {
        "cell": [cell_length, cell_width, cell_thickness],
        "swell": swell,
        "swollen_thickness": round(t_sw, 3),
        "required_height": round(t_sw + top_gap, 3),
        "pocket_inner": [round(il, 3), round(iw, 3)],
        "frame_outer": [round(ol, 3), round(ow, 3), round(rh, 3)],
        "wire_side": wire_side,
        "source": "swell / xy_clearance / top_gap 为估算，见 DFM:BAT-1",
    }
    f = Feature(name=name, add=frame, add_to="lower", cut_from=(), info=info)
    f.envelopes = {f"{name}_cell_swollen": cell}
    return f
