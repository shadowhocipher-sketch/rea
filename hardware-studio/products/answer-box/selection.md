# 选型：answer-box

第 2 步产出。每一行一个功能块，"知识库页"指向 `knowledge/`。价格是 `mfg/prices/` 里的条目（单位 USD，查询 2026-11-01；
"实查"= JLCPCB 元件库经 jlcparts 镜像，快照 2026-10-31；"待核实"= 只有搜索摘要；"估算"= 推算/假设）。
网络限制：本会话只能访问 GitHub 和搜索；lcsc.com / jlcpcb.com / waveshare.com / eemb.com 等打不开（见 REPORT）。

| 功能 | 选型 | 知识库页 | 价格区间 | 取舍 / 为什么 | 来源 |
|---|---|---|---|---|---|
| 主控 | ESP32-C3-MINI-1-H4X 模组（LCSC C41349510），**射频不开启** | knowledge/mcu/esp32-c3.md | $2.97（1）/ $2.29（100+）/ $2.12（1300+）· 实查 | 库里最便宜的 MCU 选项、深睡 4.8 μA 最低、GPIO0–5 可深睡唤醒、MicroPython + 模拟器能跑；不需要无线却带射频是浪费（约占 BOM 13%），换无射频 MCU 要先补知识库页（本次没做，见 REPORT） | [JLCPCB C41349510](https://jlcpcb.com/partdetail/C41349510) · B（镜像）· 2026-11-01 |
| 屏 | 1.54 寸 200×200 黑白墨水屏模块（SSD1681 类，Waveshare，LCSC C5374685） | knowledge/display/ssd1680-ssd1681.md | $8.05（1）/ $6.85（10+）/ $5.50（100+）· 待核实（摘要显示缺货） | 断电保持画面、深睡约 1 μA（控制器），"像纸一样"；全刷约 2 s 会闪、局刷约 0.26 s（模拟器默认值，待核实）；模块是最贵的一项，1000 台应改裸屏 + 板上升压电路 | [LCSC C5374685](https://www.lcsc.com/product-detail/C5374685.html) · B · 2026-11-01 · 待核实 |
| 摇一摇 | LIS3DHTR（LCSC C15134），I2C 0x18，INT1 → GPIO3 | knowledge/input/lis3dh.md | $1.89（1）/ $1.33（100+）/ $1.23（1000+）· 实查 | 50 Hz 低功耗 6 μA；运动中断硬件判"摇"、唤醒 MCU，MCU 可以一直深睡；阈值 1.6 g（不开高通时必须 > 1 g），真机要调 | [JLCPCB C15134](https://jlcpcb.com/partdetail/C15134) · B（镜像）· 2026-11-01 |
| 电池 | 402030 锂聚合物软包 3.7 V 约 200 mAh，带保护板（PCM） | 无（只有 C 级来源，留在产品目录，见下方包络表） | 估算 $1.91/只（C 级零售价最低值） | 30×20×4 mm 塞得进 70×50×18 的口袋尺寸；买带 PCM 的成品电芯，省掉板上 DW01 + 8205（保护参数随电芯厂而定，要规格书）；容量各卖家标称不一致 | [eBay 4 只装 402030](https://www.ebay.de/itm/121857264843) · C · 2026-11-01 · 估算 |
| 充电 | TP4056-42-ESOP8（TOPPOWER，LCSC C16581），RPROG = 10 kΩ → 130 mA | knowledge/power/tp4056.md | $0.186（1）/ $0.128（150+）/ $0.112（500+）· 实查 | 外围最少；130 mA ≈ 0.65 C 对 200 mAh 电芯（推论，按 RPROG 对照表）；Preferred 料免换料费；TEMP 接地关闭温度检测 | [JLCPCB C16581](https://jlcpcb.com/partdetail/C16581) · B（镜像）· 2026-11-01 |
| 保护 | 电芯自带 PCM；备选板上 DW01A（C351410）+ FS8205A（C908265） | knowledge/power/dw01-protection.md | 备选合计约 $0.07（1000 档）· 实查 | DW01 典型应用的 R1/C1/R2 取值库里"未查到"，自己画保护电路缺数据，所以第一版用带 PCM 的电芯 | [JLCPCB C351410](https://jlcpcb.com/partdetail/C351410) · B（镜像）· 2026-11-01 |
| 稳压 | XC6206P332MR-G（Torex，LCSC C5446） | knowledge/power/xc6206.md | $0.144（1）/ $0.094（500+）· 实查 | 静态 1 μA，深睡为主且不开 Wi-Fi，负载 ≤ 200 mA 够（knowledge/power/selection.md 的"深睡为主"场景）；压差 250 mV@100 mA：电池低于约 3.55 V 后 3V3 跟着降（C3 下限 3.0 V） | [JLCPCB C5446](https://jlcpcb.com/partdetail/C5446) · B（镜像）· 2026-11-01 |
| 充电口 | TYPE-C-31-M-12（LCSC C165948）+ CC1、CC2 各 5.1 kΩ（C25905） | knowledge/power/usb-c-sink.md | 插座 $0.187（1）/ $0.104（1000+）· 实查 | 只取 5 V，不做 PD；D+/D− 接 GPIO19/18 当 USB 烧录口 | [JLCPCB C165948](https://jlcpcb.com/partdetail/C165948) · B（镜像）· 2026-11-01 |
| 阻容 | 0402 10k ×6、5.1k ×2、100 nF ×4、1 µF ×3；0603 10 µF ×3 | knowledge/power/selection.md | 合计 < $0.1 · 实查 | GPIO8（EPD CS）、GPIO2（EPD RST）是 strapping 脚，各加 10k 上拉保证启动电平（knowledge/mcu/esp32-c3.md） | [JLCPCB C25744](https://jlcpcb.com/partdetail/C25744) · B（镜像）· 2026-11-01 |

## 引脚分配（pins.csv 的依据）

| 信号 | GPIO | 为什么 | 来源 |
|---|---|---|---|
| LIS3DH INT1 | GPIO3 | C3 只有 GPIO0–5 能唤醒深睡 | [ESP-IDF gpio/esp32c3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c3.inc) · A · 2026-11-01 |
| I2C SDA / SCL | GPIO1 / GPIO4 | 避开 strapping（2/8/9）、flash（12–17）、USB（18/19）、UART0（20/21，保留做备用下载） | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| EPD SCK / MOSI / DC / BUSY | GPIO6 / 7 / 10 / 5 | 同上 | 同上 · S · 2026-11-01 |
| EPD CS | GPIO8 + 10k 上拉 | GPIO8 下载模式要为 1；CS 空闲本来就是高电平，上拉同时满足两者（推论） | [HDG esp32c3-chip-boot-mode-control.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32c3/esp32c3-chip-boot-mode-control.inc) · S · 2026-11-01 |
| EPD RST | GPIO2 + 10k 上拉 | GPIO2 建议上拉；RST 低有效，上拉保持不复位（推论）；退出墨水屏深睡必须硬件复位，所以 RST 必须接 GPIO | [SSD1680 Rev0.14 命令 10h](https://github.com/CursedHardware/epd-driver-ic/blob/8c147a71ff451da3b16450162559cb0ccd8bdaec/SSD1680.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 元器件包络（给第 5 步外壳用）

| 零件 | 外形 长×宽×高 mm | 来源（数据手册 / 卖家页 / 实测 / 估算） |
|---|---|---|
| 墨水屏模块 | 48 × 33 × 3.0 | 长宽：[Waveshare 产品页](https://www.waveshare.com/1.54inch-e-paper-module-b.htm) · B · 2026-11-01 · 待核实（仅摘要）；厚 3.0 **估算**（裸屏 1.05 + 转接板 1.6 + 余量，按焊线不装排针；带 2.54 排针会厚得多） |
| 墨水屏可视区 | 27.6 × 27.6，按居中处理 | 同上 · B · 待核实；可视区在模块上是否居中**未查到**，首件对位 |
| PCB | 46 × 30 × 1.0 | **估算**：放得下 C3 模组 + 充电 + 加速度计 + USB-C，1.0 mm 板厚为假设 |
| C3 模组 | 16.6 × 13.2 × 3.0 | 长宽：[JLCPCB C41349510 描述](https://jlcpcb.com/partdetail/C41349510) · B（镜像）；高 3.0 **估算**（模组数据手册未查到） |
| LIS3DH | 3 × 3 × 1.0 | **估算**（按封装名 LGA-16 3×3；高度数据手册机械图未读） |
| TP4056 | 5 × 4 × 1.6 | **估算**（ESOP-8 包络） |
| USB-C 插座 / 插头外壳 | 8.94 × 3.26 × 7.35 / 12.4 × 6.5 × 20 | 库默认值（`cad/README.md`，**估算**），换成 C165948 规格书和实测线 |
| 电芯 402030 | 30 × 20 × 4.0（+10% 膨胀） | [Ampul 402030 页](https://www.ampul.eu/en/battery/5084-li-pol-battery-200mah-37v-402030-3-wires) · C · 2026-11-01 · 待核实；膨胀 10% 估算（cad/DFM.md BAT-1） |

## 这次补进知识库的页面

- `knowledge/input/lis3dh.md`：新增"寄存器位（摇一摇中断配置用）"一节（CTRL_REG1–6、INT1_CFG/SRC/THS/DURATION、OUT 寄存器，数据手册表 29–61）。
- `knowledge/display/ssd1680-ssd1681.md`："面板 / 模块参数"新增 1.54 寸模块外形 48×33、裸面板 31.8×37.3×1.05、可视区 27.6×27.6（B 级，仅摘要，待核实）。
- 电芯没有新建器件页：只有 C 级来源（按 component-knowledge 规则不能单独作为事实），留在本页。
