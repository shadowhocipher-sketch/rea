# ESP32-S3 最小系统参考设计要点

画自己的 ESP32-S3 板子（芯片方案或"模组 + 底板"方案）时的检查要点。这里只摘要点，具体电路图以乐鑫原文的图为准。

## 来源和读法

- 主要来源：乐鑫《ESP32-S3 硬件设计指南》（ESP Hardware Design Guidelines），S 级。
  - 在线版（中文）：<https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/index.html>
  - 在线版（英文）：<https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/index.html>
- 本会话打不开 docs.espressif.com（代理拦截，`getaddrinfo ENOTFOUND`），所以改读同一文档的官方源码仓库
  [espressif/esp-hardware-design-guidelines](https://github.com/espressif/esp-hardware-design-guidelines)，
  提交 `a727293`（2026-10-26），文件 `docs/en/schematic-checklist.rst`、`docs/en/pcb-layout-design.rst`、
  `docs/en/download-guidelines.rst` 和 `docs/en/esp32s3/*.inc`，只取 `.. only:: esp32s3` 适用的段落。查询日期 2026-11-01。
- 下面的"章节"写的是在线版的章节名（中文版 / 英文版），链接指向在线版对应页面。
- 引用的管脚号（pin46、pin20 等）是**芯片**（QFN56）的管脚号，不是模组的管脚号。用模组时去看模组数据手册的管脚表。
- 状态：本文是资料摘要，**未运行**——没有据此画板、打样和实测。
- 许可：乐鑫该仓库的文档内容采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)（见其 README 的 "Open Source Licensing" 一节）。
  本页是对原文的摘要、翻译和重新组织（有改动），署名：Espressif Systems,《ESP Hardware Design Guidelines》；**本页按 CC BY-SA 4.0 发布**，
  不适用本库其他文件的许可。没有复制原文的图片。

## 1. 电源和去耦

