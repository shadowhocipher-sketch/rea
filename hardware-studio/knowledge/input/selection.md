# 输入选型表

价格说明：立创/LCSC/JLCPCB 商品页本会话无法直接打开，价格来自 WebSearch 返回的商品页摘要快照（时间不明、快照间有出入），全部标"待核实"。

| 场景 | 推荐器件 | 价格区间（美元/个） | 取舍 | 来源 |
|---|---|---|---|---|
| 平面外壳、无机械开孔、电池供电 | ESP32-S3 片上电容触摸 + PCB 铜皮电极（8–15 mm） | 0（片上外设，只多一个 510 Ω 电阻；电阻价格未查到） | 免按键、可防水/接近感应；只有 S3 有（C3/C6 没有）；未过 CS 测试，插电产品要实测；隔外壳灵敏度要样机调 | [HDG 原理图清单 Touch Sensor](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 确定的"咔哒"手感、任何 MCU | 贴片轻触开关，例：Omron B3U-1000P（LCSC C231329） | 约 0.22（5+）/ 0.13（3500+）；另一快照 0.10 起 | 可靠、可做深睡唤醒；需要外壳开孔/按键帽；弹跳 ≤5 ms 要软件消抖 | [LCSC C231329](https://www.lcsc.com/product-detail/C231329.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| "摇一摇"、敲击、翻转 | LIS3DH（LIS3DHTR，LCSC C15134） | 1.02–1.83（1 个）/ 0.62–1.18（1000+），三个快照差别大 | 1 Hz 2 μA、硬件中断可唤醒 MCU；多一个 I2C 器件和一根中断线 | [LCSC C15134](https://www.lcsc.com/product-detail/C15134.html) · B · 2026-11-01 · 待核实（仅搜索摘要，快照差异大） |

## 依据

| 对比项 | 电容触摸（S3） | 轻触开关（B3U） | LIS3DH | 来源 |
|---|---|---|---|---|
| 睡眠时能否唤醒 | 能（浅睡/深睡），但睡眠中持续采样增加功耗 | 能（接唤醒 GPIO） | 能（INT1 接唤醒 GPIO），1 Hz 时 2 μA | [ESP-IDF cap_touch_sens.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/cap_touch_sens.rst) · A · 2026-11-01 |
| 主要风险 | 传导干扰误触、外壳厚度 | 弹跳、寿命 10–20 万次 | 阈值/量程调参、地址 0x18/0x19 | [Omron B3U](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · S（镜像）· 2026-11-01 · 待核实 |

器件页：[esp32-touch.md](esp32-touch.md)、[tactile-switch.md](tactile-switch.md)、[lis3dh.md](lis3dh.md)。
