# ESP32-S3（芯片）与 ESP32-S3 模组

一句话：乐鑫双核 Xtensa LX7、2.4 GHz Wi-Fi + Bluetooth LE、带 USB OTG 和 USB Serial/JTAG、14 路电容触摸的 SoC；做"有屏、有触摸、要连网"的小产品时的默认首选。

> 读法：每行最后一列是来源（链接 · 级别 · 查询日期）。本页芯片参数来自乐鑫官方 GitHub 上的《硬件设计指南》源文件（S）和 ESP-IDF 文档/头文件（A）。
> 乐鑫数据手册站点 documentation.espressif.com / www.espressif.com 在本会话 DNS 不可解析，凡是只有数据手册才有的值都写了"未查到"。

## 关键参数（芯片）

| 参数 | 值 | 来源 |
|---|---|---|
| 无线 | Wi-Fi 2.4 GHz；Bluetooth 5 (LE) | [HDG esp32s3-features.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32s3/esp32s3-features.inc) · S · 2026-11-01 |
| CPU | 双核 Xtensa LX7；ULP 协处理器（RISC-V 或 FSM） | [HDG esp32s3-features.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32s3/esp32s3-features.inc) · S · 2026-11-01 |
| 物理 GPIO | 45 个（GPIO0–21、GPIO26–48） | [ESP-IDF gpio/esp32s3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32s3.inc) · A · 2026-11-01 |
| 单电源推荐 | 3.3 V，电源输出能力 ≥ 500 mA | [HDG 原理图清单 Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 数字电源 VDD3P3_CPU / VDD3P3_RTC | 3.0–3.6 V | [HDG esp32-s-series-digital-power-supply.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/shared/esp32-s-series-digital-power-supply.inc) · S · 2026-11-01 |
| 模拟电源 VDD3P3 / VDDA | 3.0–3.6 V | [HDG 原理图清单 Analog Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 主晶振 | 只支持 40 MHz；精度 ±10 ppm 以内 | [HDG 原理图清单 External Crystal](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| USB | 全速 USB OTG（USB 2.0）+ USB Serial/JTAG；D-/D+ = GPIO19/GPIO20 | [HDG 原理图清单 USB](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 触摸通道 | 14 路，TOUCH1–14 = GPIO1–14；只有 GPIO14 能驱动屏蔽电极 | [HDG esp32s3-table-touch-gpio.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32s3/esp32s3-table-touch-gpio.inc) · S · 2026-11-01 |
| ADC | ADC1_CH0–9 = GPIO1–10；ADC2_CH0–9 = GPIO11–20；推荐用 ADC1 | [ESP-IDF gpio/esp32s3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32s3.inc) · A · 2026-11-01 |
| ADC 校准后误差 | ATTEN=0（0–850 mV）±5 mV；ATTEN=3（0–2900 mV）±50 mV | [HDG 原理图清单 ADC](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| UART / I2C / LEDC | UART×3、I2C×2、LEDC 8 通道 | [ESP-IDF soc_caps.h (esp32s3)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32s3/include/soc/soc_caps.h) · A · 2026-11-01 |
| 深睡平均电流（乐鑫实测） | 6.8 μA（汇总表）；同文正文写"约 6.9 μA"——两处略有出入 | [ESP-IDF sleep-current/esp32s3_summary.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32s3_summary.inc) · A · 2026-11-01 |
| 数据手册里的深睡/工作电流、射频指标 | 未查到（documentation.espressif.com/esp32-s3_datasheet_en.pdf 本会话 DNS 不可解析） | https://documentation.espressif.com/esp32-s3_datasheet_en.pdf · 未查到 |

## 引脚要点

| 引脚 | 要点 | 来源 |
|---|---|---|
| Strapping | GPIO0、GPIO3、GPIO45、GPIO46 | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| GPIO0 / GPIO46（启动模式） | 默认 GPIO0 上拉=1、GPIO46 下拉=0；GPIO0=1 → SPI Boot；GPIO0=0 且 GPIO46=0 → 下载模式（USB/UART） | [HDG esp32s3-chip-boot-mode-control.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32s3/esp32s3-chip-boot-mode-control.inc) · S · 2026-11-01 |
| GPIO45（VDD_SPI 电压） | EFUSE_VDD_SPI_FORCE=0 时：GPIO45=0 → VDD_SPI 3.3 V；GPIO45=1 → 1.8 V | [HDG esp32-s-series-digital-power-supply.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/shared/esp32-s-series-digital-power-supply.inc) · S · 2026-11-01 |
| GPIO3（JTAG 信号源选择） | 烧录 eFuse `STRAP_JTAG_SEL` 后，由 strapping 脚 GPIO3 选择 JTAG 信号源：复位时 GPIO3 为低 → JTAG 接 GPIO39–GPIO42（MTCK/MTDO/MTDI/MTMS）；为高 → JTAG 用内置 USB_SERIAL_JTAG。未烧该 eFuse 时（出厂默认）JTAG 固定接 USB_SERIAL_JTAG，GPIO3 的电平不影响 JTAG | [ESP-IDF jtag-debugging/configure-other-jtag.rst "Configure eFuses"](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/jtag-debugging/configure-other-jtag.rst#L24)；[jtag-debugging/esp32s3.inc（jtag-sel-gpio = GPIO3）](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/jtag-debugging/esp32s3.inc#L132) · A · 2026-11-01 |
| GPIO26–32 | 通常接 SPI flash/PSRAM，不建议他用；用 Octal flash/PSRAM（如 S3R8）时 GPIO33–37 也被占 | [ESP-IDF gpio/esp32s3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32s3.inc) · A · 2026-11-01 |
| GPIO19 / GPIO20 | 默认给 USB-JTAG；改作普通 GPIO 后 USB-JTAG 失效 | [ESP-IDF gpio/esp32s3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32s3.inc) · A · 2026-11-01 |
| GPIO0–21（RTC GPIO） | 有 RTC_GPIO 功能；深睡时只有 VDD3P3_RTC 电源域的 GPIO 能控制 | [ESP-IDF gpio/esp32s3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32s3.inc) · A · 2026-11-01 |
| UART0 | U0TXD=GPIO43、U0RXD=GPIO44；建议 TX 串 499 Ω 抑制谐波 | [HDG 原理图清单 UART](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| CHIP_PU | 高电平使能、低电平复位；不能悬空；推荐 RC 延时 R=10 kΩ、C=1 μF | [HDG 原理图清单 Chip Power-up and Reset Timing](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |

## 电压、电流

| 项目 | 值 | 来源 |
|---|---|---|
| 入口电容 | 主电源入口加 ESD 二极管和 ≥10 μF 电容 | [HDG 原理图清单 Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| VDD_SPI 1.8 V 档 | 内部 LDO 供电，典型可提供 40 mA | [HDG esp32-s-series-digital-power-supply.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/shared/esp32-s-series-digital-power-supply.inc) · S · 2026-11-01 |
| VDD_SPI 3.3 V 档 | 由 VDD3P3_RTC 经 14 Ω 电阻 R_SPI 供电，有压降；接 3.3 V flash/PSRAM 时 VDD3P3_RTC 要保持 >3.0 V | [HDG esp32-s-series-digital-power-supply.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/shared/esp32-s-series-digital-power-supply.inc) · S · 2026-11-01 |
| Wi-Fi 连接保持 Modem-sleep（160 MHz，DTIM1） | 平均 40.1 mA，最大 235.8 mA；开 DFS 后平均 20.7 mA | [ESP-IDF sleep-current/esp32s3_modem_sleep.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32s3_modem_sleep.inc) · A · 2026-11-01 |
| Wi-Fi Auto Light-sleep | DTIM1 2.45 mA；DTIM3 1.33 mA；DTIM10 0.93 mA（屏蔽箱内实测平均值） | [ESP-IDF sleep-current/esp32s3_summary.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32s3_summary.inc) · A · 2026-11-01 |
| BLE 省电例程 | 峰值 240 mA；modem sleep 17.9 mA；light sleep 3.3 mA（主晶振）/ 230 μA（外接 32 kHz） | [ESP-IDF nimble/power_save README](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/examples/bluetooth/nimble/power_save/README.md) · A · 2026-11-01 |

## 接口时序要点

| 项目 | 要点 | 来源 |
|---|---|---|
| 上电 | 3.3 V 稳定后再拉高 CHIP_PU：t_STBL ≥ 50 μs；复位低电平 t_RST ≥ 50 μs，复位电压 –0.3 ~ 0.25×VDD3P3_RTC | [HDG 原理图清单 Chip Power-up and Reset Timing](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| Strapping 采样 | CHIP_PU 拉高后 strapping 电平至少保持 t_H = 3 ms | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 慢上电 / 电池 | 慢上电、频繁上下电、电源不稳时 RC 可能不够，预留电压监控复位芯片，阈值约 3.0 V | [HDG 原理图清单 Chip Power-up and Reset Timing](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| USB 走线 | 90 Ω ±10% 差分；靠芯片预留串阻（22/33 Ω）和对地电容位 | [HDG PCB 布局 USB](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |

## 模组参数（与芯片分开）

模组（ESP32-S3-WROOM-1/1U、MINI-1/1U、WROOM-2）自带 flash/PSRAM、晶振、射频匹配和天线，外部只需 3.3 V 和少量阻容。

| 参数 | 值 | 来源 |
|---|---|---|
| 官方模组型号 | ESP32-S3-MINI-1/1U、ESP32-S3-WROOM-1/1U、ESP32-S3-WROOM-2 | [HDG esp32s3-modules.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32s3/esp32s3-modules.inc) · S · 2026-11-01 |
| 模组工作电压、尺寸、天线增益、可用 GPIO 数 | 未查到（模组数据手册 esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf 所在站点不可达） | https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf · 未查到 |
| 内置 Octal PSRAM 的模组 | IDF 注明：搭载 ESP32-S3R8 / ESP32-S3R8V 芯片的板子 GPIO33–37 也不建议他用；某个模组型号内部用的是哪颗芯片要查模组手册（未查到，站点不可达） | [ESP-IDF gpio/esp32s3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32s3.inc) · A · 2026-11-01 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| GPIO0 上挂大电容 | 不要在 GPIO0 加大电容，否则可能进下载模式；建议加上拉 | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 应用里占用了 USB 脚 | 应用关闭 USB PHY、把 USB 改作 Host/标准设备、或把 GPIO19/20 给了别的外设，USB 自动下载就失效；要保留对 strapping 脚的控制（按键）和 UART 下载口 | [HDG download-guidelines.rst](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/download-guidelines.rst) · S · 2026-11-01 |
| USB-OTG 下载模式改变 IO 电平 | 启用 USB-OTG Download Boot 时 ROM 会把 MTDO 拉高、MTCK/GPIO38 拉低等；不需要时烧 EFUSE_DIS_USB_OTG_DOWNLOAD_MODE | [HDG esp32s3-usb.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32s3/esp32s3-usb.inc) · S · 2026-11-01 |
| 上电毛刺 | GPIO1–14、XTAL_32K_P/N、GPIO17–20 上电时有约 60 μs 毛刺；GPIO19/20 各有两个高电平毛刺。别用这些脚直接驱动上电即动作的负载（继电器、MOS 栅极） | [HDG esp32s3-table-glitches.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32s3/esp32s3-table-glitches.inc) · S · 2026-11-01 |
| USB_D+ 上电抖动 | 上电时 D+ 会高低跳变，需要稳定初始态就加外部上拉 | [HDG 原理图清单 USB](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 触摸没有过 CS 测试 | 乐鑫注明 S3 触摸尚未通过传导抗扰度（CS）测试，适用场景受限（例如接市电适配器的产品要谨慎） | [HDG 原理图清单 Touch Sensor](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 随手用 ADC2 | 乐鑫硬件指南对 S3 的建议就是一句"推荐使用 ADC1"；ADC 引脚旁加 0.1 μF 滤波电容提高精度 | [HDG esp32s3-adc.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32s3/esp32s3-adc.inc) · S · 2026-11-01 |
| 未用的高阻脚漏电 | 复位后高阻、无内部上下拉的空脚要加上下拉或软件开内部上下拉，避免额外功耗 | [HDG 原理图清单 GPIO](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| eFuse 表描述写的是 gpio10 | ESP-IDF 的 S3 eFuse 表对 `STRAP_JTAG_SEL` 的说明写"through strapping gpio10"，与 JTAG 文档的 GPIO3 冲突；S3 文档变量与本库 strapping 列表（GPIO0/3/45/46）都指向 GPIO3，按 GPIO3 设计，数据手册 Boot Configurations 章节本次未读到（documentation.espressif.com 不可达），定稿前回原厂核对 | [ESP-IDF esp32s3/esp_efuse_table.csv 第 164 行](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/efuse/esp32s3/esp_efuse_table.csv#L164) · A · 2026-11-01 · 待核实 |
| 开了射频却没接天线 | 射频启用时必须接天线，否则可能工作不稳甚至损坏射频电路；不用射频就别初始化射频栈 | [HDG 原理图清单 RF Tuning](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |

## 来源列表

- [HDG] ESP Hardware Design Guidelines 源文件（乐鑫官方 GitHub，commit a727293，2026-10-26）：https://github.com/espressif/esp-hardware-design-guidelines 。渲染版：https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/index.html （本会话不可达）。文档许可证 CC BY-SA，本库只引用不转载。
- [IDF] ESP-IDF 文档与头文件（乐鑫官方 GitHub，commit d445e94，2026-10-28）：https://github.com/espressif/esp-idf
- [DS] ESP32-S3 Series Datasheet：https://documentation.espressif.com/esp32-s3_datasheet_en.pdf （本会话 DNS 不可解析，未读取）。GPIO3 的 JTAG 信号源作用改从 ESP-IDF JTAG 调试文档（A 级）取得；乐鑫硬件设计指南（commit a727293）里只列出 GPIO3 是 strapping 脚，没有写它的作用。
- 查询日期：2026-11-01。
