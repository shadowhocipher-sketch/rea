# 成本表：bom.csv

币种 CNY；损耗率 2.0%（加工费行不计损耗）。"实查" = B 级来源的阶梯价；"待核实" = 只有搜索摘要；"估算" = 推算或假设，依据见价格缓存。

## 汇总

| 数量 | 总价 | 单台 | 其中一次性费用 | 实查 | 待核实 | 估算 | 缺价格行 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 12032.82 | 120.3282 | 125.48 | 23.9% | 58.3% | 17.8% | 0 |
| 1000 | 115425.15 | 115.4252 | 125.48 | 22.8% | 59.8% | 17.4% | 0 |

## 按类别（单台）

| 数量 | 电子件 | 结构件 | 外购模块 | 包装 | 加工费 |
|---:|---:|---:|---:|---:|---:|
| 100 | 28.7563 | 26.4499 | 51.2665 | 3.4593 | 10.3962 |
| 1000 | 26.3701 | 26.4462 | 51.2665 | 2.0756 | 9.2668 |

## 明细：100 台

| 位号 | 名称 | 类别 | 计费 | 需求量 | 采购量 | 单价 | 小计 | 单台 | 状态 | 来源 | 备注 |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| U1 | 主控模组（射频不开启） | 电子件 | unit | 102 | 102 | 15.4989 | 1580.89 | 15.8089 | 实查 | [链接](https://jlcpcb.com/partdetail/C41349510) 2026-11-01 | knowledge/mcu/esp32-c3.md |
| U2 | 三轴加速度计（摇一摇） | 电子件 | unit | 102 | 102 | 8.9948 | 917.47 | 9.1747 | 实查 | [链接](https://jlcpcb.com/partdetail/C15134) 2026-11-01 | knowledge/input/lis3dh.md |
| U3 | 锂电线性充电 130 mA | 电子件 | unit | 102 | 102 | 0.9984 | 101.84 | 1.0184 | 实查 | [链接](https://jlcpcb.com/partdetail/C16581) 2026-11-01 | Preferred 料免换料费；knowledge/power/tp4056.md |
| U4 | 3.3V LDO（静态 1 μA） | 电子件 | unit | 102 | 102 | 0.8011 | 81.71 | 0.8171 | 实查 | [链接](https://jlcpcb.com/partdetail/C5446) 2026-11-01 | knowledge/power/xc6206.md |
| J1 | USB-C 16P 受电插座 | 电子件 | unit | 102 | 102 | 1.0032 | 102.33 | 1.0233 | 实查 | [链接](https://jlcpcb.com/partdetail/C165948) 2026-11-01 | knowledge/power/usb-c-sink.md |
| R1,R2 | CC 下拉 5.1k | 电子件 | unit | 204 | 204 | 0.0163 | 3.32 | 0.0332 | 实查 | [链接](https://jlcpcb.com/partdetail/C25905) 2026-11-01 |  |
| R3-R8 | 10k（RPROG、CS/RST 上拉、I2C 上拉、EN 上拉） | 电子件 | unit | 612 | 612 | 0.0224 | 13.70 | 0.1370 | 实查 | [链接](https://jlcpcb.com/partdetail/C25744) 2026-11-01 |  |
| C1-C4 | 100nF 去耦 | 电子件 | unit | 408 | 408 | 0.0292 | 11.90 | 0.1190 | 实查 | [链接](https://jlcpcb.com/partdetail/C1525) 2026-11-01 |  |
| C5-C7 | 1uF（LDO 输入/输出、EN RC） | 电子件 | unit | 306 | 306 | 0.0549 | 16.81 | 0.1681 | 实查 | [链接](https://jlcpcb.com/partdetail/C52923) 2026-11-01 |  |
| C8-C10 | 10uF（VBUS、BAT、3V3） | 电子件 | unit | 306 | 306 | 0.1492 | 45.66 | 0.4566 | 实查 | [链接](https://jlcpcb.com/partdetail/C19702) 2026-11-01 |  |
| DS1 | 1.54 寸墨水屏模块 200x200 | 外购模块 | unit | 102 | 102 | 37.3059 | 3805.21 | 38.0521 | 待核实 | [链接](https://www.lcsc.com/product-detail/C5374685.html) 2026-11-01 | 手工焊 8 根线；价格待核实 |
| BAT1 | 402030 锂聚合物电芯 200mAh（带 PCM） | 外购模块 | unit | 102 | 102 | 12.9553 | 1321.44 | 13.2144 | 估算 | [链接](https://www.ebay.de/itm/121857264843) 2026-11-01 | 估算价；手工焊引线 |
| PCB1 | PCB 2 层 46x30mm | 加工费 | unit | 102 | 102 | 2.7132 | 276.74 | 2.7674 | 待核实 | [链接](https://jlcpcb.com/blog/free-assembly-for-1-6-layer-pcbs-and-discounts-on-8-20-layer-pcba) 2026-11-01 | 按打样价折算（偏高） |
| SMT1 | 贴片工程费 | 加工费 | batch | 1 | 1 | 54.2632 | 54.26 | 0.5426 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 | 每批一次 |
| SMT2 | 钢网 | 加工费 | batch | 1 | 1 | 10.1744 | 10.17 | 0.1017 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 | 每批一次 |
| SMT3 | 贴片焊点费 | 加工费 | per_joint | 14100 | 14100 | 0.0115 | 162.59 | 1.6259 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-price) 2026-11-01 | 每台焊点 141；单面贴片 |
| SMT4 | 扩展库换料费 | 加工费 | per_extended_type | 3 | 3 | 20.3487 | 61.05 | 0.6105 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 | 扩展料 3 种；每种扩展料每批一次 |
| ENC1 | 外壳 MJF PA12（克） | 结构件 | unit | 1417.8 | 1418 | 1.8653 | 2644.99 | 26.4499 | 待核实 | [链接](https://jlc3dp.com/blog/drastic-material-price-cuts-and-adjusted-post-processing-service-fees) 2026-11-01 | 第 5 步体积 13735 mm³ × 1.01 g/cm³（估算）；只含材料费 |
| ASM1 | 整机组装人工（分钟） | 加工费 | unit | 1000 | 1000 | 0.4748 | 474.80 | 4.7480 | 估算 | 2026-11-01 | 假设：焊屏 8 线 + 焊电池 + 合壳 + 摇一摇测试 共 10 分钟 |
| PKG1 | 基础包装 | 包装 | unit | 102 | 102 | 3.3914 | 345.93 | 3.4593 | 估算 | 2026-11-01 |  |

## 明细：1000 台

| 位号 | 名称 | 类别 | 计费 | 需求量 | 采购量 | 单价 | 小计 | 单台 | 状态 | 来源 | 备注 |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| U1 | 主控模组（射频不开启） | 电子件 | unit | 1020 | 1020 | 14.7535 | 15048.56 | 15.0486 | 实查 | [链接](https://jlcpcb.com/partdetail/C41349510) 2026-11-01 | knowledge/mcu/esp32-c3.md |
| U2 | 三轴加速度计（摇一摇） | 电子件 | unit | 1020 | 1020 | 8.3165 | 8482.84 | 8.4828 | 实查 | [链接](https://jlcpcb.com/partdetail/C15134) 2026-11-01 | knowledge/input/lis3dh.md |
| U3 | 锂电线性充电 130 mA | 电子件 | unit | 1020 | 1020 | 0.7563 | 771.42 | 0.7714 | 实查 | [链接](https://jlcpcb.com/partdetail/C16581) 2026-11-01 | Preferred 料免换料费；knowledge/power/tp4056.md |
| U4 | 3.3V LDO（静态 1 μA） | 电子件 | unit | 1020 | 1020 | 0.6376 | 650.34 | 0.6503 | 实查 | [链接](https://jlcpcb.com/partdetail/C5446) 2026-11-01 | knowledge/power/xc6206.md |
| J1 | USB-C 16P 受电插座 | 电子件 | unit | 1020 | 1020 | 0.7075 | 721.61 | 0.7216 | 实查 | [链接](https://jlcpcb.com/partdetail/C165948) 2026-11-01 | knowledge/power/usb-c-sink.md |
| R1,R2 | CC 下拉 5.1k | 电子件 | unit | 2040 | 2040 | 0.0129 | 26.29 | 0.0263 | 实查 | [链接](https://jlcpcb.com/partdetail/C25905) 2026-11-01 |  |
| R3-R8 | 10k（RPROG、CS/RST 上拉、I2C 上拉、EN 上拉） | 电子件 | unit | 6120 | 6120 | 0.0149 | 91.32 | 0.0913 | 实查 | [链接](https://jlcpcb.com/partdetail/C25744) 2026-11-01 |  |
| C1-C4 | 100nF 去耦 | 电子件 | unit | 4080 | 4080 | 0.0190 | 77.49 | 0.0775 | 实查 | [链接](https://jlcpcb.com/partdetail/C1525) 2026-11-01 |  |
| C5-C7 | 1uF（LDO 输入/输出、EN RC） | 电子件 | unit | 3060 | 3060 | 0.0373 | 114.16 | 0.1142 | 实查 | [链接](https://jlcpcb.com/partdetail/C52923) 2026-11-01 |  |
| C8-C10 | 10uF（VBUS、BAT、3V3） | 电子件 | unit | 3060 | 3060 | 0.1262 | 386.06 | 0.3861 | 实查 | [链接](https://jlcpcb.com/partdetail/C19702) 2026-11-01 |  |
| DS1 | 1.54 寸墨水屏模块 200x200 | 外购模块 | unit | 1020 | 1020 | 37.3059 | 38052.07 | 38.0521 | 待核实 | [链接](https://www.lcsc.com/product-detail/C5374685.html) 2026-11-01 | 手工焊 8 根线；价格待核实 |
| BAT1 | 402030 锂聚合物电芯 200mAh（带 PCM） | 外购模块 | unit | 1020 | 1020 | 12.9553 | 13214.45 | 13.2144 | 估算 | [链接](https://www.ebay.de/itm/121857264843) 2026-11-01 | 估算价；手工焊引线 |
| PCB1 | PCB 2 层 46x30mm | 加工费 | unit | 1020 | 1020 | 2.7132 | 2767.42 | 2.7674 | 待核实 | [链接](https://jlcpcb.com/blog/free-assembly-for-1-6-layer-pcbs-and-discounts-on-8-20-layer-pcba) 2026-11-01 | 按打样价折算（偏高） |
| SMT1 | 贴片工程费 | 加工费 | batch | 1 | 1 | 54.2632 | 54.26 | 0.0543 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 | 每批一次 |
| SMT2 | 钢网 | 加工费 | batch | 1 | 1 | 10.1744 | 10.17 | 0.0102 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 | 每批一次 |
| SMT3 | 贴片焊点费 | 加工费 | per_joint | 141000 | 141000 | 0.0115 | 1625.86 | 1.6259 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-price) 2026-11-01 | 每台焊点 141；单面贴片 |
| SMT4 | 扩展库换料费 | 加工费 | per_extended_type | 3 | 3 | 20.3487 | 61.05 | 0.0610 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 | 扩展料 3 种；每种扩展料每批一次 |
| ENC1 | 外壳 MJF PA12（克） | 结构件 | unit | 14178 | 14178 | 1.8653 | 26446.19 | 26.4462 | 待核实 | [链接](https://jlc3dp.com/blog/drastic-material-price-cuts-and-adjusted-post-processing-service-fees) 2026-11-01 | 第 5 步体积 13735 mm³ × 1.01 g/cm³（估算）；只含材料费 |
| ASM1 | 整机组装人工（分钟） | 加工费 | unit | 10000 | 10000 | 0.4748 | 4748.03 | 4.7480 | 估算 | 2026-11-01 | 假设：焊屏 8 线 + 焊电池 + 合壳 + 摇一摇测试 共 10 分钟 |
| PKG1 | 基础包装 | 包装 | unit | 1020 | 1020 | 2.0349 | 2075.57 | 2.0756 | 估算 | 2026-11-01 |  |
