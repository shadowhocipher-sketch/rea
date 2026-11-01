# 成本表：route-b-module.bom.csv

币种 USD；损耗率 2.0%（加工费行不计损耗）。"实查" = B 级来源的阶梯价；"待核实" = 只有搜索摘要；"估算" = 推算或假设，依据见价格缓存。

## 汇总

| 数量 | 总价 | 单台 | 其中一次性费用 | 实查 | 待核实 | 估算 | 缺价格行 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 161.70 | 16.1700 | 18.50 | 2.8% | 75.5% | 21.7% | 0 |
| 100 | 1344.00 | 13.4400 | 18.50 | 2.5% | 75.2% | 22.3% | 0 |
| 1000 | 12534.79 | 12.5348 | 18.50 | 2.1% | 79.3% | 18.6% | 0 |

## 按类别（单台）

| 数量 | 电子件 | 结构件 | 外购模块 | 包装 | 加工费 |
|---:|---:|---:|---:|---:|---:|
| 10 | 6.0754 | 4.2075 | 2.6070 | 0.5500 | 2.7301 |
| 100 | 5.5576 | 4.2075 | 2.1318 | 0.5100 | 1.0331 |
| 1000 | 5.4819 | 4.2075 | 1.6728 | 0.3060 | 0.8666 |

## 明细：10 台

