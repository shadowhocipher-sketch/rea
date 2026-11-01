"""USB-C 开孔：按插座外形和插头外壳（overmold）避让尺寸计算开孔大小。

局部坐标（见 :mod:`hwcad.frames`）：z = 0 为外表面，-Z 往壳内；开孔中心在原点，
局部 X = 插座宽度方向，局部 Y = 插座高度方向。

规则（"插座端面离外表面的距离"决定开孔大小）
-------------------------------------------
``recess`` = 插座前端面到外壳外表面的距离（正数 = 插座端面缩在外表面以内）。

* ``recess > 0``：插头插到底时，插头外壳（overmold）的前端要伸进壳壁 ``recess`` 那么深，
  所以开孔必须让开插头外壳：开孔 = overmold 外形 + 2 × 间隙。
* ``recess <= 0``：插座端面与外表面平齐或伸出，插头外壳不进壁，开孔只需让开插座金属壳：
  开孔 = 插座外形 + 2 × 间隙。

开孔形状为跑道形（两端半圆）。函数同时给出两个检查用包络体：插座外壳和插到底时的插头外壳；
它们与外壳零件的干涉体积为 0，就说明插头能插到底。

默认尺寸（详见 cad/DFM.md 的 USB-C 小节）：

* 插头金属壳 8.25 × 2.40 mm：CJT CJ-CM026 图纸（DFM:USB-1，单一厂家图纸，待核实）。
* 插座外形 8.94 × 3.26 mm、长 7.35 mm：**估算**（常见中板 / 沉板插座外形，未查到 USB-IF 原文），
  请换成所用插座数据手册的值。
* 插头外壳 12.4 × 6.5 × 长 20 mm：**估算**（不同线材差别很大，用游标卡尺量自己的线）。
"""
from __future__ import annotations

from build123d import Align, Location, Part, Plane, SlotOverall, extrude

from .frames import Feature

DEFAULT_RECEPTACLE = (8.94, 3.26, 7.35)   # 估算，见模块说明
DEFAULT_PLUG_SHELL = (8.25, 2.40)         # DFM:USB-1（待核实）
DEFAULT_OVERMOLD = (12.4, 6.5, 20.0)      # 估算，见模块说明


def _stadium(w: float, h: float, z_top: float, depth: float) -> Part:
    """局部坐标里从 z_top 往 -Z 延伸 depth 的跑道形柱体（宽 w 沿 X，高 h 沿 Y）。"""
    if w < h:
        w = h + 1e-3
    return extrude(Plane.XY.offset(z_top - depth) * SlotOverall(w, h), amount=depth)


def usbc_opening_size(
    recess: float,
    receptacle: tuple[float, float] = DEFAULT_RECEPTACLE[:2],
    overmold: tuple[float, float] = DEFAULT_OVERMOLD[:2],
    clearance: float = 0.3,
) -> tuple[float, float, str]:
    """按规则计算开孔宽、高（mm）和采用的规则说明。"""
    if recess > 0:
        return overmold[0] + 2 * clearance, overmold[1] + 2 * clearance, "recess>0：让开插头外壳 overmold"
    return receptacle[0] + 2 * clearance, receptacle[1] + 2 * clearance, "recess<=0：让开插座金属壳"


def usbc_cutout(
    wall: float,
    recess: float = 0.5,
    receptacle_w: float = DEFAULT_RECEPTACLE[0],
    receptacle_h: float = DEFAULT_RECEPTACLE[1],
    receptacle_len: float = DEFAULT_RECEPTACLE[2],
    overmold_w: float = DEFAULT_OVERMOLD[0],
    overmold_h: float = DEFAULT_OVERMOLD[1],
    overmold_len: float = DEFAULT_OVERMOLD[2],
    clearance: float = 0.3,
    mate_gap: float = 0.0,
    name: str = "usb_c",
) -> Feature:
    """USB-C 开孔特征。

    Args:
        wall: 壁厚，mm。
        recess: 插座前端面到外表面的距离，mm（正 = 缩进；负 = 伸出）。
        receptacle_w, receptacle_h, receptacle_len: 插座金属壳外形与长度，mm。
        overmold_w, overmold_h, overmold_len: 插头外壳外形与长度，mm。
        clearance: 开孔单边间隙，mm（默认 0.3 = FDM fit_clearance）。
        mate_gap: 插到底时插头外壳前端与插座端面之间的间隙，mm（默认 0，偏保守）。
        name: 特征名。

    Returns:
        Feature：cut = 跑道形开孔；envelopes = {"<name>_receptacle", "<name>_plug_overmold"}
        （局部坐标，由 enclosure 摆放）；info 含开孔尺寸、规则、插头伸进壁的深度。
    """
    ow, oh, rule = usbc_opening_size(recess, (receptacle_w, receptacle_h), (overmold_w, overmold_h), clearance)
    cut_depth = wall + 2.0
    cut = _stadium(ow, oh, 1.0, cut_depth)
    # 插座外壳：前端面在 z = -recess，往壳内延伸 receptacle_len
    receptacle = _stadium(receptacle_w, receptacle_h, -recess, receptacle_len)
    # 插头外壳：插到底时前端在 z = -recess + mate_gap，往外延伸 overmold_len
    front = -recess + mate_gap
    plug = _stadium(overmold_w, overmold_h, front + overmold_len, overmold_len)
    info = {
        "recess": recess,
        "opening": [round(ow, 3), round(oh, 3)],
        "rule": rule,
        "overmold_enters_wall_by": round(max(recess - mate_gap, 0.0), 3),
        "defaults_note": "插座 / 插头外壳默认尺寸为估算或待核实，见 hwcad/usbc.py 与 DFM.md",
        "warnings": [],
    }
    if recess > wall + 3.0:
        info["warnings"].append("插座缩进过深，插头可能无法插到底（插头金属部分长度不够），请核对插头规格")
    f = Feature(name=name, cut=cut, info=info)
    f.envelopes = {f"{name}_receptacle": receptacle, f"{name}_plug_overmold": plug}
    return f
