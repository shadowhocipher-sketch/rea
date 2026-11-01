# ESP32 天线净空、射频布局与 Wi-Fi/BLE 共存

一句话：模组的板载 PCB 天线要伸出底板边缘或在下方挖空、外壳内四周留 ≥15 mm 净空、远离 USB/串口/晶振；Wi-Fi、BLE（以及 C6 的 802.15.4）共用**一条射频通路**分时工作，大多数 STA + BLE 组合稳定，SoftAP/嗅探 + BLE 不稳定。

> 来源：乐鑫官方 GitHub 上《硬件设计指南》PCB 布局章节源文件（S）与 ESP-IDF《RF Coexistence》文档（A）。

## 关键参数：天线与净空（模组上板）

| 项目 | 要点 | 来源 |
|---|---|---|
| 模组位置 | 板载 PCB 天线放到底板外，天线馈点靠近底板边缘 | [HDG pcb-layout-design.rst 模组摆放](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |
| 天线不能伸出时 | 馈点仍尽量靠板边，把天线两侧和下方的底板切掉留净空；**不要**把模组放在板中间、四周挖空 | [HDG pcb-layout-design.rst 模组摆放](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |
| 天线附近铺地 | 天线附近的底板要有足够铺地和密集地过孔 | [HDG pcb-layout-design.rst 模组摆放](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |
| 外壳净空 | 装进外壳后天线四周建议至少 15 mm 净空 | [HDG pcb-layout-design.rst 模组摆放](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |
| 最终验证 | 成品要测吞吐率和通信距离 | [HDG pcb-layout-design.rst 模组摆放](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |
| 外接天线（IPEX） | S3、C6 等：IPEX 座下方所有层净空 | [HDG pcb-layout-design.rst RF](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |
| 具体净空尺寸（毫米） | 各模组的净空示意图在 HDG 图片里，本次只读到文字，尺寸未查到；以模组数据手册为准 | https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf · 未查到 |

## 引脚 / 电路要点：芯片直接上板（自画射频）

| 项目 | 要点 | 来源 |
|---|---|---|
| 射频走线 | 50 Ω 阻抗控制；外层走线不换层、不分叉、尽量短，转角 135° 或圆弧，两侧密集地过孔，相邻层地平面完整 | [HDG pcb-layout-design.rst RF](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |
| 芯片侧匹配 | S3/C3：CLC；C6：CLCCL；用 0201 元件、靠近引脚之字形摆放；匹配参数随板子不同必须重新调 | [HDG 原理图清单 RF Circuit / RF Tuning](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 天线侧 | 天线阻抗约 50 Ω；建议预留 CLC 匹配；S3、C6 建议加天线 ESD 器件；PCB 天线要仿真 + 开发板实测 | [HDG 原理图清单 RF Circuit](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 晶振 | 40 MHz ±10 ppm；频偏超标直接降低射频性能；用 TX tone 测频偏、调负载电容 | [HDG 原理图清单 External Crystal](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |

## 电压、电流

| 项目 | 要点 | 来源 |
|---|---|---|
| 射频相关功耗 | 见 [esp32-wifi-ble-power.md](esp32-wifi-ble-power.md)；共存时射频分时，平均电流取决于两种协议的占空 | [ESP-IDF coexist.rst Overview](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |

## 接口时序要点：共存（时分复用）

| 组合 | 支持情况 | 来源 |
|---|---|---|
| Wi-Fi STA（扫描/连接中/已连接）+ BLE（扫描/广播/连接） | Y（支持且稳定） | [ESP-IDF coexist.rst 表 Wi-Fi & BLE](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| SoftAP 发信标 + BLE | Y | [ESP-IDF coexist.rst 表 Wi-Fi & BLE](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| SoftAP 有设备连接中/已连接 + BLE；Sniffer + BLE | C1（支持但不稳定） | [ESP-IDF coexist.rst 表 Wi-Fi & BLE](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| ESP-NOW 接收 + BLE | S（仅 STA 模式下稳定） | [ESP-IDF coexist.rst 表 Wi-Fi & BLE](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| C6：Wi-Fi + Thread/Zigbee Router | STA 下 C1；SoftAP 下 X（不支持）；End Device 多数 Y | [ESP-IDF coexist.rst 表 Wi-Fi & 802.15.4](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| 必开配置 | menuconfig 打开 CONFIG_ESP_COEX_SW_COEXIST_ENABLE，否则软件共存不生效 | [ESP-IDF coexist.rst Compile-time Options](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| S3 双核 | 把 Wi-Fi 协议栈任务与蓝牙控制器/主机任务放在不同 CPU 上 | [ESP-IDF coexist.rst Compile-time Options](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| 模组放在板子中间、四周挖空 | 乐鑫明确不推荐；改为天线朝外放板边 | [HDG pcb-layout-design.rst 模组摆放](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |
| USB 口、串口排针挨着天线 | USB 口、USB 转串口芯片、UART 线（含过孔、测试点、排针）都要尽量远离天线，UART 线包地 | [HDG pcb-layout-design.rst RF](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |
| 外壳贴着天线 / 金属件靠近 | 外壳内天线四周留 ≥15 mm；做外壳时（B 线）把这块当禁区 | [HDG pcb-layout-design.rst 模组摆放](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/pcb-layout-design.rst) · S · 2026-11-01 |
| 照抄模组的匹配值 | 射频匹配参数随板子不同，乐鑫模组上的值不能直接用 | [HDG 原理图清单 RF Tuning](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 配网用 SoftAP + BLE 同时开 | SoftAP 有设备连接时与 BLE 共存不稳定（C1）；配网方式二选一 | [ESP-IDF coexist.rst 表 Wi-Fi & BLE](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| BLE Coded PHY 拖慢 Wi-Fi | 长包占用射频时间长；可在 menuconfig 限制 Coded PHY 的 TX/RX 时间（C3/S3：BT_CTRL_COEX_PHY_CODED_TX_RX_TLIM；C6：BT_LE_COEX_PHY_CODED_TX_RX_TLIM） | [ESP-IDF coexist.rst Compile-time Options](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| 共存时内存不够 | 可减 Wi-Fi 静态/动态 RX 缓冲、TX 缓冲、BA 窗口，关 CONFIG_ESP_WIFI_RX_IRAM_OPT（约省 17 KB IRAM），开蓝牙动态内存 | [ESP-IDF coexist.rst Compile-time Options](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| 开了射频没接天线 | 可能工作不稳甚至损坏射频电路 | [HDG 原理图清单 RF Tuning](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |

## 来源列表

- [HDG] ESP Hardware Design Guidelines 源文件（pcb-layout-design.rst、schematic-checklist.rst），commit a727293：https://github.com/espressif/esp-hardware-design-guidelines 。渲染版 https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html （本会话不可达）。
- [IDF] ESP-IDF RF Coexistence（docs/en/api-guides/coexist.rst），commit d445e94：https://github.com/espressif/esp-idf
- 查询日期：2026-11-01。
