# 电源选型表

价格说明：立创/LCSC/JLCPCB 商品页本会话无法直接打开，价格来自 WebSearch 返回的商品页摘要快照（时间不明、快照间有出入），全部标"待核实"。5.1 kΩ 电阻、MOS 管等的价格本次未查。

| 场景 | 推荐器件 | 价格区间（美元/个） | 取舍 | 来源 |
|---|---|---|---|---|
| USB-C 受电口（只取 5 V，不做 PD） | 16 脚 Type-C 母座，例：TYPE-C-31-M-12（LCSC C165948）+ CC1、CC2 各一个 5.1 kΩ 下拉 | 母座约 0.19（5+）/ 0.09（5000+）；其他品牌 16 脚母座摘要最低 0.03 起 | 最简单；不读 CC 电压就只能按 USB 默认电流（USB 2.0 为 500 mA）设计 | [LCSC C165948](https://www.lcsc.com/product-detail/C165948.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 单节锂电充电，便宜、外围少 | TP4056（拓微原厂 TP4056-42-ESOP8，LCSC C16581） | 约 0.19（5+）/ 0.15（50+）/ 0.089（4000+） | 1 A 可调、两个状态脚；线性充电发热大、无电源路径、无保护 | [LCSC C16581](https://www.lcsc.com/product-detail/C16581.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
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

典型单节锂电产品的电源链：USB-C（5.1 kΩ×2）→ TP4056 → 电芯（DW01 + 双 MOS 保护）→ LDO → 3.3 V。

器件页：[usb-c-sink.md](usb-c-sink.md)、[tp4056.md](tp4056.md)、[dw01-protection.md](dw01-protection.md)、[me6211.md](me6211.md)、[xc6206.md](xc6206.md)。