| 位号 | 名称 | 类别 | 计费 | 需求量 | 采购量 | 单价 | 小计 | 单台 | 状态 | 来源 | 备注 |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| U1 | Wi-Fi/BLE 模组 | 电子件 | unit | 10.2 | 11 | 5.1160 | 56.28 | 5.6276 | 待核实 | [链接](https://www.lcsc.com/product-detail/C2913202.html) 2026-11-01 | 路线 B：模组 + 自画底板；价格待核实 |
| U4 | 3.3V LDO | 电子件 | unit | 10.2 | 11 | 0.0617 | 0.68 | 0.0679 | 实查 | [链接](https://jlcpcb.com/partdetail/C82942) 2026-11-01 |  |
| J1 | USB-C 16P 插座 | 电子件 | unit | 10.2 | 11 | 0.1872 | 2.06 | 0.2059 | 实查 | [链接](https://jlcpcb.com/partdetail/C165948) 2026-11-01 |  |
| R1,R2 | CC 下拉 5.1k | 电子件 | unit | 20.4 | 21 | 0.0024 | 0.05 | 0.0050 | 实查 | [链接](https://jlcpcb.com/partdetail/C25905) 2026-11-01 |  |
| R3-R4 | 10k 电阻 | 电子件 | unit | 20.4 | 21 | 0.0033 | 0.07 | 0.0069 | 实查 | [链接](https://jlcpcb.com/partdetail/C25744) 2026-11-01 | EN 上拉、GPIO0 上拉 |
| C1-C4 | 100nF 去耦 | 电子件 | unit | 40.8 | 41 | 0.0043 | 0.18 | 0.0176 | 实查 | [链接](https://jlcpcb.com/partdetail/C1525) 2026-11-01 |  |
| C5-C7 | 10uF | 电子件 | unit | 30.6 | 31 | 0.0297 | 0.92 | 0.0921 | 实查 | [链接](https://jlcpcb.com/partdetail/C19702) 2026-11-01 |  |
| C8 | 1uF（EN 延时） | 电子件 | unit | 10.2 | 11 | 0.0081 | 0.09 | 0.0089 | 实查 | [链接](https://jlcpcb.com/partdetail/C52923) 2026-11-01 |  |
| SW1,SW2 | 轻触按键（BOOT/RST） | 电子件 | unit | 20.4 | 21 | 0.0207 | 0.43 | 0.0435 | 实查 | [链接](https://jlcpcb.com/partdetail/C318884) 2026-11-01 |  |
| DS1 | 0.96 寸 OLED 模块 | 外购模块 | unit | 10.2 | 11 | 2.3700 | 26.07 | 2.6070 | 估算 | [链接](https://jlcpcb.com/partdetail/C18723026) 2026-11-01 |  |
| PCB1 | PCB 2 层 | 加工费 | unit | 10.2 | 11 | 0.4000 | 4.40 | 0.4400 | 待核实 | [链接](https://jlcpcb.com/blog/free-assembly-for-1-6-layer-pcbs-and-discounts-on-8-20-layer-pcba) 2026-11-01 | 按打样价折算（偏高） |
| SMT1 | 贴片工程费 | 加工费 | batch | 1 | 1 | 8.0000 | 8.00 | 0.8000 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 |  |
| SMT2 | 钢网 | 加工费 | batch | 1 | 1 | 1.5000 | 1.50 | 0.1500 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 |  |
| SMT3 | 贴片焊点费 | 加工费 | per_joint | 530 | 530 | 0.0017 | 0.90 | 0.0901 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-price) 2026-11-01 | 每台焊点 53 |
| SMT4 | 扩展库换料费 | 加工费 | per_extended_type | 3 | 3 | 3.0000 | 9.00 | 0.9000 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 | 扩展料 3 种 |
| ENC1 | 外壳 MJF PA12（克） | 结构件 | unit | 153 | 153 | 0.2750 | 42.08 | 4.2075 | 待核实 | [链接](https://jlc3dp.com/blog/drastic-material-price-cuts-and-adjusted-post-processing-service-fees) 2026-11-01 | 示例假设 15 g |
| ASM1 | 整机组装人工（分钟） | 加工费 | unit | 50 | 50 | 0.0700 | 3.50 | 0.3500 | 估算 | 2026-11-01 | 示例假设每台 5 分钟 |
| PKG1 | 基础包装 | 包装 | unit | 10.2 | 11 | 0.5000 | 5.50 | 0.5500 | 估算 | 2026-11-01 |  |

警告：

- SMT3: 这些行焊点数未知，没有计入：U1

## 明细：100 台

| 位号 | 名称 | 类别 | 计费 | 需求量 | 采购量 | 单价 | 小计 | 单台 | 状态 | 来源 | 备注 |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| U1 | Wi-Fi/BLE 模组 | 电子件 | unit | 102 | 102 | 5.1160 | 521.83 | 5.2183 | 待核实 | [链接](https://www.lcsc.com/product-detail/C2913202.html) 2026-11-01 | 路线 B：模组 + 自画底板；价格待核实 |
| U4 | 3.3V LDO | 电子件 | unit | 102 | 102 | 0.0500 | 5.10 | 0.0510 | 实查 | [链接](https://jlcpcb.com/partdetail/C82942) 2026-11-01 |  |
| J1 | USB-C 16P 插座 | 电子件 | unit | 102 | 102 | 0.1479 | 15.09 | 0.1509 | 实查 | [链接](https://jlcpcb.com/partdetail/C165948) 2026-11-01 |  |
| R1,R2 | CC 下拉 5.1k | 电子件 | unit | 204 | 204 | 0.0024 | 0.49 | 0.0049 | 实查 | [链接](https://jlcpcb.com/partdetail/C25905) 2026-11-01 |  |
| R3-R4 | 10k 电阻 | 电子件 | unit | 204 | 204 | 0.0033 | 0.67 | 0.0067 | 实查 | [链接](https://jlcpcb.com/partdetail/C25744) 2026-11-01 | EN 上拉、GPIO0 上拉 |
| C1-C4 | 100nF 去耦 | 电子件 | unit | 408 | 408 | 0.0043 | 1.75 | 0.0175 | 实查 | [链接](https://jlcpcb.com/partdetail/C1525) 2026-11-01 |  |
| C5-C7 | 10uF | 电子件 | unit | 306 | 306 | 0.0220 | 6.73 | 0.0673 | 实查 | [链接](https://jlcpcb.com/partdetail/C19702) 2026-11-01 |  |
| C8 | 1uF（EN 延时） | 电子件 | unit | 102 | 102 | 0.0081 | 0.83 | 0.0083 | 实查 | [链接](https://jlcpcb.com/partdetail/C52923) 2026-11-01 |  |
| SW1,SW2 | 轻触按键（BOOT/RST） | 电子件 | unit | 204 | 204 | 0.0160 | 3.26 | 0.0326 | 实查 | [链接](https://jlcpcb.com/partdetail/C318884) 2026-11-01 |  |
| DS1 | 0.96 寸 OLED 模块 | 外购模块 | unit | 102 | 102 | 2.0900 | 213.18 | 2.1318 | 估算 | [链接](https://jlcpcb.com/partdetail/C18723026) 2026-11-01 |  |
| PCB1 | PCB 2 层 | 加工费 | unit | 102 | 102 | 0.4000 | 40.80 | 0.4080 | 待核实 | [链接](https://jlcpcb.com/blog/free-assembly-for-1-6-layer-pcbs-and-discounts-on-8-20-layer-pcba) 2026-11-01 | 按打样价折算（偏高） |
| SMT1 | 贴片工程费 | 加工费 | batch | 1 | 1 | 8.0000 | 8.00 | 0.0800 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 |  |
| SMT2 | 钢网 | 加工费 | batch | 1 | 1 | 1.5000 | 1.50 | 0.0150 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 |  |
| SMT3 | 贴片焊点费 | 加工费 | per_joint | 5300 | 5300 | 0.0017 | 9.01 | 0.0901 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-price) 2026-11-01 | 每台焊点 53 |
| SMT4 | 扩展库换料费 | 加工费 | per_extended_type | 3 | 3 | 3.0000 | 9.00 | 0.0900 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 | 扩展料 3 种 |
| ENC1 | 外壳 MJF PA12（克） | 结构件 | unit | 1530 | 1530 | 0.2750 | 420.75 | 4.2075 | 待核实 | [链接](https://jlc3dp.com/blog/drastic-material-price-cuts-and-adjusted-post-processing-service-fees) 2026-11-01 | 示例假设 15 g |
| ASM1 | 整机组装人工（分钟） | 加工费 | unit | 500 | 500 | 0.0700 | 35.00 | 0.3500 | 估算 | 2026-11-01 | 示例假设每台 5 分钟 |
| PKG1 | 基础包装 | 包装 | unit | 102 | 102 | 0.5000 | 51.00 | 0.5100 | 估算 | 2026-11-01 |  |

警告：

- SMT3: 这些行焊点数未知，没有计入：U1

## 明细：1000 台

| 位号 | 名称 | 类别 | 计费 | 需求量 | 采购量 | 单价 | 小计 | 单台 | 状态 | 来源 | 备注 |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| U1 | Wi-Fi/BLE 模组 | 电子件 | unit | 1020 | 1020 | 5.1160 | 5218.32 | 5.2183 | 待核实 | [链接](https://www.lcsc.com/product-detail/C2913202.html) 2026-11-01 | 路线 B：模组 + 自画底板；价格待核实 |
| U4 | 3.3V LDO | 电子件 | unit | 1020 | 1020 | 0.0440 | 44.88 | 0.0449 | 实查 | [链接](https://jlcpcb.com/partdetail/C82942) 2026-11-01 |  |
| J1 | USB-C 16P 插座 | 电子件 | unit | 1020 | 1020 | 0.1043 | 106.39 | 0.1064 | 实查 | [链接](https://jlcpcb.com/partdetail/C165948) 2026-11-01 |  |
| R1,R2 | CC 下拉 5.1k | 电子件 | unit | 2040 | 2040 | 0.0019 | 3.88 | 0.0039 | 实查 | [链接](https://jlcpcb.com/partdetail/C25905) 2026-11-01 |  |
| R3-R4 | 10k 电阻 | 电子件 | unit | 2040 | 2040 | 0.0026 | 5.30 | 0.0053 | 实查 | [链接](https://jlcpcb.com/partdetail/C25744) 2026-11-01 | EN 上拉、GPIO0 上拉 |
| C1-C4 | 100nF 去耦 | 电子件 | unit | 4080 | 4080 | 0.0028 | 11.42 | 0.0114 | 实查 | [链接](https://jlcpcb.com/partdetail/C1525) 2026-11-01 |  |
| C5-C7 | 10uF | 电子件 | unit | 3060 | 3060 | 0.0186 | 56.92 | 0.0569 | 实查 | [链接](https://jlcpcb.com/partdetail/C19702) 2026-11-01 |  |
| C8 | 1uF（EN 延时） | 电子件 | unit | 1020 | 1020 | 0.0063 | 6.43 | 0.0064 | 实查 | [链接](https://jlcpcb.com/partdetail/C52923) 2026-11-01 |  |
| SW1,SW2 | 轻触按键（BOOT/RST） | 电子件 | unit | 2040 | 2040 | 0.0139 | 28.36 | 0.0284 | 实查 | [链接](https://jlcpcb.com/partdetail/C318884) 2026-11-01 |  |
| DS1 | 0.96 寸 OLED 模块 | 外购模块 | unit | 1020 | 1020 | 1.6400 | 1672.80 | 1.6728 | 估算 | [链接](https://jlcpcb.com/partdetail/C18723026) 2026-11-01 |  |
| PCB1 | PCB 2 层 | 加工费 | unit | 1020 | 1020 | 0.4000 | 408.00 | 0.4080 | 待核实 | [链接](https://jlcpcb.com/blog/free-assembly-for-1-6-layer-pcbs-and-discounts-on-8-20-layer-pcba) 2026-11-01 | 按打样价折算（偏高） |
| SMT1 | 贴片工程费 | 加工费 | batch | 1 | 1 | 8.0000 | 8.00 | 0.0080 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 |  |
| SMT2 | 钢网 | 加工费 | batch | 1 | 1 | 1.5000 | 1.50 | 0.0015 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 |  |
| SMT3 | 贴片焊点费 | 加工费 | per_joint | 53000 | 53000 | 0.0017 | 90.10 | 0.0901 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-price) 2026-11-01 | 每台焊点 53 |
| SMT4 | 扩展库换料费 | 加工费 | per_extended_type | 3 | 3 | 3.0000 | 9.00 | 0.0090 | 待核实 | [链接](https://jlcpcb.com/help/article/pcb-assembly-faqs) 2026-11-01 | 扩展料 3 种 |
| ENC1 | 外壳 MJF PA12（克） | 结构件 | unit | 15300 | 15300 | 0.2750 | 4207.50 | 4.2075 | 待核实 | [链接](https://jlc3dp.com/blog/drastic-material-price-cuts-and-adjusted-post-processing-service-fees) 2026-11-01 | 示例假设 15 g |
| ASM1 | 整机组装人工（分钟） | 加工费 | unit | 5000 | 5000 | 0.0700 | 350.00 | 0.3500 | 估算 | 2026-11-01 | 示例假设每台 5 分钟 |
| PKG1 | 基础包装 | 包装 | unit | 1020 | 1020 | 0.3000 | 306.00 | 0.3060 | 估算 | 2026-11-01 |  |

警告：

- SMT3: 这些行焊点数未知，没有计入：U1
