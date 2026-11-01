# ESP32 系列 Wi-Fi / BLE 功耗与供电

一句话：ESP32 的平均功耗主要由"射频开着的时间"决定——保持 Wi-Fi 连接时用 Auto Light-sleep 能从几十 mA 降到 1 mA 以下，BLE 浅睡接 32 kHz 晶振能降到百 μA 以下；但射频发射的**瞬时峰值**有两三百 mA，电源和储能电容要按峰值设计。

> 来源：乐鑫官方 GitHub 上 ESP-IDF 低功耗文档、实测电流表、NimBLE 省电例程 README（A）和《硬件设计指南》源文件（S）。表中电流均为乐鑫在屏蔽箱内测得的**平均值**，测试条件见原文；**数据手册里的射频收发电流本会话未能读取（未查到）**。

## 关键参数：Wi-Fi 保持连接时的平均电流

| 模式（160 MHz） | ESP32-S3 | ESP32-C3 | ESP32-C6 | 来源 |
|---|---|---|---|---|
| Modem-sleep，DTIM1 | 40.1 mA | 21.47 mA | 27.48 mA | [ESP-IDF sleep-current/*_summary.inc](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current) · A · 2026-11-01 |
| Modem-sleep + DFS，DTIM1 | 20.7 mA | 11.35 mA | 14.37 mA | [ESP-IDF sleep-current/*_summary.inc](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current) · A · 2026-11-01 |
| Auto Light-sleep，DTIM1 | 2.45 mA | 1.4 mA | 0.919 mA | [ESP-IDF sleep-current/*_summary.inc](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current) · A · 2026-11-01 |
| Auto Light-sleep，DTIM3 | 1.33 mA | 0.62 mA | 0.368 mA | [ESP-IDF sleep-current/*_summary.inc](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current) · A · 2026-11-01 |
| Auto Light-sleep，DTIM10 | 0.93 mA | 0.31 mA | 0.172 mA | [ESP-IDF sleep-current/*_summary.inc](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current) · A · 2026-11-01 |
| Deep-sleep（断开 Wi-Fi） | 6.8 μA | 4.8 μA | 6.7 μA | [ESP-IDF sleep-current/*_summary.inc](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current) · A · 2026-11-01 |
| Modem-sleep 测试中记录的最大电流（DFS 关，DTIM1） | 235.8 mA | 191.53 mA | 87.55 mA | [ESP-IDF sleep-current/*_modem_sleep.inc](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current) · A · 2026-11-01 |

## 关键参数：BLE（NimBLE 省电例程，开启电源管理）

| 项目 | ESP32-S3 | ESP32-C3 | ESP32-C6 | 来源 |
|---|---|---|---|---|
| 最大电流 | 240 mA | 262 mA | 240 mA | [ESP-IDF nimble/power_save README](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/examples/bluetooth/nimble/power_save/README.md) · A · 2026-11-01 |
| Modem sleep | 17.9 mA | 12 mA | 22 mA | [ESP-IDF nimble/power_save README](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/examples/bluetooth/nimble/power_save/README.md) · A · 2026-11-01 |
| Light sleep（主晶振作睡眠时钟） | 3.3 mA | 2.3 mA | 3.3 mA | [ESP-IDF nimble/power_save README](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/examples/bluetooth/nimble/power_save/README.md) · A · 2026-11-01 |
| Light sleep（外接 32 kHz 晶振） | 230 μA | 140 μA | 34 μA | [ESP-IDF nimble/power_save README](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/examples/bluetooth/nimble/power_save/README.md) · A · 2026-11-01 |
| 射频发射/接收电流（数据手册） | 未查到 | 未查到 | 未查到 | https://documentation.espressif.com/esp32-s3_datasheet_en.pdf · 未查到 |

## 供电要点

| 项目 | 要点 | 来源 |
|---|---|---|
| 电源能力 | 单电源 3.3 V，输出电流 ≥ 500 mA（S3/C3/C6 相同） | [HDG 原理图清单 Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 发射瞬间塌压 | 发射时模拟电源电流突增可能导致电源轨塌陷，强烈建议在该电源轨加 10 μF；入口再加 10 μF（入口离得近可合并） | [HDG 原理图清单 Analog Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 抑制谐波 | 模拟电源轨加 LC，电感额定电流最好 ≥ 500 mA | [HDG 原理图清单 Analog Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 32.768 kHz 晶振 | 可选；ESR ≤ 70 kΩ；能提高计时精度、降低平均功耗 | [HDG 原理图清单 RTC Clock Source](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| BLE 睡眠时钟精度 | 蓝牙规范要求睡眠时钟精度 ≤ 500 ppm，选时钟源要满足 | [ESP-IDF low-power-mode-ble.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/low-power-mode/low-power-mode-ble.rst) · A · 2026-11-01 |

## 接口时序要点（省电模式怎么工作）

| 项目 | 要点 | 来源 |
|---|---|---|
| Modem-sleep | 按 DTIM 间隔周期醒来收信标，间隔内关 PHY；只关射频，其他模块不睡；自动进出，不用配唤醒源 | [ESP-IDF low-power-mode-wifi.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/low-power-mode/low-power-mode-wifi.rst) · A · 2026-11-01 |
| Auto Light-sleep | 在 Modem-sleep 基础上空闲时 CPU 暂停、系统时钟关，保持 Wi-Fi 连接 | [ESP-IDF sleep-current/esp32s3_summary.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32s3_summary.inc) · A · 2026-11-01 |
| Deep-sleep | 断开 Wi-Fi，需要手动进入和配置唤醒源；醒来重连 Wi-Fi 也要耗电（重连能耗本次未查到） | [ESP-IDF sleep-current/esp32s3_summary.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current/esp32s3_summary.inc) · A · 2026-11-01 |
| 影响平均电流的三件事 | 唤醒间隔（DTIM/listen interval）、每次工作时长、基础电流 | [ESP-IDF low-power-mode-wifi.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/low-power-mode/low-power-mode-wifi.rst) · A · 2026-11-01 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| 用平均电流选 LDO | 平均 1 mA 不代表电源只要 1 mA；测试中最大电流到 235.8 mA（S3）/ 262 mA（C3 BLE），LDO 要满足 ≥500 mA 要求 | [HDG 原理图清单 Power Supply](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 以为 menuconfig 选了 32 kHz 就生效 | 初始化时检测不到外部 32 kHz 晶振会退回主晶振，浅睡电流从百 μA 级变成 mA 级 | [ESP-IDF low-power-mode-ble.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/low-power-mode/low-power-mode-ble.rst) · A · 2026-11-01 |
| Auto Light-sleep 进不去 | 多半是空闲时间不够：日志太多、持续扫描等配置都会阻止进入 | [ESP-IDF low-power-mode-ble.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/low-power-mode/low-power-mode-ble.rst) · A · 2026-11-01 |
| 用开发板测模组深睡电流 | 乐鑫说明：ESP32-S3、C3 的开发板上其他电路在深睡时仍耗电，不建议直接用开发板测模组电流；C6 的 DevKitC-1/DevKitM-1 可以。另外普通电流表内阻大，μA–mA 动态范围也难测准 | [ESP-IDF current-consumption-measurement-modules.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/current-consumption-measurement-modules.rst) · A · 2026-11-01 |

## 来源列表

- [IDF] ESP-IDF 低功耗文档、sleep-current 表、nimble/power_save 例程，commit d445e94：https://github.com/espressif/esp-idf
- [HDG] ESP Hardware Design Guidelines，commit a727293：https://github.com/espressif/esp-hardware-design-guidelines
- 查询日期：2026-11-01。
