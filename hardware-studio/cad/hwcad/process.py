"""按工艺分组的公差 / 壁厚常量。

所有长度单位 mm，角度单位度（°）。每个数值都带 ``source`` 键，指向 ``cad/DFM.md``
里的规则编号（例如 ``"DFM:FDM-1"``）；DFM.md 里有链接、来源级别和查询日期。
标了 ``估算`` / ``待核实`` 的数值同样在 DFM.md 里写了依据。

这里只放"工艺"常量，不放任何产品尺寸。

用法::

    from hwcad.process import get_process
    p = get_process("fdm")
    p.min_wall          # 1.2
    p.fit_clearance     # 0.3  （装配配合，单边）
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProcessRules:
    """一种工艺的设计规则。

    Attributes (全部 mm，角度为 °):
        key: 工艺代号（fdm / sla / mjf / im）。
        name: 中文名。
        min_wall: 最小壁厚，低于它制造商不保证成形或会报风险。
        min_feature_wall: 卡扣、定位、紧固件等受力小特征的最小厚度。
        default_wall: 外壳主体推荐壁厚（库内默认值）。
        fit_clearance: 两个分别制造、再装配的零件之间的单边配合间隙（止口、按键帽等）。
        moving_clearance: 需要相对运动的零件之间的最小间隙。
        tolerance_100mm: 100 mm 以内的典型尺寸公差（±）。
        min_hole: 最小可成形孔径。
        max_overhang_deg: 不加支撑的最大悬垂角（相对竖直方向），None 表示不适用。
        min_draft_deg: 最小脱模斜度，None 表示不适用。
        rib_to_wall_max: 筋厚 / 相邻壁厚 的上限，None 表示不适用。
        sources: 字段名 -> DFM.md 规则编号 / 状态说明。
    """

    key: str
    name: str
    min_wall: float
    min_feature_wall: float
    default_wall: float
    fit_clearance: float
    moving_clearance: float
    tolerance_100mm: float
    min_hole: float
    max_overhang_deg: float | None = None
    min_draft_deg: float | None = None
    rib_to_wall_max: float | None = None
    sources: dict = field(default_factory=dict)


PROCESSES: dict[str, ProcessRules] = {
    "fdm": ProcessRules(
        key="fdm",
        name="FDM 熔融沉积",
        min_wall=1.2,
        min_feature_wall=1.5,
        default_wall=2.0,
        fit_clearance=0.3,
        moving_clearance=0.5,
        tolerance_100mm=0.3,
        min_hole=2.0,
        max_overhang_deg=45.0,
        sources={
            "min_wall": "DFM:FDM-1 (JLC3DP 1.2 mm)",
            "min_feature_wall": "DFM:GEN-1 (JLC3DP 卡扣/紧固件 >1.5 mm)",
            "default_wall": "估算：min_feature_wall + 0.5 mm 余量，见 DFM:FDM-1 下的说明",
            "fit_clearance": "估算：取 JLC3DP 典型公差 ±0.3 mm（DFM:FDM-3）作单边间隙",
            "moving_clearance": "DFM:FDM-4 (Xometry 0.5 mm)",
            "tolerance_100mm": "DFM:FDM-3 (JLC3DP ±0.3 mm/100 mm)",
            "min_hole": "估算：未查到 FDM 最小孔径官方值，见 DFM:FDM-5",
            "max_overhang_deg": "DFM:FDM-2 (Xometry 45°)",
        },
    ),
    "sla": ProcessRules(
        key="sla",
        name="光固化 SLA/DLP",
        min_wall=0.8,
        min_feature_wall=1.5,
        default_wall=1.5,
        fit_clearance=0.2,
        moving_clearance=0.4,
        tolerance_100mm=0.2,
        min_hole=0.5,
        max_overhang_deg=None,
        sources={
            "min_wall": "DFM:SLA-1 (JLC3DP 0.8 mm)",
            "min_feature_wall": "DFM:GEN-1",
            "default_wall": "估算：= min_feature_wall",
            "fit_clearance": "估算：取 JLC3DP SLA 典型公差 ±0.2 mm（DFM:SLA-3）作单边间隙",
            "moving_clearance": "DFM:SLA-2 (Formlabs Form 4 0.4 mm)",
            "tolerance_100mm": "DFM:SLA-3 (JLC3DP ±0.2 mm/100 mm)",
            "min_hole": "DFM:SLA-4 (Formlabs Form 4 0.5 mm)",
        },
    ),
    "mjf": ProcessRules(
        key="mjf",
        name="MJF 多射流熔融（尼龙粉末）",
        min_wall=1.0,
        min_feature_wall=1.5,
        default_wall=1.5,
        fit_clearance=0.3,
        moving_clearance=0.7,
        tolerance_100mm=0.3,
        min_hole=1.0,
        max_overhang_deg=None,
        sources={
            "min_wall": "DFM:MJF-1 (JLC3DP 1.0 mm)",
            "min_feature_wall": "DFM:GEN-1",
            "default_wall": "DFM:MJF-1（Xometry 转述 HP：推荐 1.5 mm，待核实）",
            "fit_clearance": "估算：取 JLC3DP MJF 典型公差 ±0.3 mm（DFM:MJF-3）作单边间隙",
            "moving_clearance": "DFM:MJF-2（Xometry 转述 HP 0.5–0.7 mm，取 0.7，待核实）",
            "tolerance_100mm": "DFM:MJF-3 (JLC3DP ±0.3 mm/100 mm)",
            "min_hole": "DFM:MJF-4（Creabis 最小 1 mm，待核实）",
        },
    ),
    "im": ProcessRules(
        key="im",
        name="注塑",
        min_wall=1.14,
        min_feature_wall=1.14,
        default_wall=2.0,
        fit_clearance=0.1,
        moving_clearance=0.3,
        tolerance_100mm=0.1,
        min_hole=1.0,
        max_overhang_deg=None,
        min_draft_deg=0.5,
        rib_to_wall_max=0.6,
        sources={
            "min_wall": "DFM:IM-1 (Protolabs ABS 1.14–3.56 mm 下限)",
            "min_feature_wall": "DFM:IM-1",
            "default_wall": "估算：DFM:IM-1 ABS 范围中段",
            "fit_clearance": "估算：未查到官方值，按模具公差远小于打印取 0.1 mm，见 DFM:IM-7",
            "moving_clearance": "估算：未查到官方值，见 DFM:IM-7",
            "tolerance_100mm": "估算：未查到官方值，见 DFM:IM-7",
            "min_hole": "估算：未查到官方值，见 DFM:IM-7",
            "min_draft_deg": "DFM:IM-2（0.5° 来自第三方，待核实；Protolabs 轻纹理 3°）",
            "rib_to_wall_max": "DFM:IM-3 (Protolabs ≤60%)",
        },
    ),
}


def get_process(key: str) -> ProcessRules:
    """按代号取工艺规则；代号不区分大小写，可用 fdm / sla / dlp / mjf / im / injection。"""
    k = key.strip().lower()
    alias = {"dlp": "sla", "injection": "im", "injection_molding": "im", "sls": "mjf"}
    k = alias.get(k, k)
    if k not in PROCESSES:
        raise KeyError(f"未知工艺 {key!r}，可选：{sorted(PROCESSES)}")
    return PROCESSES[k]


# 打印平台尺寸（X, Y, Z，mm）。用于"能否放上平台"检查；数值都待核实（只查到零售商/第三方页面）。
PRINTER_BEDS: dict[str, dict] = {
    "prusa_mk4s": {"bed": (250.0, 210.0, 220.0), "source": "DFM:BED-1（待核实）"},
    "bambu_a1_mini": {"bed": (180.0, 180.0, 180.0), "source": "DFM:BED-2（待核实）"},
    "bambu_p1s": {"bed": (256.0, 256.0, 256.0), "source": "DFM:BED-2（待核实）"},
}


# 螺丝相关。自攻螺丝孔/柱比例来自 EJOT PT 系列（注塑热塑性塑料），见 DFM:FAST-1。
SELF_TAP_HOLE_FACTOR = 0.8   # 底孔 = 0.8 × 螺纹公称直径（EJOT PT / DELTA PT）
SELF_TAP_BOSS_FACTOR = 2.0   # 柱外径 = 2.0 × 螺纹公称直径（EJOT PT / DELTA PT）

# 热熔螺母（铜嵌件）。只有查到来源的规格才放默认值，其他规格必须在参数里给出（见 DFM:FAST-2）。
HEAT_INSERT_TABLE: dict[str, dict] = {
    "M3": {"hole_d": 4.0, "length": 5.8, "min_wall": 1.8,
            "source": "DFM:FAST-2（Accu HTBI-M3-BR 商品页，B 级）"},
}

# 通孔（螺丝过孔）默认 = 公称直径 + 0.4 mm。ISO 273 原表未能打开，见 DFM:FAST-3（待核实）。
CLEARANCE_HOLE_EXTRA = 0.4
