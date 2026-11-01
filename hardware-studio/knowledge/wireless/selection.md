# 无线选型表（ESP32 系列）

价格说明：立创/LCSC/JLCPCB 商品页本会话无法直接打开，价格来自 WebSearch 返回的商品页摘要快照（时间不明、快照间有出入），全部标"待核实"；带外接天线座的 "U" 版本价格本次没有拿到。

| 场景 | 推荐 | 价格区间（美元/个） | 取舍 | 来源 |
|---|---|---|---|---|
| 塑料外壳、天线能放板边、不想调射频 | 板载 PCB 天线模组（如 ESP32-C3-MINI-1-N4，LCSC C2838502） | 3.06（1 个）/ 2.01（1300+） | 不用自己做射频匹配；要求天线伸出板边或挖空、外壳内四周 ≥15 mm 净空 | [LCSC C2838502](https://www.lcsc.com/product-detail/RF-Modules_Espressif-Systems-ESP32-C3-MINI-1-N4_C2838502.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 金属外壳、天线位置受限 | "U" 版本模组（IPEX 外接天线），如 ESP32-C3-MINI-1U-N4（LCSC C2911374）、ESP32-C6-MINI-1U-N4（C7558096） | 未查到（搜索摘要无价格） | 天线可引到外壳外；多一根天线和 IPEX 座成本；IPEX 座下方所有层净空 | https://www.lcsc.com/product-detail/C2911374.html · 未查到 |
| 只要 BLE、最省电（广播/连接间隙浅睡） | ESP32-C6 + 外接 32 kHz 晶振 | 模组 3.92（1 个）/ 2.83（1300+），摘要显示缺货 | 例程浅睡 34 μA（C3 140 μA、S3 230 μA）；不接 32 kHz 晶振则 3.3 mA | [LCSC C5736265](https://www.lcsc.com/product-detail/C5736265.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 一直保持 Wi-Fi 连接、电池供电 | ESP32-C6（Auto Light-sleep DTIM10 0.172 mA）或 C3（0.31 mA） | 同 MCU 选型表 | S3 同条件 0.93 mA，耗电约为 C3 的 3 倍、C6 的 5.4 倍；路由器 DTIM 设置影响很大 | [ESP-IDF sleep-current](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/sleep-current) · A · 2026-11-01 |
| Wi-Fi + BLE 同时用（BLE 配网后 STA 联网） | 任一款（S3/C3/C6），STA + BLE 组合共存稳定 | 同 MCU 选型表 | 避免 SoftAP 已连接 + BLE（不稳定）；S3 把两套协议栈分到两个核 | [ESP-IDF coexist.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 |
| Wi-Fi 网关 + Thread/Zigbee 路由 | 双芯片（乐鑫举例 ESP32-S3 + ESP32-H2），各自天线 | 未查到（H2 本次未查） | 单芯片 C6 的 Wi-Fi + Router 共存不稳定/不支持 | [ESP-IDF coexist.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-guides/coexist.rst) · A · 2026-11-01 · 未查到（H2 价格） |

器件页：[esp32-wifi-ble-power.md](esp32-wifi-ble-power.md)、[esp32-antenna-coexistence.md](esp32-antenna-coexistence.md)；芯片细节见 [../mcu/](../mcu/selection.md)。