| 要点 | 内容 | 来源 |
|---|---|---|
| 供电 | 单电源供电时推荐 3.3 V，输出电流不小于 500 mA | [原理图设计 › 电源 / Schematic Checklist › Power Supply](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-power-supply) · S · 2026-11-01 |
| 电源入口 | 外部电源进板处加 ESD 保护二极管和至少 10 µF 电容 | [原理图设计 › 电源 / Schematic Checklist › Power Supply](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-power-supply) · S · 2026-11-01 |
| 数字电源 | 芯片 pin46 VDD3P3_CPU 是数字电源，pin20 VDD3P3_RTC 是 RTC 及部分数字电源，工作电压 3.0–3.6 V；管脚旁加 0.1 µF 电容 | [原理图设计 › 电源 › 数字电源](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#digital-power-supply)（源文件 `shared/esp32-s-series-digital-power-supply.inc`）· S · 2026-11-01 |
| VDD_SPI | 给 flash/PSRAM 供电，1.8 V 或 3.3 V（默认）；管脚旁加 0.1 µF 和 1 µF，不要加过大的电容。3.3 V 模式下由 VDD3P3_RTC 经 14 Ω 电阻（R_SPI）供电，有压降，要保证 VDD3P3_RTC 高于 3.0 V | [原理图设计 › 电源 › 数字电源](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#digital-power-supply) · S · 2026-11-01 |
| VDD3P3_RTC 不能单独供电 | 所有电源必须同时上电 | [原理图设计 › 电源 › 数字电源](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#digital-power-supply) · S · 2026-11-01 |
| 模拟电源 | VDD3P3（pin2、pin3）和 VDDA（pin55、pin56）是模拟电源，3.0–3.6 V。发射时电流突增可能拉垮电源轨，强烈建议在 VDD3P3 电源轨上加 10 µF 电容，与 1 µF 配合；若主电源入口靠近 VDD3P3，两个 10 µF 可合并 | [原理图设计 › 电源 › 模拟电源](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-power-supply) · S · 2026-11-01 |
| 外围器件数 | 芯片方案除晶振外只需约 20 个阻容感器件 | [原理图设计 › 概述](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-overview) · S · 2026-11-01 |
| 版图 | 电源走线、去耦电容摆放见 PCB 版图布局 › 电源 | [PCB 版图布局 › 电源](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/pcb-layout-design.html) · S · 2026-11-01 |

## 2. EN（CHIP_PU）复位电路

| 要点 | 内容 | 来源 |
|---|---|---|
| 功能 | CHIP_PU 高电平使能芯片，低电平复位；**不能悬空** | [原理图设计 › 上电时序与复位 / Chip Power-up and Reset Timing](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html) · S · 2026-11-01 |
| 时序 | 3.3 V 电源稳定后再拉高 CHIP_PU：t_STBL ≥ 50 µs；复位时 CHIP_PU 保持低于 V_IL_nRST（−0.3 ~ 0.25 × VDD3P3_RTC V）的时间 t_RST ≥ 50 µs | [原理图设计 › 上电时序与复位 / Chip Power-up and Reset Timing](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html)，表"上电和复位时序参数" · S · 2026-11-01 |
| RC 延时 | 推荐 R = 10 kΩ、C = 1 µF，再按实际电源上电特性调整；CHIP_PU 走线尽量短，防止干扰引起重启 | [原理图设计 › 上电时序与复位 / Chip Power-up and Reset Timing](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html) · S · 2026-11-01 |
| 电池类产品 | 电源上升/下降慢（例如电池充电时）、频繁上下电、电源不稳时，单靠 RC 可能不满足时序，会导致芯片无法正常启动或 flash 擦写偶发失败；建议预留电压监控（复位）芯片，阈值约 3.0 V | [原理图设计 › 上电时序与复位 / Chip Power-up and Reset Timing](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html) · S · 2026-11-01 |

与本库的关系：用 TP4056 + DW01A 这类锂电池方案时，第 4 条适用，BOM 里应考虑加一颗电压监控芯片。

## 3. 下载/启动电路和 strapping 管脚

| 要点 | 内容 | 来源 |
|---|---|---|
| strapping 管脚 | GPIO0、GPIO3、GPIO45、GPIO46；复位后变成普通 IO | [原理图设计 › Strapping 管脚](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-strapping-pins) · S · 2026-11-01 |
| 启动模式 | GPIO0 和 GPIO46 决定启动模式。默认 GPIO0 上拉（1）、GPIO46 下拉（0）。GPIO0=1 → SPI Boot（正常运行）；GPIO0=0 且 GPIO46=0 → Joint Download Boot（支持 USB-Serial-JTAG、USB-OTG 和 UART 下载） | [原理图设计 › Strapping 管脚](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-strapping-pins)，表"启动模式控制"（源文件 `esp32s3/esp32s3-chip-boot-mode-control.inc`）· S · 2026-11-01 |
| GPIO0 | 建议加上拉电阻；**不要加大电容**，否则可能进入下载模式 | [原理图设计 › Strapping 管脚](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-strapping-pins) · S · 2026-11-01 |
| 时序 | 建立时间 t_SU ≥ 0 ms，保持时间 t_H ≥ 3 ms（CHIP_PU 拉高后芯片读取 strapping 的时间） | [原理图设计 › Strapping 管脚](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-strapping-pins)，表"Strapping 管脚时序参数" · S · 2026-11-01 |
| GPIO45 | 和 eFuse（EFUSE_VDD_SPI_FORCE / EFUSE_VDD_SPI_TIEH）一起决定 VDD_SPI 电压：FORCE=0 时 GPIO45=0 → 3.3 V，GPIO45=1 → 1.8 V。由此推出：用 3.3 V flash/PSRAM 且 eFuse 未强制时，GPIO45 不能被外部电路拉高（推论）。片内 flash/PSRAM 且已用 eFuse 固定 VDD_SPI 时，GPIO45 不再影响 VDD_SPI（`esp32s3-chip-core-schem-note.inc`） | [原理图设计 › 电源 › 数字电源](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#digital-power-supply)，表"VDD_SPI 电压控制" · S · 2026-11-01 |
| GPIO3 | JTAG 信号源选择：烧录 eFuse `STRAP_JTAG_SEL` 后，复位时 GPIO3 低 → JTAG 走 GPIO39–GPIO42，高 → 走内置 USB_SERIAL_JTAG；未烧该 eFuse（默认）时 GPIO3 不影响 JTAG。硬件设计指南只把它列为 strapping 管脚，本条取自 ESP-IDF JTAG 调试文档；数据手册"启动配置项"章节本会话打不开，ESP-IDF eFuse 表的字段说明写成 gpio10，与文档冲突，见 `knowledge/mcu/esp32-s3.md` | [ESP-IDF configure-other-jtag.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/jtag-debugging/configure-other-jtag.rst#L24)、[esp32s3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/jtag-debugging/esp32s3.inc#L132) · A · 2026-11-01 · 待核实 |
| 下载口 | 可以经 UART 或 USB 下载。建议保留对 strapping 管脚的控制（按键或测试点），并保留 UART 下载口——当前 RF 测试固件只支持 UART | [下载指导 / Download Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/download-guidelines.html) · S · 2026-11-01 |
| USB 自动下载失效的情况 | 应用里关掉了 USB PHY、把 USB 配成别的功能（主机或标准设备）、或把 USB 管脚改作其他外设时，USB 自动下载不可用，需要用 strapping 管脚进下载模式 | [下载指导 / Download Guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/download-guidelines.html) · S · 2026-11-01 |

## 4. 原生 USB

| 要点 | 内容 | 来源 |
|---|---|---|
| 管脚 | GPIO19 = USB D−，GPIO20 = USB D+；芯片带全速 USB OTG（USB 2.0）和 USB Serial/JTAG | [原理图设计 › USB](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-usb) · S · 2026-11-01 |
| 串阻和对地电容 | 在 D−/D+ 走线上靠近芯片预留串联电阻（初值 22/33 Ω）和对地电容（初始可不贴） | [原理图设计 › USB](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-usb) · S · 2026-11-01 |
| 上电状态 | 上电时 USB_D+ 会在高低之间跳动；需要稳定初始状态时建议加外部上拉 | [原理图设计 › USB](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-usb) · S · 2026-11-01 |
| USB-OTG 下载模式 | 启用时 ROM 会初始化外部 PHY 相关 IO（MTMS、MTDI、GPIO21、MTDO、MTCK、GPIO38）的状态；不需要这个模式时，烧 eFuse EFUSE_DIS_USB_OTG_DOWNLOAD_MODE 关掉，避免这些 IO 状态被改 | [原理图设计 › USB](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-usb)（源文件 `esp32s3/esp32s3-usb.inc`）· S · 2026-11-01 |
| 版图 | USB 走线规则见 PCB 版图布局 › USB | [PCB 版图布局](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/pcb-layout-design.html) · S · 2026-11-01 |

USB-C 受电还需要 CC1/CC2 各接 5.1 kΩ 下拉，这条来自 USB Type-C 规范，不在乐鑫指南里，见 `knowledge/`（A 线）的 USB-C 页面。

## 5. 晶振（芯片方案）

| 要点 | 内容 | 来源 |
|---|---|---|
| 频率 | 固件只支持 40 MHz 晶振，精度 ±10 ppm 以内 | [原理图设计 › 时钟源 › 外置主晶振时钟源（必选）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-external-crystal-source) · S · 2026-11-01 |
| 串联器件 | XTAL_P 线上加串联器件，初始建议 24 nH 电感，减小晶振谐波对射频的影响，整机测试后调整 | [原理图设计 › 时钟源 › 外置主晶振时钟源（必选）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-external-crystal-source) · S · 2026-11-01 |
| 负载电容 | C_L = C1×C4/(C1+C4) + C_stray，用认证测试工具发单音，用频谱仪测频偏，调到 ±10 ppm 以内；晶振幅度建议大于 500 mV | [原理图设计 › 时钟源 › 外置主晶振时钟源（必选）](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-external-crystal-source) · S · 2026-11-01 |

用模组时晶振在模组内部，不用管这一节。

## 6. 天线净空

| 要点 | 内容 | 来源 |
|---|---|---|
| 模组摆放 | 模组板载 PCB 天线最好伸出底板之外，天线馈点靠近底板边缘 | [PCB 版图布局 › 基于模组的版图设计通用要点](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/pcb-layout-design.html) · S · 2026-11-01 |
| 伸不出去时 | 馈点仍尽量靠板边，把天线两侧和下方的底板挖掉，留足净空；不要把模组放在板子中间再四面挖空；天线附近底板要铺足地铜、打密集地过孔 | [PCB 版图布局 › 基于模组的版图设计通用要点](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/pcb-layout-design.html)，图"模组天线净空区" · S · 2026-11-01 |
| 外壳 | 装进外壳后天线四周建议至少 15 mm 净空；成品要测吞吐量和通信距离 | [PCB 版图布局 › 基于模组的版图设计通用要点](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/pcb-layout-design.html) · S · 2026-11-01 |
| 远离干扰源 | 射频走线附近不走高频信号；天线远离晶振、高频时钟；USB 口、USB 转串口芯片、UART 线（走线、过孔、测试点、排针）尽量远离天线，UART 线包地 | [PCB 版图布局 › 射频](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/pcb-layout-design.html) · S · 2026-11-01 |
| 自画天线（芯片方案） | PCB 天线要仿真并在开发板上实测；建议在靠近天线处加 CLC 匹配电路用于调谐；IPEX 座下方所有层净空 | [PCB 版图布局 › 射频](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/pcb-layout-design.html) · S · 2026-11-01 |

## 7. 模组还是芯片

指南给出的可用模组：ESP32-S3-MINI-1 / MINI-1U、ESP32-S3-WROOM-1 / WROOM-1U、ESP32-S3-WROOM-2（`esp32s3/esp32s3-modules.inc`，链接到各模组数据手册）· S · 2026-11-01。

| 对比项 | 模组 + 底板 | 芯片直接上板 | 依据 |
|---|---|---|---|
| 要自己做的电路 | 电源、复位、strapping、USB、天线净空 | 上面全部 + 40 MHz 晶振、flash/PSRAM 连接、射频匹配和天线（第 5、6 节） | 本页第 1–6 节，即 [原理图设计 / Schematic Checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html) 与 [PCB 版图布局](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/pcb-layout-design.html) · S · 2026-11-01 |
| 射频调试 | 只需按第 6 节摆放和净空 | 要用频谱仪调晶振频偏、调天线匹配 | 第 5、6 节：[原理图设计 › 时钟源 › 外置主晶振时钟源](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/schematic-checklist.html#schematic-checklist-external-crystal-source)、[PCB 版图布局 › 射频](https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/pcb-layout-design.html) · S · 2026-11-01 |
| 无线认证 | 乐鑫为模组发布了认证证书（[Regulatory Certificates 列表](https://documentation.espressif.com/en/documentList?t=Certificate)），整机认证可能可以引用模组证书 | 整机需要完整的射频测试 | 证书列表链接来自指南"相关文档和资源"页 · A；能否引用、引用到什么程度见 `compliance/`（E 线）· **待核实** |
| 器件成本 | 见 `mfg/prices/`：ESP32-S3-MINI-1U-N4R2 镜像价 $3.81（100+）；WROOM-1-N16R8 约 $5.12（待核实） | 芯片 + 晶振 + flash + 阻容，本次未查价 | **未查到**芯片方案的完整对比价 |
| 何时选 | 量小、要快、没有射频仪器 | 量大（单价差乘以数量能覆盖射频调试和认证费用）、尺寸受限 | 见 `mfg/production-routes.md`（估算） |

## 8. 自检清单

- [ ] 3.3 V 电源 ≥ 500 mA，入口 ESD + 10 µF；
- [ ] 每个电源管脚的去耦按第 1 节，VDD3P3 有 10 µF；
- [ ] CHIP_PU 有 10 kΩ + 1 µF，不悬空；电池方案预留电压监控芯片；
- [ ] GPIO0 有上拉，没有大电容；能用按键或测试点把 GPIO0 拉低；GPIO45/GPIO46 没有被外部电路拉到错误电平；
- [ ] GPIO19/GPIO20 走 USB，预留 22/33 Ω 串阻；留 UART 下载口；
- [ ] 模组天线伸出板边或挖空净空，外壳内四周约 15 mm；
- [ ] 芯片方案：40 MHz ±10 ppm 晶振、24 nH 串联电感、负载电容按公式初算并实测调整。
