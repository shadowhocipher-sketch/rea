# 外壳可制造性（DFM）规则：FDM / 光固化 / MJF / 注塑

查询日期：2026-11-01。来源级别按 `.claude/skills/research-method/SKILL.md`（S/A/B/C）。
`hwcad/process.py` 里的每个常量都用 `DFM:<编号>` 指回本页。

> **核对状态说明（重要）**：本会话的网络策略拦截了 jlc3dp.com、formlabs.com、protolabs.com、hp.com、usb.org
> 等站点（WebFetch 报 `getaddrinfo ENOTFOUND`，curl 报 `CONNECT tunnel failed, response 403`）。
> 下表数值来自搜索引擎对这些**官方页面**的摘要，链接是原页面地址，但没有逐字打开原文核对。
> 因此"核对"一列统一写"摘要"；在能访问这些站点的环境里应打开链接逐条核对，核对后改为"原文"。
> 只有 C 级来源或来源互相冲突的，标"待核实"。

## 0. 通用

| 编号 | 规则 | 数值 | 来源 · 级别 · 日期 | 核对 |
|---|---|---|---|---|
| GEN-1 | 凸台、定位、卡扣、紧固件等功能特征的厚度 | > 1.5 mm | [JLC3DP 3D Printing Design Guideline](https://jlc3dp.com/help/article/3D-Printing-Design-Guideline) · B · 2026-11-01 | 摘要 |
| GEN-2 | 制造商给的最小壁厚是自动检查阈值，不是物理极限；薄壁可能在去支撑或搬运时断；零件越大壁要越厚 | — | 同上；[JLC3DP 壁厚文章](https://jlc3dp.com/blog/3d-print-wall-thickness) · B · 2026-11-01 | 摘要 |

## 1. FDM（熔融沉积）

| 编号 | 规则 | 数值 | 来源 · 级别 · 日期 | 核对 |
|---|---|---|---|---|
| FDM-1 | 最小壁厚 | JLC3DP：≥ 1.2 mm；Xometry：有支撑 0.75 mm / 无支撑 1.0 mm | [JLC3DP 壁厚文章](https://jlc3dp.com/blog/3d-print-wall-thickness) · B · 2026-11-01；[Xometry FDM Quick Design Guide](https://xometry.pro/en/?p=154421) · B · 2026-11-01 | 摘要 |
| FDM-1a | 库内默认壁厚 `default_wall` | 2.0 mm | **估算**：GEN-1 的 1.5 mm + 0.5 mm 余量 | — |
| FDM-2 | 不加支撑的最大悬垂角（相对竖直） | 45°；孔竖直放可减少支撑 | [Xometry FDM Quick Design Guide](https://xometry.pro/en/?p=154421) · B · 2026-11-01 | 摘要 |
| FDM-3 | 典型尺寸公差 | ±0.3 mm（≤100 mm），更大尺寸按比例 | [JLC3DP 3D Printing Service 能力页](https://jlc3dp.com/capabilities/3d-printing-service) · B · 2026-11-01（同站产品页另写"down to ±0.2 mm"，是最好情况） | 摘要 |
| FDM-3a | 装配配合单边间隙 `fit_clearance`（止口、按键帽、USB 开孔） | 0.3 mm | **估算**：取 FDM-3 的一个公差值作单边间隙；首件打样后按实测调整 | — |
| FDM-4 | 运动件最小间隙 | 0.5 mm | [Xometry FDM Quick Design Guide](https://xometry.pro/en/?p=154421) · B · 2026-11-01 | 摘要 |
| FDM-5 | 最小孔径；过孔比名义尺寸放大量 | 最小孔径：**未查到**（查过 JLC3DP、Xometry 摘要）；库内取 2.0 mm 为**估算**。过孔放大 0.2–0.5 mm 只见于第三方 | [wevolver FDM tips](https://www.wevolver.com/article/fdm-3d-printing-design-tips-best-practices-and-techniques-for-stronger-prints) · C · 2026-11-01 | 待核实 |
| FDM-6 | 3D 打印卡扣若沿 Z 方向（跨层）受弯，许用应力 / 应变减半 | ×0.5 | [Core77 How to Design Snap Fit Components](https://www.core77.com/posts/65318/How-to-Design-Snap-Fit-Components) · C · 2026-11-01 | 待核实 |

## 2. 光固化（SLA / DLP）

| 编号 | 规则 | 数值 | 来源 · 级别 · 日期 | 核对 |
|---|---|---|---|---|
| SLA-1 | 最小壁厚 | JLC3DP：≥ 0.8 mm；Formlabs Form 4：有支撑 / 无支撑都 0.2 mm；Formlabs 旧版 Design Specs：有支撑 0.4 mm，≤0.4 mm 的无支撑壁可能翘曲 | [JLC3DP 壁厚文章](https://jlc3dp.com/blog/3d-print-wall-thickness) · B；[Formlabs Form 4 Design Guide](https://formlabs.com/blog/design-guide-form4) · A；[Formlabs Design Specs](https://formlabs.com/support/Design-Specs/) · A · 2026-11-01 | 摘要；Formlabs 新旧值冲突，以所用机型为准 |
| SLA-2 | 零件间最小间隙（防止粘连） | Form 4：0.4 mm；Form 1+/Form 2 旧指南：0.5 mm | [Formlabs Form 4 Design Guide](https://formlabs.com/blog/design-guide-form4) · A · 2026-11-01 | 摘要 |
| SLA-3 | 典型尺寸公差 | ±0.2 mm（≤100 mm） | [JLC3DP 能力页](https://jlc3dp.com/capabilities/3d-printing-service) · B · 2026-11-01 | 摘要 |
| SLA-3a | 装配配合单边间隙 | 0.2 mm | **估算**：取 SLA-3 的一个公差值 | — |
| SLA-4 | 最小孔径；排液孔 | Form 4：孔 0.5 mm；排液孔 0.75 mm；小于 0.15 mm 的凹凸细节可能糊掉 | [Formlabs Form 4 Design Guide](https://formlabs.com/blog/design-guide-form4) · A · 2026-11-01 | 摘要 |
| SLA-5 | Formlabs 数值基于 Clear 树脂、100 µm 层厚，其他树脂和层厚会略有不同 | — | 同上 | 摘要 |

## 3. MJF（HP Multi Jet Fusion，尼龙粉末）

| 编号 | 规则 | 数值 | 来源 · 级别 · 日期 | 核对 |
|---|---|---|---|---|
| MJF-1 | 最小壁厚 | JLC3DP：≥ 1.0 mm；Xometry 转述 HP：最小 0.5 mm、推荐 1.5 mm | [JLC3DP 壁厚文章](https://jlc3dp.com/blog/3d-print-wall-thickness) · B；[Xometry EU MJF Design Guide (PDF)](https://xometry.pro/wp-content/uploads/2024/05/EN-EU-MJF-Design-Guide.pdf) · B · 2026-11-01 | 摘要；HP 官方手册未能找到 / 打开，待核实 |
| MJF-2 | 一起打印的运动件间隙 | 0.5–0.7 mm（截面厚时更大）；库内取 0.7 mm | 同上 Xometry PDF；[Xometry Asia HP MJF guidelines](https://xometry.asia/en/hp-mjf-3d-printing-design-guidelines/) · B · 2026-11-01 | 待核实（来源间不一致） |
| MJF-3 | 典型尺寸公差 | ±0.3 mm（≤100 mm） | [JLC3DP 能力页](https://jlc3dp.com/capabilities/3d-printing-service) · B · 2026-11-01 | 摘要 |
| MJF-3a | 装配配合单边间隙 | 0.3 mm | **估算**：取 MJF-3 的一个公差值 | — |
| MJF-4 | 孔 | Creabis：最小 1 mm、推荐 2 mm（需清粉）；另有资料写 1 mm 厚处 0.5 mm 孔 | [Creabis Design Rules (PDF)](https://creabis.de/pdf/Design-Rules_en.pdf) · B · 2026-11-01 | 待核实 |
| MJF-5 | 掏空件 | 壁约 2 mm，至少 2 个排粉孔，孔径 ≥ 5 mm | 同 MJF-1 Xometry PDF · B · 2026-11-01 | 待核实 |

## 4. 注塑

| 编号 | 规则 | 数值 | 来源 · 级别 · 日期 | 核对 |
|---|---|---|---|---|
| IM-1 | 推荐壁厚（按材料） | ABS 0.045–0.140 in（1.14–3.56 mm）；PC 1–3.1（英国站表格，单位推断为 mm）；壁厚尽量均匀 | [Protolabs Design Guidelines: Plastic Injection Molding](https://protolabs.com/services/injection-molding/plastic-injection-molding/design-guidelines) · B · 2026-11-01；[Protolabs UK 均匀壁厚](https://www.protolabs.com/en-gb/resources/design-tips/improving-part-design-with-uniform-wall-thickness/) · B · 2026-11-01 | 摘要；PC 单位待核实 |
| IM-2 | 脱模斜度 | Protolabs：轻纹理（PM-T1）约 3°，重纹理（PM-T2）≥ 5°；铝模可能要加斜度。"任何面至少 0.5°""每英寸深 1°"只见于第三方 | [Protolabs Draft Angle Guidelines](https://www.protolabs.com/injection-molding/fundamentals-of-molding/draft) · B · 2026-11-01；第三方：[Hubs draft angle](https://www.hubs.com/knowledge-base/draft-angle/) · C | 摘要；0.5° 待核实 |
| IM-3 | 筋厚 | 相邻壁厚的 40–60%，不超过 60%（防缩痕） | [Protolabs Design for Mouldability](https://www.protolabs.com/en-gb/resources/guides-and-trend-reports/designing-for-mouldability-volume-1/) · B · 2026-11-01 | 摘要 |
| IM-4 | 螺丝柱壁厚 | 所在壁厚的 40–60%；用筋把柱子连到侧壁，不要做实心粗柱（会缩痕、气孔）；Protolabs 铣模可能需要更厚 | [Protolabs Plastic Boss Design](https://www.protolabs.com/resources/design-tips/plastic-boss-design-on-molded-parts/) · B · 2026-11-01 | 摘要 |
| IM-5 | 相邻壁厚差 | 较薄壁不小于相邻壁的 40–60% | [Protolabs 壁厚问题](https://www.protolabs.com/resources/design-tips/solving-wall-thickness-issues-in-molded-parts/) · B · 2026-11-01 | 摘要 |
| IM-6 | 斜度的影响因素 | 壁厚、材料、顶出方式、收缩率、表面纹理、深度 | [Protolabs Draft](https://www.protolabs.com/injection-molding/fundamentals-of-molding/draft) · B · 2026-11-01 | 摘要 |
| IM-7 | 注塑配合间隙、公差、最小孔径 | **未查到**官方数值（查过 Protolabs 摘要）；库内 fit 0.1 / moving 0.3 / 公差 0.1 / 孔 1.0 mm 均为**估算**，开模前以模厂 DFM 报告为准 | — | — |

## 5. 紧固件

| 编号 | 规则 | 数值 | 来源 · 级别 · 日期 | 核对 |
|---|---|---|---|---|
| FAST-1 | 热塑性塑料自攻螺丝（EJOT PT / DELTA PT） | 底孔 dh = 0.8 × d1（DELTA PT 需要更高强度时可到 0.88 × d1）；柱外径 dT = 2 × d1；EVO PT 底孔 0.85 × d1 ±0.05 mm（约 1° 斜度注塑孔口处），拧入深度 ≥ 2 × d1 | [EJOT DELTA PT Flyer](https://www.ejot.de/medias/sys_master/Industry_Flyer/Industry_Flyer/h11/hc7/9331662782494/EJOT-DELTA-PT-Flyer-08.23-en.pdf) · S；[EJOT PT Flyer](https://www.ejot.de/medias/sys_master/Industry_Flyer/Industry_Flyer/h54/h3c/9331729760286/EJOT-PT-Flyer-08.23-en.pdf) · S；[EJOT EVO PT Flyer](https://www.industrie.ejot.de/medias/sys_master/Industry_Flyer/Industry_Flyer/hd3/hbc/9334340976670/EJOT-EVO-PT-Flyer-08.23-en.pdf) · S · 2026-11-01 | 摘要。比例针对注塑件；3D 打印件需打试样调整 |
| FAST-2 | M3 铜热熔螺母（Accu HTBI-M3-BR） | 底孔 4.0 mm（-0/+0.1），长 5.8 mm，孔周最小壁 1.8 mm；适用 PLA/ABS/PETG/尼龙 | [Accu HTBI-M3-BR 商品页](https://accu.co.uk/brass-threaded-inserts/845137-HTBI-M3-BR) · B · 2026-11-01 | 摘要。其他规格**未查到**原厂数据，库内不给默认值 |
| FAST-2a | 热熔螺母孔深 = 嵌件长 + 1.0 mm | — | **估算**：给熔融料留空间；DigiKey 教程取 +1.2 mm（[Maker.io](https://www.digikey.de/en/maker/tutorials/2025/intro-to-freecad-part-4-how-to-use-heat-set-inserts) · C） | — |
| FAST-3 | 螺丝过孔 | ISO 273 规定过孔精 / 中 / 粗三个系列，2024 年复审仍有效；具体 M3 数值未能取得。库内默认 d + 0.4 mm | [ISO 273:1979](https://www.iso.org/standard/4183.html) · S · 2026-11-01 | 待核实（表内数值未读到） |
| FAST-4 | 沉头孔直径默认 2d + 0.6 mm；过孔柱外径至少 = 沉头孔径 + 2 × 最小壁厚 | — | **估算**（避免沉头孔底只剩一圈薄壁；见 `hwcad/enclosure.py`） | — |

## 6. 卡扣

| 编号 | 规则 | 数值 | 来源 · 级别 · 日期 | 核对 |
|---|---|---|---|---|
| SNAP-1 | 等截面矩形悬臂梁：y = 0.67·ε·L²/t ⇔ ε = 1.5·t·y/L² | 公式 | Bayer（现 Covestro）《Snap-Fit Joints for Plastics – A Design Guide》，只找到第三方转载：[Scribd 副本](https://www.scribd.com/document/455201152/Snap-fit-pdf) · C · 2026-11-01 | 待核实（原文 PDF 未找到） |
| SNAP-2 | 经典梁公式低估根部应变，引入挠度放大系数 Q（与梁根部是实心块还是薄板有关）；许用应变和摩擦系数表在手册 IV-4 页 | — | [BASF Snap-Fit Design Manual（UL Prospector 上 BASF 提供的内容）](https://ulprospector.ul.com/1248/snapfit-3/) · A · 2026-11-01 | 摘要；Q 的数值表未取得 |
| SNAP-3 | 许用应变举例 | Bayblend 一次装配 2.5%，频繁装拆应降低；PC 4%–9.2%；PEI 9.8%；POM 1.5% | Bayer 资料转载（Scribd）· C；[Eng-Tips 帖子](https://eng-tips.com/threads/allowable-strain-of-polypropylene-pp.243605) · C · 2026-11-01 | 待核实（只有 C 级来源，库内**不给默认许用值**） |

## 7. USB-C

| 编号 | 规则 | 数值 | 来源 · 级别 · 日期 | 核对 |
|---|---|---|---|---|
| USB-1 | 插头金属壳外形 | 8.25 ± 0.03 × 2.40 ± 0.03 mm（单一厂家图纸） | [CJT CJ-CM026-24P 图纸](https://cjt.com/up/CJ-CM026-24P_dwg.pdf) · S（该零件）· 2026-11-01 | 待核实（未取得 USB-IF 原文） |
| USB-2 | 插座壳长度（参考尺寸） | 6.20 ± 0.02 mm | USB Type-C ECN for receptacle shell length（[镜像](https://docs.ampnuts.ru/eevblog.docs/Standards/USB%203.1/usb_31_030215/USB%20Type-C/USB%20Type-C%20ECNs/USB%20Type-C%20ECN%20for%20receptacle%20shell%20length.pdf)）· A · 2026-11-01 | 待核实（非 usb.org 原站） |
| USB-3 | 插头外壳（overmold）最大尺寸 | **未查到** USB-IF 规范里的数值（查过搜索摘要；规范为 IEC 62680-1-3 / USB Type-C Cable and Connector Specification）。库内默认 12.4 × 6.5 × 20 mm 为**估算**：DigiKey 论坛有用户以 12.5 mm 为限（C 级），GCT USB4215 图纸配合视图标 6.5 Max | [DigiKey 论坛](https://forum.digikey.com/t/overmold-size-of-the-usb-c-male-end/70874) · C；[GCT USB4215](https://gct.co/Files/Drawings/USB4215.pdf) · S（该零件）· 2026-11-01 | 估算，**用游标卡尺量实际线材** |
| USB-4 | 插座外形默认 8.94 × 3.26 × 7.35 mm | — | **估算**，未查到 S 级来源；必须换成所用插座数据手册的值 | — |
| USB-5 | 开孔规则：插座端面缩进外表面（recess > 0）时，插头外壳要伸进壁里，开孔按插头外壳 + 间隙；平齐或伸出时按插座外形 + 间隙 | — | 几何推导（见 `hwcad/usbc.py`），由插头包络干涉检查验证 | — |

## 8. 电池

| 编号 | 规则 | 数值 | 来源 · 级别 · 日期 | 核对 |
|---|---|---|---|---|
| BAT-1 | 软包电芯膨胀余量 | 没有统一标准，各厂自定；电池包厂商 Epec："部分软包电芯在寿命期内可能膨胀 10% 或更多"；外壳要为膨胀留空间、避免点压力 | [Epec Battery Enclosure Design](https://www.epectec.com/batteries/battery-enclosure-design.html) · C；[evkx Pouch Cell](https://evkx.net/dictionary/pouch-cell) · C · 2026-11-01 | 待核实。库内默认厚度 +10%、平面单边 0.5 mm、顶部 0.3 mm 均为**估算**；以电芯规格书的寿命末期厚度为准 |

## 9. 打印平台

| 编号 | 机型 | 平台 X × Y × Z | 来源 · 级别 · 日期 | 核对 |
|---|---|---|---|---|
| BED-1 | Prusa MK4S | 250 × 210 × 220 mm | [3DJake 商品页](https://www.3djake.com/prusa/mk4s) · B · 2026-11-01（未取得 prusa3d.com 原页） | 待核实 |
| BED-2 | Bambu Lab A1 mini / P1S | 180³ / 256³ mm | [A1 mini TDS（经销商托管）](https://www.3dprintergear.com.au/assets/files/A1%20Mini%20TDS.pdf) · B；[B&H 商品页](https://www.bhphotovideo.com/c/product/1940046-REG/bambu_lab_pf002_m_sa005_us_a1_mini_combo_3d.html) · B · 2026-11-01 | 待核实 |

## 10. 多大批量换哪种工艺

公开资料给出的注塑 / 3D 打印成本平衡点差别很大，取决于零件大小、模具价格、打印材料价格：

| 来源 | 平衡点 | 来源 · 级别 · 日期 |
|---|---|---|
| Xometry | 250–2,000 件；小无人机支架到 2,000 件打印仍有竞争力 | [Xometry 3D Printing vs Injection Molding Breakeven](https://www.xometry.com/resources/3d-printing/3d-printing-vs-injection-molding-breakeven/) · B · 2026-11-01 |
| RSP（合同制造商） | 250–500 件 | [RSP](https://www.rspinc.com/blog/contract-manufacturing/3d-printing-vs-injection-molding/) · C · 2026-11-01 |
| Prusa 自家 MK4S 屏幕壳 | 约 80,000 件（€6,000 模具；只比较开模后的单件成本） | [Prusa](https://pro.prusa3d.com/?p=16235) · A · 2026-11-01 |
| Formlabs | 视树脂采购量可到 40,000 件以上；打印无需模具、当天可开工 | [Formlabs Race to 1,000 Parts](https://formlabs.com/blog/race-to-1000-parts-3d-printing-injection-molding/) · A · 2026-11-01 |

**估算的决策表**（依据：上表区间；小型电子产品外壳一般为 50–150 mm、每台 2–4 个塑料件。在具体项目里应拿两家以上报价复核）：

| 每款零件数量 | 建议工艺 | 理由 |
|---|---|---|
| 1–20 | FDM（功能验证）；外观样机用光固化 | 无模具、当天出件；光固化表面好、公差 ±0.2 mm |
| 20–300 | 光固化或 MJF（外包） | 单价随数量几乎不变；MJF 尼龙件强度和一致性适合小批量终端件 |
| 300–2,000 | MJF 与铝模（快速模）注塑二选一，拿报价比较 | 落在 Xometry / RSP 给出的平衡点区间内 |
| > 2,000 | 注塑（钢模 / 铝模） | 超过大部分来源的平衡点；先按 IM-1~IM-6 改设计（均匀壁厚、斜度、筋、螺丝柱） |

切换前要改的设计（估算 / 经验，按本页规则核对）：3D 打印件的厚实心螺丝柱、零斜度直壁、尖角，在注塑时都要改；
光固化 / MJF 的配合间隙（0.2–0.3 mm）在注塑时通常可以收小（IM-7 未查到官方值）。
