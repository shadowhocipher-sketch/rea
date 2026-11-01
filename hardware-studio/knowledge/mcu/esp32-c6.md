# ESP32-C6（芯片）与 ESP32-C6 模组

一句话：乐鑫单核 RISC-V SoC，2.4 GHz **Wi-Fi 6** + Bluetooth LE + **802.15.4（Thread/Zigbee）**，带 LP（低功耗）核和 USB Serial/JTAG，**没有电容触摸、没有 USB OTG**；适合要接 Matter/Thread/Zigbee 或要 Wi-Fi 6 省电特性的产品。

> 本页芯片参数来自乐鑫官方 GitHub 上的《硬件设计指南》源文件（S）和 ESP-IDF 文档/头文件（A）。数据手册站点本会话不可达，只在数据手册里的值写"未查到"。

## 关键参数（芯片）

| 参数 | 值 | 来源 |
|---|---|---|
| 无线 | Wi-Fi 6（2.4 GHz）；Bluetooth 5 (LE)；802.15.4 Thread/Zigbee | [HDG esp32c6-features.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c6/esp32c6-features.inc) · S · 2026-11-01 |
| CPU | 32 位 RISC-V 单核（HP）；另有 LP 核（SOC_LP_CORE_SUPPORTED） | [ESP-IDF soc_caps.h (esp32c6)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c6/include/soc/soc_caps.h) · A · 2026-11-01 |
| 物理 GPIO | 31 个（GPIO0–30）；合封 flash 的型号 SPI0/1 脚和 GPIO10–11 不引出，只剩 22 个 | [ESP-IDF gpio/esp32c6.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c6.inc) · A · 2026-11-01 |
| 封装 | QFN40 与 QFN32；区别是 flash 是否合封 | [HDG esp32c6-chip-core-schem-note.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c6/esp32c6-chip-core-schem-note.inc) · S · 2026-11-01 |
| 合封 flash | 4 MB 或 8 MB，引脚不引出 | [HDG 原理图清单 Flash](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 单电源推荐 | 3.3 V，电源输出能力 ≥ 500 mA | [HDG 原理图清单 Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 数字电源 VDDPST1 / VDDPST2 | 3.0–3.6 V | [HDG 原理图清单 Digital Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 模拟电源 VDDA / VDDA3P3 | 3.0–3.6 V；VDDA3P3 发射时电流突增，加 10 μF | [HDG 原理图清单 Analog Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 主晶振 | 只支持 40 MHz；±10 ppm 以内 | [HDG 原理图清单 External Crystal](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 射频匹配 | 推荐 CLCCL 结构（带通，兼顾谐波与低频噪声） | [HDG 原理图清单 RF Circuit](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| USB | USB Serial/JTAG（USB 2.0 全速设备），D-/D+ = GPIO12/GPIO13；无 OTG | [HDG 原理图清单 USB](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 电容触摸 | 无（soc_caps.h 没有 SOC_TOUCH_SENSOR_SUPPORTED） | [ESP-IDF soc_caps.h (esp32c6)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c6/include/soc/soc_caps.h) · A · 2026-11-01 |
| ADC | ADC1_CH0–6 = GPIO0–6（HDG）；只有 1 个 ADC 外设（soc_caps.h：SOC_ADC_PERIPH_NUM = 1） | [HDG esp32c6-adc.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c6/esp32c6-adc.inc) · S · 2026-11-01；[ESP-IDF soc_caps.h (esp32c6)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c6/include/soc/soc_caps.h) · A · 2026-11-01 |
| ADC 校准后误差 | ATTEN=0（0–1000 mV）±12 mV；ATTEN=3（0–3300 mV）±40 mV | [HDG 原理图清单 ADC](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| UART / I2C / LEDC | HP UART×2 + LP UART×1（固定脚）、I2C×2、LEDC 6 通道 | [ESP-IDF soc_caps.h (esp32c6)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c6/include/soc/soc_caps.h) · A · 2026-11-01 |
| 深睡平均电流（乐鑫实测） | 6.7 μA | [ESP-IDF sleep-current/esp32c6_summary.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32c6_summary.inc) · A · 2026-11-01 |
| 数据手册里的电流、射频指标 | 未查到（documentation.espressif.com/esp32-c6_datasheet_en.pdf 本会话不可达） | https://documentation.espressif.com/esp32-c6_datasheet_en.pdf · 未查到 |

## 引脚要点

| 引脚 | 要点 | 来源 |
|---|---|---|
| Strapping | GPIO8、GPIO9、GPIO15、MTMS、MTDI | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| MTMS / MTDI 是哪个 GPIO | MTMS = GPIO4，MTDI = GPIO5 | [ESP-IDF io_mux_reg.h (esp32c6)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c6/register/soc/io_mux_reg.h) · A · 2026-11-01 |
| 启动模式 | 默认 GPIO8 浮空、GPIO9 上拉；SPI Boot：GPIO9=1；下载：GPIO8=1、GPIO9=0；GPIO8=0 且 GPIO9=0 是无效组合，要避免 | [HDG esp32c6-chip-boot-mode-control.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c6/esp32c6-chip-boot-mode-control.inc) · S · 2026-11-01 |
| GPIO15、MTMS、MTDI 的 strapping 作用 | 未查到（数据手册 Boot Configurations 章节） | https://documentation.espressif.com/esp32-c6_datasheet_en.pdf · 未查到 |
| GPIO24–30 | 通常接 SPI flash，不建议他用；无合封 flash 的型号 GPIO14 不引出 | [ESP-IDF gpio/esp32c6.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c6.inc) · A · 2026-11-01 |
| GPIO12 / GPIO13 | 默认 USB-JTAG；改作 GPIO 后 USB-JTAG 失效 | [ESP-IDF gpio/esp32c6.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c6.inc) · A · 2026-11-01 |
| LP GPIO | GPIO0–7 是 LP_GPIO0–7；深睡时只有 VDDPST1 电源域的 GPIO 能控制 | [ESP-IDF gpio/esp32c6.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c6.inc) · A · 2026-11-01 |
| HP UART0 | U0TXD=GPIO16、U0RXD=GPIO17 | [HDG 原理图清单 UART](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| VDD_SPI（pin 23） | 由 VDDPST2 经 R_SPI 输出约 3.3 V 给 flash，有压降，VDDPST2 要 ≥3.0 V；不作电源时可当普通 GPIO | [HDG esp32-c-series-digital-power-supply.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/shared/esp32-c-series-digital-power-supply.inc) · S · 2026-11-01 |

## 电压、电流

| 项目 | 值 | 来源 |
|---|---|---|
| Wi-Fi Modem-sleep（160 MHz，DTIM1） | 平均 27.48 mA，最大 87.55 mA；开 DFS 平均 14.37 mA | [ESP-IDF sleep-current/esp32c6_modem_sleep.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32c6_modem_sleep.inc) · A · 2026-11-01 |
| Wi-Fi Auto Light-sleep | DTIM1 0.919 mA；DTIM3 0.368 mA；DTIM10 0.172 mA | [ESP-IDF sleep-current/esp32c6_summary.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32c6_summary.inc) · A · 2026-11-01 |
| BLE 省电例程 | 峰值 240 mA；modem sleep 22 mA；light sleep 3.3 mA（主晶振）/ 34 μA（外接 32 kHz） | [ESP-IDF nimble/power_save README](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/examples/bluetooth/nimble/power_save/README.md) · A · 2026-11-01 |

## 接口时序要点

| 项目 | 要点 | 来源 |
|---|---|---|
| 上电/复位 | t_STBL ≥ 50 μs、t_RST ≥ 50 μs；复位电压 –0.3 ~ 0.25×VDDPST1 | [HDG 原理图清单 Chip Power-up and Reset Timing](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| Strapping 保持 | t_H ≥ 3 ms | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |

## 模组参数（与芯片分开）

| 参数 | 值 | 来源 |
|---|---|---|
| 官方模组型号 | ESP32-C6-MINI-1/1U、ESP32-C6-WROOM-1/1U | [HDG esp32c6-modules.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c6/esp32c6-modules.inc) · S · 2026-11-01 |
| 模组尺寸、天线、可用 GPIO、工作电压 | 未查到（esp32-c6-mini-1_mini-1u_datasheet_en.pdf 所在站点不可达） | https://documentation.espressif.com/esp32-c6-mini-1_mini-1u_datasheet_en.pdf · 未查到 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| GPIO8/GPIO9 同时为 0 | 无效组合，会触发不可预期行为；GPIO8 不要在上电时被外部拉低 | [HDG esp32c6-chip-boot-mode-control.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c6/esp32c6-chip-boot-mode-control.inc) · S · 2026-11-01 |
| GPIO9 加大电容 | 可能进下载模式 | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| Wi-Fi 网关同时当 Thread/Zigbee 路由 | 单射频分时复用，Wi-Fi 软 AP 与 Thread/Zigbee Router 不支持共存；做边界路由/网关乐鑫建议双芯片（如 S3 + H2）双天线 | [ESP-IDF coexist.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| BLE 浅睡用了主晶振 | 不接 32 kHz 晶振时浅睡 3.3 mA，接了 34 μA；即使 menuconfig 选了 32 kHz，初始化检测不到晶振也会退回主晶振 | [ESP-IDF low-power-mode-ble.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/low-power-mode/low-power-mode-ble.rst) · A · 2026-11-01 |
| C6 浅睡要开 MAC/BB 掉电 | 例程注明 C6 浅睡要设置 CONFIG_ESP_PHY_MAC_BB_PD 才能正常 | [ESP-IDF nimble/power_save README](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/examples/bluetooth/nimble/power_save/README.md) · A · 2026-11-01 |
| 以为 C6 有触摸 / OTG | 两者都没有 | [ESP-IDF soc_caps.h (esp32c6)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c6/include/soc/soc_caps.h) · A · 2026-11-01 |

## 来源列表

- [HDG] ESP Hardware Design Guidelines 源文件，commit a727293：https://github.com/espressif/esp-hardware-design-guidelines （渲染版 https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c6/index.html 本会话不可达）
- [IDF] ESP-IDF，commit d445e94：https://github.com/espressif/esp-idf
- [DS] ESP32-C6 Series Datasheet：https://documentation.espressif.com/esp32-c6_datasheet_en.pdf （未读取）
- 查询日期：2026-11-01。
