# 合规检查清单：(b) 不联网的口袋设备（锂电池 + 充电口）

> **这是资料整理，不是法律意见。** 清单只根据你给出的产品特征，从 `compliance/data/requirements.yaml` 里挑出可能相关的法规条目；是否适用、怎么做，以法规原文和认证机构/检测机构的书面意见为准。标"待核实"的条目尤其要确认。

数据查询日期：2026-11-01。数据来源：`compliance/data/requirements.yaml`（共 57 条）。

## 产品特征

| 特征 | 取值 |
|---|---|
| 无线 | 无 |
| 联网 | 否 |
| 电池 | lithium |
| 随附电源适配器 | 否 |
| 儿童用 | 否 |
| 目标市场 | CN, EU, US, UK, AU |

## 提示

- 产品有可充电电池但不随附适配器：只要不在包装里提供充电器，适配器相关条目不会列出；如果随附充电器，请设 adapter: true。

共 24 条，其中待核实 9 条。

## CN · 中国

### CN-03 CCC 强制性产品认证（产品本体是否在目录内）　⚠️ **待核实**

- **依据**：市场监管总局《强制性产品认证目录描述与界定表（2023年修订）》（2023 年第 36 号公告）及后续调整
- **要求**：列入 CCC 目录的产品，未获得认证证书（或按规定完成自我声明）并加施 CCC 标志的，不得出厂、销售、进口。2023 年修订版共 16 大类 96 种产品，部分产品实行自我声明程序 A / B；2024 年后目录又有增补。
- **适用条件**：任何在中国销售的电子产品都要先按《描述与界定表》判断本体是否属于目录产品（例如信息技术设备、音视频设备）。
- **证据形式**：认证 / 型号核准（由认证机构或主管部门发证）。目录内产品由指定认证机构认证，或按目录标注走自我声明（报送系统 sdoc.cnca.cn）；目录外产品不需要 CCC。
- **来源**：[香港工业贸易署转载：强制性产品认证目录描述与界定表（2023年修订）公告](https://www.tid.gov.hk/english/aboutus/tradecircular/cic/asia/2023/files/ci2023659a.pdf) · A · 2026-11-01<br>[汕头市政府文件（提到截至 2024 年底目录为 16 大类 105 种）](https://www.shantou.gov.cn/attachment/0/135/135589/2446285.docx) · A · 2026-11-01
- **疑点 / 待核实**：认监委官网（cnca.gov.cn）原文附件本次无法访问，没有读到具体条目。USB 供电的小型桌面电子产品 是否落入"信息技术设备""音视频设备"等目录类别，取决于产品功能和界定表的描述，必须让认证机构判断。
- **备注**：产品本体不在目录内时，其随附的适配器（CN-04）、内置锂电池（CN-05）仍可能各自需要 CCC。

### CN-05 CCC：锂离子电池和电池组（GB 31241）　⚠️ **待核实**

- **依据**：市场监管总局 2023 年公告（对锂离子电池和电池组、移动电源实施 CCC 管理）；国家标准 GB 31241-2022；实施规则 CNCA-C09-01:2023
- **要求**：自 2023-08-01 起对便携式电子产品用锂离子电池和电池组、移动电源实施 CCC 管理；自 2024-08-01 起，未获 CCC 证书和未标注认证标志的，不得出厂、销售、进口或在其他经营活动中使用。锂离子电池和电池组依据 GB 31241。
- **适用条件**：产品内置可充电锂离子 / 锂聚合物电池（便携式电子产品用），在中国销售。
- **证据形式**：认证 / 型号核准（由认证机构或主管部门发证）。电池（或电池组）由指定认证机构认证；整机厂通常采购已获 CCC 的电芯/电池组并保存证书。
- **来源**：[香港工业贸易署转载：市场监管总局关于对锂离子电池等产品实施 CCC 管理的公告（2023）](https://www.tid.gov.hk/english/aboutus/tradecircular/cic/asia/2023/files/ci2023409a.pdf) · A · 2026-11-01<br>[人民网：8月起对锂电池实施CCC认证（2023-07-31）](https://paper.people.com.cn/zgnybwap/html/2023-07/31/content_26009869.htm) · C · 2026-11-01
- **疑点 / 待核实**：市场监管总局官网原文本次无法访问；公告文号和发布日期各来源不一致（3 月 / 7 月，"第10号"）。内置于整机中的电池是否必须单独持有 CCC 证书（还是只对单独销售的电池），以及小容量电池是否有豁免，没有读到原文条款。
- **备注**：2026 年工信部公示了《移动电源安全技术规范》强制性国家标准报批稿（第三方报道），只影响移动电源（充电宝）类产品。

### CN-07 中国 RoHS：电器电子产品有害物质限制使用　⚠️ **待核实**

- **依据**：《电器电子产品有害物质限制使用管理办法》；《电器电子产品有害物质限制使用达标管理目录（2026年版）》；GB 26572—2025（2027-08-01 实施）
- **要求**：电器电子产品须按标准标注有害物质信息（RoHS 标识、信息披露）；列入达标管理目录的产品还须满足限量要求并纳入合格评定。2026 年版目录共 33 种产品，新增产品管控要求 2027-08-01 起实施。
- **适用条件**：所有在中国销售的电器电子产品（标识义务）；是否属于达标管理目录的 33 种产品需单独判断。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。标识和信息披露由企业自行完成；目录内产品的合格评定方式（自我声明或认证）待核实。
- **来源**：[国家科技传播中心网站：达标管理目录（2026年版）相关公告](https://www.ncsti.gov.cn/kjdt/tzgg/202605/t20260528_248133.html) · A · 2026-11-01<br>[ChemLinked：达标管理目录（2026 版）英文翻译](https://chemical.chemlinked.com/translation/qualification-management-catalogue-for-the-restriction-of-hazardous-substances-in-electrical-appliances-and-electronic-products-2026-version) · C · 2026-11-01
- **疑点 / 待核实**：工信部原文和目录附件本次无法访问，33 种产品的具体名单没有读到（第三方称新增智能手环等）；旧标准 SJ/T 11364、GB/T 26572-2011 与 GB 26572—2025 的过渡安排没查到官方说明。
- **备注**：物料选型时就要求供应商提供符合限量要求的声明或检测报告，省得后面补。

### CN-10 锂电池出口：出境危险货物运输包装使用鉴定（"危包证"）与 UN 38.3　✅ 已核实

- **依据**：《中华人民共和国进出口商品检验法》第十七条；UN《试验和标准手册》第三部分 38.3；海运按《国际海运危险货物规则》（IMDG Code）
- **要求**：进出口商品检验法第十七条：为出口危险货物生产包装容器的企业，须申请商检机构（现为海关）做包装容器的性能鉴定；生产出口危险货物的企业，须申请包装容器的使用鉴定；使用未经鉴定合格的包装容器的危险货物，不准出口。按海关答疑（媒体转述），大部分锂电池属于危险货物，出口前要完成 UN 38.3 测试，由电池生产厂或出口商向属地海关申请 《出境危险货物运输包装使用鉴定结果单》（俗称危包证），海运订舱和危险品申报时都要提供；包装要有 UN 包装标记、锂电池标记 / 9 类危险品标签，电池须标额定能量（Wh）。
- **适用条件**：产品含锂离子电池或锂金属纽扣电池，从中国出口（空运、海运、快递）。
- **证据形式**：认证 / 型号核准（由认证机构或主管部门发证）。危包证由属地海关出具；UN 38.3 测试报告和测试摘要向电芯/电池组供应商索取，整机出口时由货代/承运人核对。
- **来源**：[香港工业贸易署转载：《中华人民共和国进出口商品检验法》全文（2018 年修正文本，节录自全国人大信息中心网站）](https://www.tid.gov.hk/english/aboutus/tradecircular/cic/asia/2019/files/ci201952a.pdf) · A · 2026-11-01<br>[维基文库：中华人民共和国进出口商品检验法（2021 年）](https://zh.wikisource.org/wiki/%E4%B8%AD%E5%8D%8E%E4%BA%BA%E6%B0%91%E5%85%B1%E5%92%8C%E5%9B%BD%E8%BF%9B%E5%87%BA%E5%8F%A3%E5%95%86%E5%93%81%E6%A3%80%E9%AA%8C%E6%B3%95_(2021%E5%B9%B4)) · C · 2026-11-01<br>[人民日报海外版：锂电池出口有哪些要求？（海关答疑，2024-07-20）](https://paper.people.com.cn/hwbwap/html/2024-07/20/content_26070303.htm) · C · 2026-11-01
- **疑点 / 待核实**：已核实的只是第十七条"出口危险货物包装须经使用鉴定"（A 级转载为 2018 年修正文本，2021 年修正后的现行文本只在第三方转载里见到，条文一致）。以下只有第三方或媒体来源：危包证办理流程和材料；锂电池哪些情况算危险货物、哪些按 UN 特殊规定 188（小电芯 ≤20 Wh、小电池 ≤100 Wh、锂金属电芯 ≤1 g 等，第三方资料）可以免除危险品包装要求；装在设备里的小电池（UN 3481 / UN 3091）出口时是否仍需危包证。海关总署原文（customs.gov.cn）本次无法访问，需要向属地海关或货代确认。
- **备注**：中国境内运输和空运要求见 CN-11；进口国在途要求见 EU-15、UK-12、US-08、AU-09。

### CN-11 锂电池航空运输（中国民航）：MH/T 1020 与 UN 38.3；运输安全国标 GB 21966　⚠️ **待核实**

- **依据**：民航行业标准 MH/T 1020-2018《锂电池航空运输规范》；国际民航组织《危险物品安全航空运输技术细则》（ICAO TI，Doc 9284）；GB 21966-2008《锂原电池和蓄电池在运输中的安全要求》
- **要求**：按第三方提供的 MH/T 1020-2018 译本：锂电池（芯）交付航空运输前须通过 UN《试验和标准手册》第三部分 38.3 的系列试验。ICAO 技术细则把锂电池列为危险物品，按包装说明（例如装在设备中的锂离子电池为 PI 967、与设备包装在一起为 PI 966）规定数量限制和包装要求。GB 21966-2008 等同采用 IEC 62281:2004，规定锂电池运输中的安全试验方法和要求。
- **适用条件**：产品含锂离子电池或锂金属纽扣电池，在中国境内空运、快递，或从中国空运出口。
- **证据形式**：第三方测试（指定或认可的实验室出报告）。UN 38.3 测试报告 / 测试摘要向电池供应商索取；空运还要货代按承运人要求出具运输条件鉴定或危险品申报，所需文件以承运人为准。
- **来源**：[codeofchina：MH/T 1020-2018 英文译本页面](https://codeofchina.com/standard/MHT1020-2018.html) · C · 2026-11-01<br>[chinesestandard.net：GB 21966-2008 英文译本](https://www.chinesestandard.net/PDF-EN/GB21966-2008EN-P06P-H4752H-175950.pdf) · C · 2026-11-01<br>[ICAO DGP 工作文件（中文）：锂电池客货运相关修订](https://www.icao.int:443/safety/DangerousGoods/DGP25/DGP.25.WP.033.5.ch.pdf) · A · 2026-11-01
- **疑点 / 待核实**：民航局（caac.gov.cn）原文和 MH/T 1020 现行版本本次都没读到，只有第三方译本；MH/T 1020 是否已有 2018 版之后的修订未查到。GB 21966-2008 是否现行、是否为强制性标准、是否会按 IEC 62281 新版修订，搜索结果没有直接说明。ICAO 工作文件只是修订讨论材料，不是技术细则现行文本；IATA 2026 版锂电池指南（PI 965–970、Section II 变化、30% 荷电状态）本次只见到第三方摘要。快递（邮政）渠道对含锂电池物品的收寄规定未查。
- **备注**：选电芯时就要求供应商提供 UN 38.3 测试报告和测试摘要，型号要与实物一致。

## EU · 欧盟 CE

### EU-05 电磁兼容指令 EMC 2014/30/EU（无无线功能的产品）　✅ 已核实

- **依据**：Directive 2014/30/EU
- **要求**：设备的电磁骚扰不得超出限值、并有足够的抗扰度；编制技术文件和欧盟符合性声明，加施 CE 标志；文件保存 10 年。
- **适用条件**：不含无线电功能的电子产品（含无线的产品由 RED 第 3(1)(b) 条覆盖 EMC）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。内部生产控制（自我声明），通常按协调标准测试。
- **来源**：[EUR-Lex：Directive 2014/30/EU](https://eur-lex.europa.eu/eli/dir/2014/30/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[European Commission：Electromagnetic compatibility (EMC) Directive](https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/electromagnetic-compatibility-emc-directive_en) · A · 2026-11-01

### EU-08 RoHS 2011/65/EU（有害物质限制）　✅ 已核实

- **依据**：Directive 2011/65/EU 及其附件 II 的修订（如 Delegated Directive (EU) 2015/863）
- **要求**：电子电气设备中限用物质（铅、汞、镉、六价铬、多溴联苯、多溴二苯醚及后续增加的邻苯二甲酸酯类）不得超过最大浓度值；纳入符合性声明并加施 CE 标志。
- **适用条件**：所有在欧盟销售的电子电气产品（含随附适配器、线缆）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。技术文件里保存物料合规声明 / 检测报告。
- **来源**：[EUR-Lex：Directive 2011/65/EU](https://eur-lex.europa.eu/eli/dir/2011/65/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[European Commission (DG ENV)：RoHS Directive](https://environment.ec.europa.eu/topics/waste-and-recycling/rohs-directive_en) · A · 2026-11-01
- **疑点 / 待核实**：限用物质总数各来源说法不一（6 种 / 10 种），以附件 II 现行版本为准。

### EU-09 WEEE 2012/19/EU（废弃电子电气设备生产者责任）　⚠️ **待核实**

- **依据**：Directive 2012/19/EU
- **要求**：生产者须在销售所在的每个成员国登记、承担回收处理费用并报告数量；产品标注带叉垃圾桶符号。
- **适用条件**：所有在欧盟销售的电子电气产品。
- **证据形式**：注册 / 备案 / 生产者责任登记。各成员国分别登记（例如德国 EAR、法国等），远程销售者可能需要授权代表。
- **来源**：[EUR-Lex：Directive 2012/19/EU](https://eur-lex.europa.eu/eli/dir/2012/19/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[European Commission (DG ENV)：Waste from Electrical and Electronic Equipment (WEEE)](https://environment.ec.europa.eu/topics/waste-and-recycling/waste-electrical-and-electronic-equipment-weee_en) · A · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）
- **疑点 / 待核实**：DG ENV 的 WEEE 页面本次未在搜索结果中出现（只在 RoHS 页面摘要中看到"WEEE 指令与 RoHS 配合促进回收"），登记义务按法规原文核对；各成员国登记的具体流程和费用不在本库范围，需逐国确认。

### EU-10 电池法规 (EU) 2023/1542：生产者责任、标签、合规义务　⚠️ **待核实**

- **依据**：Regulation (EU) 2023/1542
- **要求**：投放含电池的产品（便携式电池包括纽扣电池和内置锂电池）须承担电池的生产者延伸责任（登记、回收），满足标签与信息要求、有害物质限制等，各项义务按法规分阶段适用。
- **适用条件**：产品含任何电池（内置可充电锂电池或纽扣电池）。
- **证据形式**：注册 / 备案 / 生产者责任登记。各成员国电池生产者登记；电池本身的合规文件向电池供应商索取。
- **来源**：[EUR-Lex：Regulation (EU) 2023/1542](https://eur-lex.europa.eu/eli/reg/2023/1542/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[EUR-Lex：Commission Notice C/2025/214（第 11 条可拆卸性指南）](https://eur-lex.europa.eu/eli/C/2025/214/oj/eng) · A · 2026-11-01
- **疑点 / 待核实**：各项义务（标签、二维码、CE 标志等）的具体适用日期本次没有逐条读到原文。
- **备注**：第 11 条可拆卸要求单独列在 EU-11。

### EU-11 电池法规第 11 条：便携式电池可由终端用户拆卸更换（2027-02-18 起）　✅ 已核实

- **依据**：Regulation (EU) 2023/1542 第 11 条；委员会指南 C/2025/214
- **要求**：自 2027-02-18 起，含便携式电池的产品须设计成终端用户可用市售工具拆卸、更换电池（有例外情形，2026 年有授权法规增加了可由独立专业人员更换的产品类别）。义务在投放该产品的制造商/进口商。
- **适用条件**：产品含便携式电池（含纽扣电池、内置锂电池），计划 2027-02-18 以后在欧盟投放。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。设计要求，写进技术文件；例外情形需要论证。
- **来源**：[EUR-Lex：Regulation (EU) 2023/1542](https://eur-lex.europa.eu/eli/reg/2023/1542/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[EUR-Lex：Commission Notice C/2025/214（第 11 条指南）](https://eur-lex.europa.eu/eli/C/2025/214/oj/eng) · A · 2026-11-01
- **疑点 / 待核实**：2026 年新增例外（如可穿戴设备）的最终文本和状态没读到；外壳用卡扣/胶粘的产品要尽早评估。
- **备注**：对外壳设计（B 线）影响大：电池仓要能用普通工具打开。

### EU-12 通用产品安全法规 GPSR (EU) 2023/988　✅ 已核实

- **依据**：Regulation (EU) 2023/988
- **要求**：消费品须安全（覆盖其他专门法规没管到的风险）；制造商须做内部风险分析、编制技术文件、标注识别和联系信息，在欧盟须有负责的经营者；在线销售有额外信息要求。2024-12-13 起适用，取代 2001/95/EC。
- **适用条件**：所有面向消费者的产品。
- **证据形式**：一般安全义务（无固定证书，靠风险评估和技术文件）。没有证书；靠风险评估、技术文件和标签。
- **来源**：[EUR-Lex：Regulation (EU) 2023/988](https://eur-lex.europa.eu/eli/reg/2023/988/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[EU-OSHA：Regulation 2023/988/EU general product safety](https://osha.europa.eu/en/legislation/directive/regulation-2023988eu-general-product-safety) · A · 2026-11-01<br>[GOV.UK：EU Regulation 2023/988 on general product safety factsheet（北爱尔兰适用说明）](https://www.gov.uk/government/publications/general-product-safety-regulations-northern-ireland/eu-regulation-2023988-on-general-product-safety-factsheet) · A · 2026-11-01
- **疑点 / 待核实**：欧盟负责经营者的具体条款（GPSR 与市场监管法规 (EU) 2019/1020 的衔接）条款号待核实。

### EU-15 锂电池运输：ADR（经 2008/68/EC 在欧盟境内适用）与 UN 38.3 测试摘要　✅ 已核实

- **依据**：Directive 2008/68/EC（内陆危险货物运输）附件 I 第 I.1 节 = ADR；Commission Delegated Directive (EU) 2025/149（适用 ADR 2025）；空运 ICAO TI / IATA DGR，海运 IMDG Code
- **要求**：Directive 2008/68/EC 规定欧盟境内公路、铁路、内河危险货物运输适用 ADR / RID / ADN；2025/149 号授权指令把附件更新为 2025-01-01 起适用的 ADR 版本（过渡期到 2025-06-30）。锂电池在 ADR 中属于第 9 类危险货物：运输前须通过 UN 38.3 测试，制造商和后续分销商须提供测试摘要（第三方资料：ADR 2.2.9.1.7，2020-01-01 起）。小电芯/小电池按特殊规定 188 可以简化包装和文件。进出欧盟的空运按 ICAO 技术细则 / IATA DGR，海运按 IMDG Code。
- **适用条件**：产品含锂离子电池或锂金属纽扣电池，运进欧盟或在欧盟境内运输（含电商发货、退货）。
- **证据形式**：第三方测试（指定或认可的实验室出报告）。UN 38.3 测试报告和测试摘要向电池供应商索取；包装、标记、文件按承运人和货代要求。
- **来源**：[EU-OSHA：Directive 2008/68/EC on the inland transport of dangerous goods](https://osha.europa.eu/en/legislation/directives/directive-2008-68-ec) · A · 2026-11-01<br>[EUR-Lex：Commission Delegated Directive (EU) 2025/149](https://eur-lex.europa.eu/eli/dir_del/2025/149/oj/eng/pdf) · S · 2026-11-01<br>[TÜV Rheinland：Lithium batteries transport（2025-01）](https://tuv.com/content-media-files/germany/bs-products/pdfs/other/tuev-rheinland-lithiumbatteries-transport-01-2025-en.pdf) · C · 2026-11-01
- **疑点 / 待核实**：已核实的是"欧盟境内运输适用 ADR，且已更新到 ADR 2025"。ADR 中锂电池的具体条款号（2.2.9.1.7、测试摘要义务、特殊规定 188 的 Wh / 锂含量门限）只来自第三方资料，UNECE ADR 原文本次没有读到。2027 年起 ADR 是否再改锂电池条款未查。
- **备注**：测试摘要义务与美国 US-08 相同，可以共用一份供应商文件。

## US · 美国 FCC / CPSC

### US-03 FCC Part 15 Subpart B 无意辐射体（数字设备）：SDoC　⚠️ **待核实**

- **依据**：47 CFR Part 15 Subpart B；47 CFR 2.906（Supplier's Declaration of Conformity）
- **要求**：含数字电路（有时钟）的设备属于无意辐射体，B 类（家用）数字设备一般走供应商符合性声明（SDoC）：自行测试合规、由美国境内的负责方保存记录、产品附合规信息；不需要向 FCC 提交。也可以选择走认证。
- **适用条件**：所有含数字电路的电子产品（Part 15 有豁免条款，见疑点）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。由实验室按 Part 15 B 类限值测试，负责方保存测试报告和 SDoC。
- **来源**：[eCFR：47 CFR Part 15 Subpart B—Unintentional Radiators](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-B) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[eCFR：47 CFR Part 2 Subpart J—Equipment Authorization Procedures（含 2.906）](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-2/subpart-J) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[Cornell LII：47 CFR 2.906（镜像）](https://www.law.cornell.edu/cfr/text/47/2.906) · C · 2026-11-01
- **疑点 / 待核实**：Part 15 Subpart B 的设备分类表和豁免条款（例如低功耗或特定用途的数字设备）本次没有读到原文；电池供电的小设备是否落入豁免，需要实验室判断。
- **备注**：带无线的产品，非无线部分（数字电路）同样要做 Subpart B 评估。

### US-08 锂电池运输：49 CFR 173.185 与 UN 38.3 测试摘要　✅ 已核实

- **依据**：49 CFR 173.185；UN《试验和标准手册》第三部分 38.3
- **要求**：锂电池（含锂离子和锂金属纽扣电池）运输前须通过 UN 38.3 测试；2008-01-01 及以后制造的锂电芯/电池，其制造商和后续分销商须提供测试摘要（test summary）。含电池的设备运输有包装、标记和数量方面的要求和例外。
- **适用条件**：产品含锂离子电池，或含锂金属纽扣电池（如 CR 系列），需要运输（含快递、空运）。
- **证据形式**：第三方测试（指定或认可的实验室出报告）。向电池供应商索取 UN 38.3 测试报告和测试摘要；整机包装按承运方要求。
- **来源**：[eCFR：49 CFR 173.185 Lithium cells and batteries](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-E/section-173.185) · S · 2026-11-01<br>[PHMSA：Lithium Battery Test Summary (2024)](https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2024-09/Lithium-Battery-Test-Summary-2024.pdf) · A · 2026-11-01
- **疑点 / 待核实**：小型消费设备的例外条款（173.185(c) 等）现行文本没有读到；空运还要看 IATA DGR，本库未展开。碱性/锌空纽扣电池不属于锂电池。
- **备注**：运输要求在所有市场都适用：中国出口和空运见 CN-10、CN-11，欧盟 EU-15，英国 UK-12，澳大利亚 AU-09。

### US-09 锂电池产品安全：未查到联邦层面的专门强制标准（一般安全义务）　⚠️ **待核实**

- **依据**：未查到专门联邦法规；适用 CPSC 一般产品安全管辖
- **要求**：本次没有找到适用于一般小型消费电子内置锂电池的联邦强制安全标准（UL 2054 / UL 62133 等为自愿标准，但零售渠道常作为准入条件）。CPSC 可对存在缺陷的产品要求召回。
- **适用条件**：产品内置可充电锂电池，在美国销售。
- **证据形式**：一般安全义务（无固定证书，靠风险评估和技术文件）。未查到强制证书；建议电池选用有 UL/IEC 62133 报告的电芯/电池组。
- **来源**：[CPSC 企业指南示例页（纽扣电池；未找到锂电池专页，仅作 CPSC 官方指南入口）](https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Button-Cell-and-Coin-Battery) · A · 2026-11-01
- **疑点 / 待核实**：只能说"未查到"，不能证明不存在；部分州（如纽约州对电动出行设备电池）有州法，小型消费电子是否受影响未查。

## UK · 英国 UKCA

### UK-02 Electromagnetic Compatibility Regulations 2016（无无线功能的产品）　✅ 已核实

- **依据**：The Electromagnetic Compatibility Regulations 2016
- **要求**：设备须满足电磁兼容基本要求，编制技术文件和符合性声明，加施 UKCA（或按承认安排加施 CE）。
- **适用条件**：不含无线电功能的电子产品（含无线的由 UK-01 覆盖）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。内部生产控制。
- **来源**：[GOV.UK：Electromagnetic Compatibility Regulations 2016: Great Britain（法定指南）](https://www.gov.uk/government/publications/electromagnetic-compatibility-regulations-2016/electromagnetic-compatibility-regulations-2016-great-britain) · A · 2026-11-01
- **疑点 / 待核实**：本次没有在搜索结果里看到该条例在 legislation.gov.uk 的原文链接（SI 编号未核对）。

### UK-04 RoHS Regulations 2012（英国有害物质限制）　✅ 已核实

- **依据**：The Restriction of the Use of Certain Hazardous Substances in Electrical and Electronic Equipment Regulations 2012（SI 2012/3032）
- **要求**：电子电气设备中限用物质不得超标；纳入符合性声明。大不列颠有独立的豁免制度。
- **适用条件**：所有在英国销售的电子电气产品。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。物料合规声明 / 检测报告存入技术文件。
- **来源**：[legislation.gov.uk：SI 2012/3032](https://www.legislation.gov.uk/uksi/2012/3032/contents) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[GOV.UK：RoHS Regulations 2012 (as amended): Great Britain](https://www.gov.uk/government/publications/restriction-of-hazardous-substances-rohs-regulations/rohs-regulations-2012-as-amended-great-britain) · A · 2026-11-01

### UK-05 WEEE Regulations 2013（生产者责任）　✅ 已核实

- **依据**：The Waste Electrical and Electronic Equipment Regulations 2013（SI 2013/3113）
- **要求**：电子电气设备生产者每年登记，承担家用废弃设备的回收处理费用；年投放量低于 5 吨的小生产者可直接向环境主管机构登记。
- **适用条件**：所有在英国销售的电子电气产品。
- **证据形式**：注册 / 备案 / 生产者责任登记。加入生产者合规计划或按小生产者直接登记。
- **来源**：[legislation.gov.uk：SI 2013/3113](https://www.legislation.gov.uk/uksi/2013/3113/contents) · S · 2026-11-01<br>[GOV.UK：Regulations: waste electrical and electronic equipment (WEEE)](https://www.gov.uk/guidance/regulations-waste-electrical-and-electronic-equipment) · A · 2026-11-01
- **疑点 / 待核实**：2025 年有修订（GOV.UK 提到），修订内容本次未读。

### UK-06 英国电池法规（投放市场条例 2008、废电池条例 2009）　✅ 已核实

- **依据**：The Batteries and Accumulators (Placing on the Market) Regulations 2008；The Waste Batteries and Accumulators Regulations 2009（SI 2009/890）
- **要求**：首次在英国投放电池（含装在产品里的电池）的生产者须登记、承担便携式电池的回收责任（通常加入电池合规计划），电池须满足设计、标记等投放市场要求。
- **适用条件**：产品含任何电池（内置锂电池或纽扣电池），在英国销售。
- **证据形式**：注册 / 备案 / 生产者责任登记。在国家包装废物数据库（NPWD）登记，通常通过电池合规计划。
- **来源**：[legislation.gov.uk：The Waste Batteries and Accumulators Regulations 2009](https://www.legislation.gov.uk/uksi/2009/890/contents) · S · 2026-11-01<br>[GOV.UK：Waste batteries: producer responsibility](https://www.gov.uk/guidance/waste-batteries-producer-responsibility) · A · 2026-11-01<br>[GOV.UK：Regulations: batteries and waste batteries](https://www.gov.uk/guidance/regulations-batteries-and-waste-batteries) · A · 2026-11-01
- **疑点 / 待核实**：Defra 曾就修订电池法规征求意见，结果和新法规状态未查到。

### UK-07 General Product Safety Regulations 2005（大不列颠一般产品安全）　✅ 已核实

- **依据**：The General Product Safety Regulations 2005（SI 2005/1803）；Product Regulation and Metrology Act 2025（授权法）
- **要求**：在大不列颠投放的消费品须安全，生产者须提供警示信息、标注识别信息、配合召回。北爱尔兰自 2024-12-13 起适用欧盟 GPSR。2025 年《产品监管与计量法》已获御准，授权政府以二级立法制定新的产品安全要求（包括在线市场）。
- **适用条件**：所有面向消费者的产品。
- **证据形式**：一般安全义务（无固定证书，靠风险评估和技术文件）。无证书；风险评估和技术文件。
- **来源**：[legislation.gov.uk：The General Product Safety Regulations 2005](https://www.legislation.gov.uk/uksi/2005/1803/contents) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[GOV.UK：General Product Safety Regulations 2005: Great Britain](https://www.gov.uk/government/publications/general-product-safety-regulations-2005/general-product-safety-regulations-2005-great-britain) · A · 2026-11-01<br>[Jones Day：Product Regulation and Metrology Bill receives Royal Assent](https://www.jonesday.com/en/insights/2025/07/product-regulation-and-metrology-bill-receives-royal-assent) · C · 2026-11-01
- **疑点 / 待核实**：《产品监管与计量法》下已经发布了哪些二级立法，未查到。

### UK-12 锂电池运输：Carriage of Dangerous Goods Regulations 2009（ADR 适用于国内运输）与 UN 38.3　✅ 已核实

- **依据**：The Carriage of Dangerous Goods and Use of Transportable Pressure Equipment Regulations 2009（SI 2009/1348）；ADR；空运 ICAO TI，海运 IMDG Code
- **要求**：SI 2009/1348 把 ADR（公路）、RID（铁路）、ADN（内河）的适用范围扩大到英国国内运输（"按不时修订的版本"）。锂电池在 ADR 中属于第 9 类危险货物，运输前须通过 UN 38.3 测试并由制造商和后续分销商提供测试摘要（第三方资料，见 EU-15）。进出英国的空运按 ICAO 技术细则 / IATA DGR，海运按 IMDG Code。
- **适用条件**：产品含锂离子电池或锂金属纽扣电池，运进英国或在英国境内运输。
- **证据形式**：第三方测试（指定或认可的实验室出报告）。同 EU-15：UN 38.3 测试报告和测试摘要向电池供应商索取。
- **来源**：[legislation.gov.uk：SI 2009/1348 The Carriage of Dangerous Goods and Use of Transportable Pressure Equipment Regulations 2009](https://www.legislation.gov.uk/uksi/2009/1348/contents) · S · 2026-11-01<br>[TÜV Rheinland：Lithium batteries transport（2025-01）](https://tuv.com/content-media-files/germany/bs-products/pdfs/other/tuev-rheinland-lithiumbatteries-transport-01-2025-en.pdf) · C · 2026-11-01
- **疑点 / 待核实**：已核实的是 SI 2009/1348 让 ADR 适用于英国国内运输；legislation.gov.uk 提示修订文本可能未完全更新，现行版本没有逐条核对。锂电池具体条款同 EU-15，只有第三方资料。英国民航局（CAA）空运危险品规定本次没查。

## AU · 澳大利亚 RCM

### AU-03 ACMA EMC 要求（EMC 标准 + 标签通知，合规等级 1/2/3）　✅ 已核实

- **依据**：Radiocommunications Labelling (Electromagnetic Compatibility) Notice 2017 及 EMC 标准（立法登记号 F2018L00028，名称待核实）
- **要求**：电子产品须符合适用的 EMC 标准；供应商按设备风险等级（合规等级 1/2/3）保存文件，须先在国家数据库注册为负责供应商，才能加施 RCM 标志。
- **适用条件**：所有在澳大利亚销售的电子产品（含无线产品）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。等级越高要求越多（测试报告、符合性声明）；ACMA 的"等级"与 EESS 的电气安全等级不是一回事。
- **来源**：[Federal Register of Legislation：F2018L00028](https://www.legislation.gov.au/F2018L00028/latest/text) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[EESS：ACMA Requirements – Use of RCM](https://www.eess.gov.au/rcm/acma-requirements-use-of-rcm/) · A · 2026-11-01
- **疑点 / 待核实**：合规等级 1/2/3 各自的具体要求本次没有读到条文；F2018L00028 的正式名称没有确认。

### AU-08 锂电池产品：未查到联邦层面针对小型消费电子的强制标准　⚠️ **待核实**

- **依据**：未查到专门强制标准；适用澳大利亚消费者法一般安全义务
- **要求**：本次没有找到适用于一般小型消费电子内置锂电池的联邦强制安全标准（电动出行设备电池有州层面规定，不在本库范围）。
- **适用条件**：产品内置可充电锂电池，在澳大利亚销售。
- **证据形式**：一般安全义务（无固定证书，靠风险评估和技术文件）。未查到。
- **来源**：[Product Safety Australia：Mandatory standards（强制标准清单入口）](https://www.productsafety.gov.au/product-safety-laws/safety-standards-bans/mandatory-standards) · A · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）
- **疑点 / 待核实**：查过：WebSearch "lithium-ion batteries mandatory standard consumer products Australia 2026"，只找到旧报告和部长声明；需在强制标准清单中再核对。随附的电池充电器若为市电供电，见 AU-04。

### AU-09 锂电池运输：空运按 CASR Part 92 + ICAO 技术细则；陆运按 ADG Code　✅ 已核实

- **依据**：Civil Aviation Safety Regulations 1998 Part 92（危险物品航空运输）；ICAO《危险物品安全航空运输技术细则》；Australian Dangerous Goods Code（ADG Code 7.8，公路 / 铁路）
- **要求**：航空运输危险物品受 CASR Part 92 管辖，其中"技术细则"指 ICAO《危险物品安全航空运输技术细则》；锂电池在技术细则中是危险物品，有包装说明和数量限制，运输前须通过 UN 38.3 测试（第三方资料，澳大利亚原文未单独核实）。公路 / 铁路运输按 ADG Code（第三方资料：7.8 版向国际规则靠拢、增加了锂电池 UN 编号；按特殊规定 188 运输的小电池仍属危险货物，单件含 2 个以上电池或 4 个以上电芯的设备需随附特殊规定 188 要求的文件）。
- **适用条件**：产品含锂离子电池或锂金属纽扣电池，运进澳大利亚或在澳大利亚境内运输。
- **证据形式**：第三方测试（指定或认可的实验室出报告）。UN 38.3 测试报告和测试摘要向电池供应商索取；包装和文件按承运人要求。
- **来源**：[Federal Register of Legislation：F2022N00318（引用 CASR Part 92 与 ICAO 技术细则的 CASA 文书）](https://www.legislation.gov.au/F2022N00318/asmade/2022-12-20/text/original/pdf) · S · 2026-11-01<br>[Master Instruments：Sea and road freight compliance summary（锂电池，IMDG 2018 / ADG）](https://www.master-instruments.com.au/files/knowledge-centre/transportation/lithium_battery_summary_for_sea__road_imdg2018_v3___2020_edn.pdf) · C · 2026-11-01<br>[TT Club：TT Talk - Lithium complexities](https://www.ttclub.com/news-and-resources/news/article/tt-talk-lithium-complexities/) · C · 2026-11-01
- **疑点 / 待核实**：已核实的是"空运受 CASR Part 92 管辖、技术细则指 ICAO 文件"（来自一份引用 Part 92 的 CASA 文书，不是 Part 92 本身）。ADG Code 现行版本和锂电池条款本次没有在 ntc.gov.au 读到，只有第三方摘要；UN 38.3 测试摘要在澳大利亚陆运中的要求未单独核实。
- **备注**：澳大利亚市场的产品安全（非运输）要求见 AU-08。

## 必须找认证机构 / 检测机构确认的事项

- 上面所有标"待核实"的条目；
- 产品归类：是否属于中国 CCC 目录、欧盟通用充电器类别、玩具定义、联网/可连接产品定义；
- 使用已认证无线模组时，整机还需要做哪些测试（中国 SRRC、FCC、RED、ACMA）；
- 测试项目、样机数量、周期和费用。

> **这是资料整理，不是法律意见。** 清单只根据你给出的产品特征，从 `compliance/data/requirements.yaml` 里挑出可能相关的法规条目；是否适用、怎么做，以法规原文和认证机构/检测机构的书面意见为准。标"待核实"的条目尤其要确认。
