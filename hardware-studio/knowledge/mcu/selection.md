# MCU 选型表

价格说明：立创/LCSC/JLCPCB 商品页本会话无法直接打开（代理拒绝连接），下表价格来自 WebSearch 返回的 LCSC/JLCPCB 商品页摘要快照，快照时间不明、不同快照之间有出入，所以全部标"待核实"。下单前打开链接看实时阶梯价。

| 场景 | 推荐器件 | 价格区间（美元/个） | 取舍 | 来源 |
|---|---|---|---|---|
| 有彩屏/墨水屏 + 触摸 + Wi-Fi，或要 USB 设备（键盘、U 盘、音频） | ESP32-S3 模组，如 ESP32-S3-WROOM-1-N16R8（LCSC C2913202） | 约 3.4（整盘）– 5.5（1 个），各快照不同 | 唯一带 14 路触摸和 USB OTG 的；双核、PSRAM 选项多；贵、功耗比 C 系列高（Modem-sleep 平均 40.1 mA vs C3 21.47 mA） | [LCSC C2913202](https://www.lcsc.com/product-detail/WiFi-Modules_Espressif-Systems-ESP32-S3-WROOM-1-N16R8_C2913202.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 按键 + 小屏 + Wi-Fi/BLE，成本优先 | ESP32-C3 模组，如 ESP32-C3-MINI-1-N4（LCSC C2838502） | 3.06（1 个）/ 2.14（100+）/ 2.01（1300+） | 最便宜；深睡 4.8 μA 最低；无触摸、无 OTG、GPIO 只有 22 个（深睡唤醒只能用 GPIO0–5） | [LCSC C2838502](https://www.lcsc.com/product-detail/RF-Modules_Espressif-Systems-ESP32-C3-MINI-1-N4_C2838502.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 要接 Matter-over-Thread / Zigbee，或 Wi-Fi 6 省电 | ESP32-C6 模组，如 ESP32-C6-MINI-1-N4（LCSC C5736265） | 3.92（1 个）– 2.83（1300+）；摘要显示当时缺货 | 唯一带 802.15.4；Wi-Fi 浅睡电流最低（DTIM10 0.172 mA）；无触摸、无 OTG；做 Wi-Fi + Thread 网关要双芯片 | [LCSC C5736265](https://www.lcsc.com/product-detail/C5736265.html) · B · 2026-11-01 · 待核实（仅搜索摘要，缺货） |
| 原型阶段 | 对应芯片的官方开发板（DevKitC / DevKitM） | 未查到 | 先用开发板验证功能和功耗，再换模组上板 | https://www.lcsc.com/ · 未查到（本会话未搜索开发板价格） |

## 依据（参数对比，均出自各器件页）

| 对比项 | ESP32-S3 | ESP32-C3 | ESP32-C6 | 来源 |
|---|---|---|---|---|
| 深睡平均电流（乐鑫实测） | 6.8 μA | 4.8 μA | 6.7 μA | [ESP-IDF sleep-current](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current) · A · 2026-11-01 |
| Wi-Fi Auto Light-sleep，DTIM3 | 1.33 mA | 0.62 mA | 0.368 mA | [ESP-IDF sleep-current](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current) · A · 2026-11-01 |
| 电容触摸 | 14 路 | 无 | 无 | [ESP-IDF soc_caps.h](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc) · A · 2026-11-01 |
| USB | OTG + Serial/JTAG | Serial/JTAG | Serial/JTAG | [HDG 原理图清单 USB](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 物理 GPIO | 45 | 22 | 31（合封 flash 型号 22） | [ESP-IDF gpio 文档](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio) · A · 2026-11-01 |

器件页：[esp32-s3.md](esp32-s3.md)、[esp32-c3.md](esp32-c3.md)、[esp32-c6.md](esp32-c6.md)。
