# USB Type-C 受电（Sink）：CC 下拉 5.1 kΩ

一句话：做 USB-C 供电/充电的小产品（Sink），要在 CC1、CC2 上**各接一个** 5.1 kΩ 下拉（Rd）到地，否则 C-to-C 充电器不会给 VBUS 上电；不做 PD 时最多按 Rp 广播拿到 5 V 1.5 A / 3 A。

> 规范来源说明：usb.org 本会话不可达。本页读自 GitHub 仓库 usb-c/USB-Type-C 托管的 **USB Type-C Cable and Connector Specification Release 2.1（May 2021）** PDF（版权 USB 3.0 Promoter Group），非官方托管，标"待核实"。2.1 之后的版本（如 R2.3）是否改动下列条款未核对。

## 关键参数

| 参数 | 值 | 来源 |
|---|---|---|
| Sink 端接 | Sink 用下拉电阻把 CC1 **和** CC2 都端接到地；Sink 在 CC1、CC2 上呈现**各自独立**的 Rd | [Type-C R2.1 §4.5.1.3.2、§4.5.1.2.1](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| Rd 实现方式 | 5.1 kΩ ±10% 接地：能识别电源电流能力，CC 最高 2.04 V；5.1 kΩ ±20% 接地：不能识别，最高 2.18 V；1.1 V ±20% 钳位：不能识别，最高 1.32 V | [Type-C R2.1 表 4-25](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 电流档（5 V） | Default（USB 2.0 为 500 mA；USB 3.2 单/双通道 900 / 1500 mA）、1.5 A、3.0 A | [Type-C R2.1 §4.6.2.1](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 供电优先级 | USB PD（最高，最大 5 A）> Type-C 3.0 A > Type-C 1.5 A > BC 1.2（最高 1.5 A）> 默认 USB 供电 | [Type-C R2.1 表 4-17](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 引脚要点

| 项目 | 要点 | 来源 |
|---|---|---|
| CC1 / CC2 | 每个 CC 一个 5.1 kΩ 到 GND，不要两个 CC 共用一个电阻 | [Type-C R2.1 §4.5.1.2.1](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| D+ / D- 接 ESP32 | S3：GPIO20 / GPIO19；C3：GPIO19 / GPIO18；C6：GPIO13 / GPIO12；靠芯片预留 22/33 Ω 串阻和对地电容位 | [HDG 原理图清单 USB](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| VBUS 入口 | ESP32 侧建议主电源入口加 ESD 二极管和 ≥10 μF 电容 | [HDG 原理图清单 Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |

## 电压、电流（Sink 检测 CC 电压判断可用电流）

| 检测 | 最小 | 最大 | 来源 |
|---|---|---|---|
| vRd-USB（默认电流） | 0.25 V | 0.61 V | [Type-C R2.1 表 4-36](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| vRd-1.5（1.5 A） | 0.70 V | 1.16 V | [Type-C R2.1 表 4-36](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| vRd-3.0（3.0 A） | 1.31 V | 2.04 V | [Type-C R2.1 表 4-36](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| CC 引脚钳位电压（可选保护） | ≥ 2.9 V | — | [Type-C R2.1 表 4-37](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 接口时序要点

| 项目 | 要点 | 来源 |
|---|---|---|
| 连接判定 | Source 看到 CC 上有 Rd 才认为接了 Sink 并打开 VBUS；Sink 以 VBUS 出现判断 Source 已接入，用 CC 判断方向 | [Type-C R2.1 §4.5.1.3.2](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 想用 >500 mA | 必须实现能识别电流的 Rd（±10%）并用 ADC/比较器读 CC 电压（见上表），或做 PD；只放两个电阻不读 CC 时应按默认 USB 电流设计 | [Type-C R2.1 表 4-25、§4.6.2.1](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| CC 不接电阻或两个 CC 共用一个电阻 | 规范要求 CC1、CC2 各自独立的 Rd；Source 要检测到 Rd 才开 VBUS（§4.5.1.2.1），不接则 C-to-C 充电器不出电；而 USB-C 转 Standard-A 线的 C 插头里自带 56 kΩ Rp（表 4-24 注 1），所以会出现"A-to-C 线能充、C-to-C 线不能充" | [Type-C R2.1 §4.5.1.2.1、表 4-24](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 用 5% 电阻就以为能读电流档 | 规范只区分 ±10%（可识别）和 ±20%（不可识别）；常用 1% / 5% 的 5.1 kΩ 都在 ±10% 内，但不读 CC 电压就仍然只能按默认电流 | [Type-C R2.1 表 4-25](https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 充电 + 系统峰值超过默认电流 | 例：充电 500 mA + ESP32 Wi-Fi 峰值（S3 Modem-sleep 测得最大 235.8 mA）会超过 USB 2.0 默认 500 mA；要么读 CC 档位，要么限制充电电流 | [ESP-IDF sleep-current/esp32s3_modem_sleep.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32s3_modem_sleep.inc) · A · 2026-11-01 |
| 16 脚母座当成全功能 | 16 脚（USB 2.0）母座够用作受电 + USB 2.0 数据；商品页标称 5 A/20 V 是连接器额定，不代表能拿到这些电流 | [LCSC C165948](https://www.lcsc.com/product-detail/C165948.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |

## 来源列表

- [TypeC] USB Type-C Cable and Connector Specification Release 2.1（USB 3.0 Promoter Group，May 2021）。第三方镜像：https://github.com/usb-c/USB-Type-C/blob/10c96fd182812054b5a2903f3af5574b775b1ff0/USB-C_Specification/Revision_2.1/USB%20Type-C%20Spec%20R2.1%20-%20May%202021.pdf （sha256 前缀 4963071ac21ee4c3）。官方文档库 https://www.usb.org/documents 本会话不可达。
- [HDG] ESP Hardware Design Guidelines，commit a727293：https://github.com/espressif/esp-hardware-design-guidelines
- [B] LCSC TYPE-C-31-M-12（搜索摘要）：https://www.lcsc.com/product-detail/C165948.html
- 查询日期：2026-11-01。
