# ESP32-C3（芯片）与 ESP32-C3 模组

一句话：乐鑫单核 RISC-V、2.4 GHz Wi-Fi + Bluetooth LE 的低成本 SoC，22 个 GPIO，带 USB Serial/JTAG（不是 USB OTG），**没有电容触摸**；适合"按键 + 小屏 + 连网"、对成本敏感的产品。

> 本页芯片参数来自乐鑫官方 GitHub 上的《硬件设计指南》源文件（S）和 ESP-IDF 文档/头文件（A）。数据手册站点本会话不可达，只在数据手册里的值写"未查到"。

## 关键参数（芯片）

| 参数 | 值 | 来源 |
|---|---|---|
| 无线 | Wi-Fi 2.4 GHz；Bluetooth 5 (LE) | [HDG esp32c3-features.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c3/esp32c3-features.inc) · S · 2026-11-01 |
| CPU | 32 位 RISC-V 单核 | [HDG esp32c3-features.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c3/esp32c3-features.inc) · S · 2026-11-01 |
| 物理 GPIO | 22 个（GPIO0–21） | [ESP-IDF gpio/esp32c3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c3.inc) · A · 2026-11-01 |
| 单电源推荐 | 3.3 V，电源输出能力 ≥ 500 mA | [HDG 原理图清单 Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 数字/模拟电源 | VDD3P3_CPU 3.0–3.6 V；VDDA、VDD3P3 3.0–3.6 V | [HDG 原理图清单 Digital / Analog Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| VDD3P3_RTC | RTC 与模拟电源脚，近处 0.1 μF；不能单独作为备份电源 | [HDG 原理图清单 RTC Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 主晶振 | 只支持 40 MHz；±10 ppm 以内 | [HDG 原理图清单 External Crystal](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 外部 flash | 最大 16 MB，由 VDD_SPI 供电 | [HDG 原理图清单 Flash](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| USB | USB Serial/JTAG 控制器（USB 2.0 全速设备）；D-/D+ = GPIO18/GPIO19；无 USB OTG | [HDG 原理图清单 USB](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 电容触摸 | 无（soc_caps.h 没有 SOC_TOUCH_SENSOR_SUPPORTED） | [ESP-IDF soc_caps.h (esp32c3)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c3/include/soc/soc_caps.h) · A · 2026-11-01 |
| ADC | ADC1_CH0–4 = GPIO0–4；ADC2_CH0 = GPIO5 | [ESP-IDF gpio/esp32c3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c3.inc) · A · 2026-11-01 |
| ADC 校准后误差 | ATTEN=0（0–750 mV）±10 mV；ATTEN=3（0–2500 mV）±35 mV | [HDG 原理图清单 ADC](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| UART / I2C / LEDC | UART×2、I2C×1、LEDC 6 通道 | [ESP-IDF soc_caps.h (esp32c3)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c3/include/soc/soc_caps.h) · A · 2026-11-01 |
| 深睡平均电流（乐鑫实测） | 4.8 μA | [ESP-IDF sleep-current/esp32c3_summary.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32c3_summary.inc) · A · 2026-11-01 |
| 数据手册里的电流、射频指标 | 未查到（documentation.espressif.com/esp32-c3_datasheet_en.pdf 本会话不可达） | https://documentation.espressif.com/esp32-c3_datasheet_en.pdf · 未查到 |

## 引脚要点

| 引脚 | 要点 | 来源 |
|---|---|---|
| Strapping | GPIO2、GPIO8、GPIO9 | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 启动模式 | 默认 GPIO2、GPIO8 浮空，GPIO9 上拉；SPI Boot：GPIO2=1、GPIO9=1；下载：GPIO2=1、GPIO8=1、GPIO9=0 | [HDG esp32c3-chip-boot-mode-control.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c3/esp32c3-chip-boot-mode-control.inc) · S · 2026-11-01 |
| GPIO2 | 其实不决定启动模式，但因上电毛刺建议上拉 | [HDG esp32c3-chip-boot-mode-control.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c3/esp32c3-chip-boot-mode-control.inc) · S · 2026-11-01 |
| GPIO12–17 | 通常接 SPI flash，不建议他用；flash 合封的型号这些脚不能外用 | [ESP-IDF gpio/esp32c3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c3.inc) · A · 2026-11-01 |
| GPIO18 / GPIO19 | 默认 USB-JTAG；改作 GPIO 后 USB-JTAG 失效 | [ESP-IDF gpio/esp32c3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c3.inc) · A · 2026-11-01 |
| 深睡唤醒脚 | 只有 GPIO0–5 能从深睡唤醒；其他 GPIO 只能从浅睡唤醒 | [ESP-IDF gpio/esp32c3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c3.inc) · A · 2026-11-01 |
| CHIP_EN | 高使能、低复位；不能悬空；推荐 RC 10 kΩ / 1 μF | [HDG 原理图清单 Chip Power-up and Reset Timing](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |

## 电压、电流

| 项目 | 值 | 来源 |
|---|---|---|
| Wi-Fi Modem-sleep（160 MHz，DTIM1） | 平均 21.47 mA，最大 191.53 mA；开 DFS 平均 11.35 mA | [ESP-IDF sleep-current/esp32c3_modem_sleep.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32c3_modem_sleep.inc) · A · 2026-11-01 |
| Wi-Fi Auto Light-sleep | DTIM1 1.4 mA；DTIM3 0.62 mA；DTIM10 0.31 mA | [ESP-IDF sleep-current/esp32c3_summary.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32c3_summary.inc) · A · 2026-11-01 |
| BLE 省电例程 | 峰值 262 mA；modem sleep 12 mA；light sleep 2.3 mA（主晶振）/ 140 μA（外接 32 kHz） | [ESP-IDF nimble/power_save README](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/examples/bluetooth/nimble/power_save/README.md) · A · 2026-11-01 |

## 接口时序要点

| 项目 | 要点 | 来源 |
|---|---|---|
| 上电/复位 | t_STBL ≥ 50 μs，t_RST ≥ 50 μs | [HDG 原理图清单 Chip Power-up and Reset Timing](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| Strapping 保持 | t_H ≥ 3 ms | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| USB 走线 | 90 Ω ±10% 差分，下方完整地平面 | [HDG PCB 布局 USB](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |

## 模组参数（与芯片分开）

| 参数 | 值 | 来源 |
|---|---|---|
| 官方模组型号 | ESP32-C3-MINI-1/1U、ESP32-C3-WROOM-02/02U，以及 ESP8685-WROOM-01/03/04/05/06/07 | [HDG esp32c3-modules.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c3/esp32c3-modules.inc) · S · 2026-11-01 |
| 模组尺寸、天线、可用 GPIO、工作电压 | 未查到（esp32-c3-mini-1_datasheet_en.pdf 所在站点不可达） | https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.pdf · 未查到 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| 以为 C3 有触摸 | C3 没有电容触摸外设；要触摸选 S3 或外加触摸 IC | [ESP-IDF soc_caps.h (esp32c3)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c3/include/soc/soc_caps.h) · A · 2026-11-01 |
| 以为 C3 能做 USB 设备（键盘、U 盘） | 只有 USB Serial/JTAG，没有 OTG 外设 | [ESP-IDF soc_caps.h (esp32c3)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c3/include/soc/soc_caps.h) · A · 2026-11-01 |
| GPIO9 接按键带大电容 | GPIO9 是启动脚，不要加大电容，否则可能进下载模式 | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| GPIO18 上电 50 μs 高电平毛刺 | GPIO18 上电有约 50,000 ns 高电平毛刺；MTCK、MTDO、GPIO10、U0RXD 有约 5 ns 低电平毛刺 | [HDG esp32c3-table-glitches.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c3/esp32c3-table-glitches.inc) · S · 2026-11-01 |
| 用 ADC2 | ADC2 没有出厂校准，某些芯片版本 ADC2 不可用；用 ADC1 | [HDG esp32c3-adc.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c3/esp32c3-adc.inc) · S · 2026-11-01 |
| 深睡唤醒脚选错 | 只有 GPIO0–5 能唤醒深睡，按键要接到这几个脚 | [ESP-IDF gpio/esp32c3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c3.inc) · A · 2026-11-01 |
| USB 自动下载失效 | 应用把 USB 脚另作他用后无法自动下载，要保留 GPIO9 按键和 UART0 | [HDG download-guidelines.rst](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/download-guidelines.rst) · S · 2026-11-01 |

## 来源列表

- [HDG] ESP Hardware Design Guidelines 源文件，commit a727293：https://github.com/espressif/esp-hardware-design-guidelines （渲染版 https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/index.html 本会话不可达）
- [IDF] ESP-IDF，commit d445e94：https://github.com/espressif/esp-idf
- [DS] ESP32-C3 Series Datasheet：https://documentation.espressif.com/esp32-c3_datasheet_en.pdf （未读取）
- [Errata] ESP32-C3 勘误（HDG 中引用）：https://www.espressif.com/sites/default/files/documentation/esp32-c3_errata_en.pdf （未读取）
- 查询日期：2026-11-01。
