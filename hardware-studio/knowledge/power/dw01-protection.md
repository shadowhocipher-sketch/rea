# DW01 类单节锂电保护 IC（以 Fortune DW01-P + FS8205A 为例）

一句话：单节锂电"保护板"的核心：一颗保护 IC 监测电芯电压和 MOS 压降，驱动两颗背靠背 N-MOS 切断充电或放电回路，防过充、过放、过流和短路。市面"DW01A"是很多厂家共用的名字，阈值可能不同，**以所买型号的规格书为准**。

> 数据手册来源说明：本页以台湾富晶（Fortune Semiconductor）**DW01-P（DW01-P-DS-10_EN Rev 1.0，Sep 2006）** 和配套双 N-MOS **FS8205A（FS8205A-DS-12_EN Rev 1.2，Aug 2009）** 为例，读自 GitHub 仓库 alltheworld/tp4056 的 doc/ 目录，非官方托管，标"待核实"。PDF 文本提取时 "μ" 字符丢失，单位按首页 "3 μA / 0.1 μA" 补回。

## 关键参数（DW01-P）

| 参数 | 最小 / 典型 / 最大 | 来源 |
|---|---|---|
| 过充保护电压 VOCP | 4.20 / 4.25 / 4.30 V | [DW01-P Rev1.0 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 过充释放电压 VOCR | 4.00 / 4.05 / 4.10 V | [DW01-P Rev1.0 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 过放保护电压 VODP | 2.30 / 2.40 / 2.50 V | [DW01-P Rev1.0 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 过放释放电压 VODR | 2.90 / 3.00 / 3.10 V | [DW01-P Rev1.0 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 过流检测电压 VOI1（CS 脚） | 120 / 150 / 180 mV | [DW01-P Rev1.0 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 短路检测电压 VOI2（VCC=3.6 V） | 1.00 / 1.35 / 1.70 V | [DW01-P Rev1.0 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 充电器检测阈值 VCHA | –1.2 / –0.7 / –0.2 V | [DW01-P Rev1.0 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 封装 | SOT-23-6 | [DW01-P Rev1.0 Ordering Information](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 引脚要点

| 引脚 | 要点 | 来源 |
|---|---|---|
| 1 OD | 放电控制 MOS 栅极 | [DW01-P Rev1.0 Pin Configuration](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 2 CS | 电流检测 / 充电器检测输入，经 R2 接到 MOS 另一端 | [DW01-P Rev1.0 Pin Configuration](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 3 OC | 充电控制 MOS 栅极 | [DW01-P Rev1.0 Pin Configuration](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 4 TD | 测试脚（缩短延时用） | [DW01-P Rev1.0 Pin Configuration](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 5 VCC | 经电阻 R1 接电芯正极，并加 C1，抑制充电器纹波和干扰 | [DW01-P Rev1.0 Design Guide 2](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 6 GND | 接电芯负极 | [DW01-P Rev1.0 Pin Configuration](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| R1、C1、R2 的推荐值 | 未查到（在典型应用图中，PDF 图内文字未能提取） | https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf · 未查到 |

## 电压、电流

| 项目 | 值 | 来源 |
|---|---|---|
| 工作电流（VCC=3.9 V） | 典型 3.0 μA，最大 6.0 μA | [DW01-P Rev1.0 电气特性 ICC](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 掉电电流（VCC=2.0 V） | 最大 0.1 μA | [DW01-P Rev1.0 电气特性 IPD](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| FS8205A 导通电阻 | VGS=4.5 V、4 A：典型 21 / 最大 25 mΩ；VGS=2.5 V、3 A：典型 27 / 最大 35 mΩ | [FS8205A Rev1.2 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/FS8205A-DS-12_EN.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| FS8205A 额定 | VDS 20 V；ID 6 A（25 °C）/ 5 A（70 °C）；脉冲 25 A | [FS8205A Rev1.2 绝对最大值](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/FS8205A-DS-12_EN.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 过流动作电流 | 手册公式 RON = VOIP / (2 × IT)；例：IT=3 A 需 RON=25 mΩ。估算：配 FS8205A（最大 25 mΩ@4.5 V）约 3 A；电芯低时栅压下降，RON 升到 35 mΩ，动作电流降到约 2.1 A | [DW01-P Rev1.0 Design Guide 1](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 估算 |

## 接口时序要点（保护延时）

| 项目 | 典型 / 最大 | 来源 |
|---|---|---|
| 过充延时 TOC | 80 / 200 ms | [DW01-P Rev1.0 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 过放延时 TOD（3.6→2.0 V） | 40 / 100 ms；但正文又写"默认过放延时 10 ms"——手册内部冲突 | [DW01-P Rev1.0 电气特性 / 功能说明](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 过流延时 TOI1 | 10 / 20 ms | [DW01-P Rev1.0 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 短路延时 TOI2 | 最大 500（文本提取后单位显示为 "s"，前缀疑似丢失，单位待核实） | [DW01-P Rev1.0 电气特性](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 过充释放条件 | 电芯电压降到 VOCR 以下；或低于 VOCP 且接上负载。高于 VOCP 时接负载也不释放 | [DW01-P Rev1.0 功能说明 Overcharge](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| 不同厂家"DW01A"阈值不同 | 立创上 DW01A 有 PUOLOP、YONGYUTAI、HL、Fortune DW01A-G 等多个品牌；本页数值只代表 Fortune DW01-P | [LCSC DW01A 搜索摘要（C351410 等）](https://www.lcsc.com/product-detail/C351410.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 把保护 IC 当电量管理 | DW01-P 过放阈值 2.4 V（典型），可能低于电芯规格书的放电截止电压（电芯手册本次未查，需对照）；固件应自己测电压按电芯规格提前关机，保护 IC 只做最后一道防线 | [DW01-P Rev1.0 电气特性 VODP](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 过流电流随 MOS 和温度漂移 | 动作电流 = VOIP /（2×RON），RON 随温度和栅压变化；大电流负载（功放、电机）要核算 | [DW01-P Rev1.0 Design Guide 1](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 过放后接充电器不恢复 | 过放锁定靠充电器检测（CS 低于 VCHA）或电压回升到 VODR 释放；R2 用于此时的闩锁保护 | [DW01-P Rev1.0 Design Guide 3](https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 来源列表

- [DW01-P] One Cell Lithium-ion/Polymer Battery Protection IC，DW01-P-DS-10_EN Rev 1.0（Fortune Semiconductor，Sep 2006）。第三方镜像：https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/DW01-P_DataSheet_V10.pdf （sha256 前缀 80defc55e243a05a）。手册印的官网 http://www.fsc.com.tw 本会话未访问（同类站点被拦截）。
- [FS8205A] FS8205A-DS-12_EN Rev 1.2（Fortune，Aug 2009）。第三方镜像：https://github.com/alltheworld/tp4056/blob/839b6d6fb0c57fc2e62fba5bea80eb2f5f90d8ea/doc/FS8205A-DS-12_EN.pdf （sha256 前缀 3fc239b75be4b235）
- [B] LCSC DW01A 列表（搜索摘要）：https://www.lcsc.com/product-detail/C351410.html
- 查询日期：2026-11-01。
