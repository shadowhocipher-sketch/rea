# 显示选型表

价格说明：立创/LCSC/JLCPCB 商品页本会话无法直接打开，下表价格来自 WebSearch 返回的商品页摘要快照（时间不明，快照间有出入），全部标"待核实"；下单前打开链接核对。

| 场景 | 推荐器件 | 价格区间（美元/个） | 取舍 | 来源 |
|---|---|---|---|---|
| 小字、图标、低成本，一直亮着也行 | SSD1306（或兼容的 SSD1315）0.96 寸 128×64 OLED 模块，例：HS96L03W2C03（LCSC C5248080，SSD1315） | 约 1.43（该型号）；立创类目摘要写 0.96 寸 SSD1306 模块 1.50–3.00 | 便宜、I2C 两根线、驱动现成；单色、小；睡眠 ≤10 μA 但亮屏要持续供电 | [LCSC C5248080](https://www.lcsc.com/product-detail/C5248080.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 彩色表情、动画、图标 | ST7789 SPI 彩屏模块：1.14 寸 240×135 或 2 寸 320×240（如 HS20HS072RX） | 1.14 寸约 1.91（1 个）；2 寸约 2.22 | 色彩和刷新快；控制器 6 mA + 背光（背光电流未查到），不适合常亮电池产品；1.54 寸 240×240 在立创未搜到 | [JLCPCB LCD 分类](https://jlcpcb.com/parts/2nd/Displays/LCD_Screen_2206) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 电池供电、画面长时间不变（价签、答案机、日历） | SSD1681 1.54 寸 200×200 或 SSD1680 2.13/2.9 寸墨水屏模块，例：Waveshare 1.54inch e-Paper（LCSC C5374685） | 8.05（1 个）/ 6.85（10+）/ 5.50（100+）；摘要同时显示缺货 | 断电保持画面、深睡约 1 μA；全刷约 2.6–3.2 s 会闪（GxEPD2 常量，待核实），不适合动画；价格最高 | [LCSC C5374685](https://www.lcsc.com/product-detail/C5374685.html) · B · 2026-11-01 · 待核实（仅搜索摘要，缺货） |

## 依据（参数对比，均出自各器件页）

| 对比项 | SSD1306 | ST7789V | SSD1680 / SSD1681 | 来源 |
|---|---|---|---|---|
| 逻辑电源 | VDD 1.65–3.3 V | VDDI 1.65–3.3 V、VDD 2.4–3.3 V | VCI 2.2–3.7 V | [ssd1306.md](https://github.com/libdriver/ssd1306/blob/0bcc8ce229608353ac699ea56bfce104318ce962/datasheet/ssd1306_datasheet.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 最低功耗状态 | 睡眠 ≤10 μA（IDD）+ ≤10 μA（ICC） | Sleep-in IDD 典型 15 μA（不含背光） | 深睡 Mode 1 典型 1 μA | [st7789.md](https://github.com/libdriver/st7789/blob/7bd8bc794bea273b934fffac4a73133ee0eb7ebf/datasheet/st7789_datasheet.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 最高接口速率（写） | I2C 400 kHz / SPI 10 MHz | SPI 写周期 ≥66 ns（≈15 MHz） | SPI 写 20 MHz | [ssd1680-ssd1681.md](https://github.com/CursedHardware/epd-driver-ic/blob/8c147a71ff451da3b16450162559cb0ccd8bdaec/SSD1680.pdf) · S（镜像）· 2026-11-01 · 待核实 |

器件页：[ssd1306.md](ssd1306.md)、[st7789.md](st7789.md)、[ssd1680-ssd1681.md](ssd1680-ssd1681.md)。
