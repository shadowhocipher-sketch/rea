# 电源选型表

价格说明：立创/LCSC/JLCPCB 商品页本会话无法直接打开，价格来自 WebSearch 返回的商品页摘要快照（时间不明、快照间有出入），全部标"待核实"。5.1 kΩ 电阻、MOS 管等的价格本次未查。

| 场景 | 推荐器件 | 价格区间（美元/个） | 取舍 | 来源 |
|---|---|---|---|---|
| USB-C 受电口（只取 5 V，不做 PD） | 16 脚 Type-C 母座，例：TYPE-C-31-M-12（LCSC C165948）+ CC1、CC2 各一个 5.1 kΩ 下拉 | 母座约 0.19（5+）/ 0.09（5000+）；其他品牌 16 脚母座摘要最低 0.03 起 | 最简单；不读 CC 电压就只能按 USB 默认电流（USB 2.0 为 500 mA）设计 | [LCSC C165948](https://www.lcsc.com/product-detail/C165948.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 单节锂电充电，便宜、外围少 | TP4056（拓微原厂 TP4056-42-ESOP8，LCSC C16581） | 约 0.19（5+）/ 0.15（50+）/ 0.089（4000+） | 1 A 可调、两个状态脚；线性充电发热大、无电源路径、无保护 | [LCSC C16581](https://www.lcsc.com/product-detail/C16581.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 单节锂电充电，体积小、电流 ≤ 500 mA | MCP73831T-2ACI/OT（Microchip，SOT-23-5，4.2 V，LCSC C424093） | 两个快照：约 0.73（1+）/ 0.374（1000+）；约 0.81（1+）/ 0.435（1000+） | 比 TP4056 小、PROG 悬空即停充、STAT 三态；最大 500 mA，后缀决定浮充电压和终止电流；同样无保护、无电源路径 | [LCSC C424093](https://www.lcsc.com/product-image/C424093.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 屏幕上显示电量百分比（单节锂电） | MAX17048G+T10（Maxim/ADI 电量计，TDFN-8 2×2 mm，LCSC C2682616） | LCSC 摘要起价约 1.35；JLCPCB 摘要约 2.48（1+）/ 1.36（1000+） | 只测电压、无检流电阻、I2C、休眠 3 μA；默认模型对部分电池不准，要精确需定制模型；需要 MCU 定期做温度补偿 | [LCSC C2682616](https://lcsc.com/product-detail/image/MAX17048G-T10_C2682616.html)；[JLCPCB C2682616](https://jlcpcb.com/partdetail/2777647-MAX17048GT10/C2682616) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 裸电芯需要保护 | DW01A 类保护 IC + 双 N-MOS（FS8205A 类） | DW01A 各品牌约 0.011–0.025（大批量到 20 片档） | 防过充/过放/过流/短路；阈值随品牌不同；买带保护板的成品电池可省 | [LCSC DW01A（C351410 等）](https://www.lcsc.com/product-detail/C351410.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 3.3 V 主电源，带 Wi-Fi 的 ESP32 | ME6211C33M5G-N（LCSC C82942） | 约 0.05–0.06（10+）/ 0.03–0.036（9000+），两个快照 | 500 mA 够 ESP32 要求、带 CE；静态 60 μA，深睡产品偏耗电 | [LCSC C82942](https://www.lcsc.com/product-detail/Low-Dropout-Regulators-LDO_ME6211C33M5G-N_C82942.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 深睡为主、负载 ≤ 200 mA 的 3.3 V（传感器、墨水屏、无 Wi-Fi） | XC6206P332MR（Torex 原厂 LCSC C5446；兼容品牌 C347376 等） | 原厂约 0.14（5+）/ 0.088（6000+）；兼容品牌大批量约 0.007–0.04 | 静态 1 μA；只有约 200 mA、压差 250 mV@100 mA、无使能脚 | [LCSC C5446](https://www.lcsc.com/product-detail/Low-Dropout-Regulators-LDO_XC6206P332MR_C5446.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 深睡为主 **且** 要 Wi-Fi 峰值 500 mA | 需要"低静态电流 + ≥500 mA"的 LDO（如任务书提到的 RT9080 类） | 未查到 | 本次没有读到可核对的 RT9080 / AP2112 数据手册，不推荐具体型号；按研究方法补齐后再写 | https://www.richtek.com/ · 未查到（官网不可达，GitHub 上未找到镜像） |

## 依据（参数对比，均出自各器件页）

| 对比项 | ME6211C33 | XC6206（3.3 V） | 来源 |
|---|---|---|---|
| 静态电流 | 典型 60 μA | 典型 1.0 μA | [ME6211 V14](https://github.com/STM32-base/STM32-base.github.io/blob/9f6b21f4e951d431c98ed292a4ceef740f7e4df3/assets/pdf/regulators/ME6211.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 最大输出电流 | 500 mA | ≥ 200 mA | [XC6206 ETR0305_008](https://github.com/STM32-base/STM32-base.github.io/blob/9f6b21f4e951d431c98ed292a4ceef740f7e4df3/assets/pdf/regulators/XC6206.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 100 mA 压差（典型） | 120 mV | 250 mV | [XC6206 ETR0305_008](https://github.com/STM32-base/STM32-base.github.io/blob/9f6b21f4e951d431c98ed292a4ceef740f7e4df3/assets/pdf/regulators/XC6206.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 使能脚 | 有（C 版本） | 无 | [ME6211 V14](https://github.com/STM32-base/STM32-base.github.io/blob/9f6b21f4e951d431c98ed292a4ceef740f7e4df3/assets/pdf/regulators/ME6211.pdf) · S（镜像）· 2026-11-01 · 待核实 |

| 对比项 | TP4056 | MCP73831 | 来源 |
|---|---|---|---|
| 最大充电电流 | 1000 mA（RPROG = 1.2 kΩ） | 约 500 mA（RPROG = 2 kΩ） | [TP4056.pdf 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/TP4056.pdf)；[MCP73831/2 DS20001984G](https://github.com/RewokN/project_N_simple_BMS/blob/8ed279128e0d378290b7396e87fc8a116b9ac17e/Documents/MCP738312.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 封装 | SOP-8（带散热片） | SOT-23-5 / DFN-8 2×3 mm | [TP4056.pdf](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/TP4056.pdf)；[MCP73831/2 DS20001984G](https://github.com/RewokN/project_N_simple_BMS/blob/8ed279128e0d378290b7396e87fc8a116b9ac17e/Documents/MCP738312.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 浮充电压 | 4.2 V | 4.20/4.35/4.40/4.50 V（按后缀） | [MCP73831/2 DS20001984G DC Characteristics](https://github.com/RewokN/project_N_simple_BMS/blob/8ed279128e0d378290b7396e87fc8a116b9ac17e/Documents/MCP738312.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 状态输出 | 两个开漏脚（充电中 / 充满） | 一个 STAT 脚，三态（MCP73832 为开漏） | [MCP73831/2 DS20001984G Table 5-1](https://github.com/RewokN/project_N_simple_BMS/blob/8ed279128e0d378290b7396e87fc8a116b9ac17e/Documents/MCP738312.pdf) · S（镜像）· 2026-11-01 · 待核实 |

典型单节锂电产品的电源链：USB-C（5.1 kΩ×2）→ TP4056 或 MCP73831 → 电芯（DW01 + 双 MOS 保护）→ LDO → 3.3 V；要显示电量百分比时在电芯两端并一颗 MAX17048（I2C 接 MCU）。

器件页：[usb-c-sink.md](usb-c-sink.md)、[tp4056.md](tp4056.md)、[mcp73831.md](mcp73831.md)、[max17048.md](max17048.md)、[dw01-protection.md](dw01-protection.md)、[me6211.md](me6211.md)、[xc6206.md](xc6206.md)。
