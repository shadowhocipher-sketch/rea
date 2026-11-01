# 合规检查清单：(c) 带 BLE 和纽扣电池的儿童玩具

> **这是资料整理，不是法律意见。** 清单只根据你给出的产品特征，从 `compliance/data/requirements.yaml` 里挑出可能相关的法规条目；是否适用、怎么做，以法规原文和认证机构/检测机构的书面意见为准。标"待核实"的条目尤其要确认。

数据查询日期：2026-11-01。数据来源：`compliance/data/requirements.yaml`（共 52 条）。

## 产品特征

| 特征 | 取值 |
|---|---|
| 无线 | ble |
| 联网 | 否 |
| 电池 | coin |
| 随附电源适配器 | 否 |
| 儿童用 | 是 |
| 目标市场 | CN, EU, US, UK, AU |

## 提示

- 产品有无线但标为不联网：如果它通过手机 App 间接上网，欧盟 RED 网络安全条款、CRA、英国 PSTI、澳洲智能设备规则都可能适用，请把 connected 设为 true 再跑一次对比（待核实）。

共 34 条，其中待核实 13 条。

## CN · 中国

### CN-01 SRRC 无线电发射设备型号核准（2.4 GHz / 5 GHz Wi-Fi、蓝牙）　⚠️ **待核实**

- **依据**：工信部《关于加强和规范2400MHz、5100MHz和5800MHz频段无线电管理有关事宜的通知》（工信部无〔2021〕129号）
- **要求**：在 2400–2483.5 MHz、5150–5350 MHz、5725–5850 MHz 频段工作的蓝牙、无线局域网等设备，除微功率短距离设备外，应取得无线电发射设备型号核准证（SRRC），并满足通知附件的技术要求（第三方资料称新增了自适应等测试要求）。5100 MHz 频段限室内使用。
- **适用条件**：产品含 Wi-Fi 或蓝牙等无线发射功能，在中国销售。
- **证据形式**：认证 / 型号核准（由认证机构或主管部门发证）。向工信部无线电管理机构申请型号核准，样机需在指定检测机构测试。用已取得核准的模组时整机是否还要单独核准，待核实。
- **来源**：[工信部无〔2021〕129号 转载 PDF（TI E2E 论坛附件，非官方）](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/968/_E55DE14FE890E0651430_2021_1530_129_F7530A30E55D1A4E8C54E14F6F601653E89073518E4EA0523A5F8C54C4890383_2400MHz_0130_5100MHz_8C54_5800MHz_9198B56BE065BF7E3575A17B0674096773518B4E9C5B84761A90E5770B30_.pdf) · C · 2026-11-01<br>[In Compliance Magazine：MIIT 2021 No. 129 解读](https://incompliancemag.com/chinas-latest-regulation-on-2-4-ghz-and-5-ghz-equipment/) · C · 2026-11-01
- **疑点 / 待核实**：工信部官网原文页面本次未能定位（搜索摘要提到工信部页面的成文日期 2021-09-08、发布日期 2021-10-13，但没给出 URL）。实施和过渡期日期各来源不一致（2022-01-01 起施行、过渡期至 2023-10-15 / 两年）。使用已核准模组的整机是否需要单独核准，需要向检测机构确认。
- **备注**：与 CN-02 一起看：蓝牙低功率设备是否可按微功率设备免核准，是本条最大的疑点。

### CN-02 微功率短距离无线电发射设备目录和技术要求（免型号核准的边界）　⚠️ **待核实**

- **依据**：工业和信息化部公告 2019 年第 52 号《微功率短距离无线电发射设备目录和技术要求》
- **要求**：列入目录且符合技术要求的微功率设备，生产或进口后在国内销售和使用，无需取得无线电频率使用许可、无线电台执照和型号核准，但仍须符合产品质量等法律法规、国家标准和无线电管理规定。
- **适用条件**：产品含无线发射功能，想判断能否按微功率设备免于型号核准（例如低功率 2.4 GHz 私有协议或 BLE）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。免核准不等于免要求：仍须满足目录中对应类别的频率、功率等技术指标，没有统一的证书。
- **来源**：[IT之家 转载公告全文](https://www.ithome.com/0/459/757.htm) · C · 2026-11-01<br>[维基文库：微功率短距离无线电发射设备目录和技术要求](https://zh.wikisource.org/wiki/%E5%BE%AE%E5%8A%9F%E7%8E%87%E7%9F%AD%E8%B7%9D%E7%A6%BB%E6%97%A0%E7%BA%BF%E7%94%B5%E5%8F%91%E5%B0%84%E8%AE%BE%E5%A4%87%E7%9B%AE%E5%BD%95%E5%92%8C%E6%8A%80%E6%9C%AF%E8%A6%81%E6%B1%82) · C · 2026-11-01
- **疑点 / 待核实**：工信部官网原文本次未能定位，只看到转载。目录 2.4 GHz 类别的具体功率限值本次没有读到原文；Wi-Fi / 蓝牙产品是否可以落入微功率类别（与 CN-01 的 129 号通知如何衔接）没把握，必须问检测机构。
- **备注**：公告日期各来源写法不同（2019-11-19 附件 / 2019-11-28 生效）。

### CN-03 CCC 强制性产品认证（产品本体是否在目录内）　⚠️ **待核实**

- **依据**：市场监管总局《强制性产品认证目录描述与界定表（2023年修订）》（2023 年第 36 号公告）及后续调整
- **要求**：列入 CCC 目录的产品，未获得认证证书（或按规定完成自我声明）并加施 CCC 标志的，不得出厂、销售、进口。2023 年修订版共 16 大类 96 种产品，部分产品实行自我声明程序 A / B；2024 年后目录又有增补。
- **适用条件**：任何在中国销售的电子产品都要先按《描述与界定表》判断本体是否属于目录产品（例如信息技术设备、音视频设备）。
- **证据形式**：认证 / 型号核准（由认证机构或主管部门发证）。目录内产品由指定认证机构认证，或按目录标注走自我声明（报送系统 sdoc.cnca.cn）；目录外产品不需要 CCC。
- **来源**：[香港工业贸易署转载：强制性产品认证目录描述与界定表（2023年修订）公告](https://www.tid.gov.hk/english/aboutus/tradecircular/cic/asia/2023/files/ci2023659a.pdf) · A · 2026-11-01<br>[汕头市政府文件（提到截至 2024 年底目录为 16 大类 105 种）](https://www.shantou.gov.cn/attachment/0/135/135589/2446285.docx) · A · 2026-11-01
- **疑点 / 待核实**：认监委官网（cnca.gov.cn）原文附件本次无法访问，没有读到具体条目。USB 供电的小型桌面电子产品 是否落入"信息技术设备""音视频设备"等目录类别，取决于产品功能和界定表的描述，必须让认证机构判断。
- **备注**：产品本体不在目录内时，其随附的适配器（CN-04）、内置锂电池（CN-05）仍可能各自需要 CCC。

### CN-06 CCC：玩具（含电玩具），新版实施规则 CNCA-C22-02:2026　✅ 已核实

- **依据**：国家认监委 2026 年第 8 号公告；《强制性产品认证实施规则 玩具》CNCA-C22-02:2026；GB 6675 系列（2025 版，第三方资料）
- **要求**：属于 CCC 目录的玩具须取得 CCC 证书。2026-11-01 起，CCC 认证活动应当按新版实施规则开展；已颁发的有效证书可继续使用，通过变更、到期换证等方式逐步转换。
- **适用条件**：产品面向儿童、属于玩具（第三方资料称适用于面向 14 岁以下儿童的电玩具、塑胶玩具、金属玩具、弹射玩具等目录类别）。
- **证据形式**：认证 / 型号核准（由认证机构或主管部门发证）。由指定认证机构按实施规则做型式试验 + 工厂检查，发 CCC 证书。
- **来源**：[香港工业贸易署转载：国家认监委关于发布电动自行车、童车、玩具 CCC 实施规则的公告（2026）](https://www.tid.gov.hk/en/tradecircular/files/2026/ci4972026a.pdf) · A · 2026-11-01<br>[STC：New CCC Implementation Rules for Electric Bicycles, Toys, and Children's Vehicle Products](https://stc.group/en/media/detail/2380) · C · 2026-11-01
- **疑点 / 待核实**：公告日期两个来源写法不同（2026-05-29 / 2026-05-31）；产品是否属于"玩具"目录类别需按界定表判断；新版 GB 6675 的版本号仅来自第三方。
- **备注**：今天（2026-11-01）正好是新规则强制执行日，新申请按新规则做。

### CN-07 中国 RoHS：电器电子产品有害物质限制使用　⚠️ **待核实**

- **依据**：《电器电子产品有害物质限制使用管理办法》；《电器电子产品有害物质限制使用达标管理目录（2026年版）》；GB 26572—2025（2027-08-01 实施）
- **要求**：电器电子产品须按标准标注有害物质信息（RoHS 标识、信息披露）；列入达标管理目录的产品还须满足限量要求并纳入合格评定。2026 年版目录共 33 种产品，新增产品管控要求 2027-08-01 起实施。
- **适用条件**：所有在中国销售的电器电子产品（标识义务）；是否属于达标管理目录的 33 种产品需单独判断。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。标识和信息披露由企业自行完成；目录内产品的合格评定方式（自我声明或认证）待核实。
- **来源**：[国家科技传播中心网站：达标管理目录（2026年版）相关公告](https://www.ncsti.gov.cn/kjdt/tzgg/202605/t20260528_248133.html) · A · 2026-11-01<br>[ChemLinked：达标管理目录（2026 版）英文翻译](https://chemical.chemlinked.com/translation/qualification-management-catalogue-for-the-restriction-of-hazardous-substances-in-electrical-appliances-and-electronic-products-2026-version) · C · 2026-11-01
- **疑点 / 待核实**：工信部原文和目录附件本次无法访问，33 种产品的具体名单没有读到（第三方称新增智能手环等）；旧标准 SJ/T 11364、GB/T 26572-2011 与 GB 26572—2025 的过渡安排没查到官方说明。
- **备注**：物料选型时就要求供应商提供符合限量要求的声明或检测报告，省得后面补。

### CN-08 纽扣电池：未查到中国针对"含纽扣电池产品"的专门强制要求　⚠️ **待核实**

- **依据**：未查到
- **要求**：本次没有找到中国市场监管总局发布的、针对含纽扣电池产品防误吞（电池仓固定、警示标签等）的专门强制性国家标准。玩具类产品的电池要求在玩具 CCC（CN-06）所用的 GB 6675 / 电玩具标准中。
- **适用条件**：产品使用纽扣/硬币电池，在中国销售。
- **证据形式**：未确定。未查到。
- **来源**：[国家标准全文公开系统（建议在此按'纽扣电池'检索）](https://openstd.samr.gov.cn/) · S · 2026-11-01
- **疑点 / 待核实**：查过：WebSearch 中文检索"纽扣电池 强制性国家标准 儿童 误吞"，结果只有澳大利亚和美国的资料。不能据此认为中国没有要求，需要认证机构确认。
- **备注**：即便没有专门要求，也建议参照 AU-05 / US-05 的做法设计电池仓（螺丝固定）和警示。

## EU · 欧盟 CE

### EU-01 无线电设备指令 RED 2014/53/EU（安全、EMC、频谱）　✅ 已核实

- **依据**：Directive 2014/53/EU（RED）
- **要求**：无线电设备须满足基本要求：健康与安全（第 3(1)(a) 条，无低电压下限）、电磁兼容（第 3(1)(b) 条）、有效使用无线电频谱（第 3(2) 条）；编制技术文件、签发欧盟符合性声明、加施 CE 标志。
- **适用条件**：产品含任何有意发射/接收无线电的功能（Wi-Fi、BLE、NFC 等）。含无线的产品走 RED，不再单独适用 EMC 指令和 LVD。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。完整采用协调标准时可按附件 II（内部生产控制）自我声明；第 3(2) 条未完整采用协调标准时须公告机构参与（附件 III / IV）。
- **来源**：[EUR-Lex：Directive 2014/53/EU](https://eur-lex.europa.eu/eli/dir/2014/53/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[European Commission：Radio Equipment Directive (RED)](https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en) · A · 2026-11-01
- **备注**：用已有 CE 资料的无线模组，整机仍需自己做 RED 评估（模组报告可以复用一部分）。

### EU-03 RED 网络安全授权法规（第 3(3)(d)(e)(f) 条）　✅ 已核实

- **依据**：Delegated Regulation (EU) 2022/30；被 Delegated Regulation (EU) 2026/339 废止，废止自 2027-12-11 生效
- **要求**：自 2025-08-01 起，能直接或间接联网的无线电设备、以及玩具类/儿童看护类/可穿戴类无线电设备，须满足网络保护、个人数据与隐私保护、防欺诈的基本要求。协调标准为 EN 18031-1/-2/-3（部分条款有限制）。2026/339 号授权法规于 2026-04-29 公布，自 2027-12-11 起废止 2022/30，届时由网络韧性法案（EU-04）接管；2025-08-01 至 2027-12-10 投放的设备仍按 2022/30 监管。
- **适用条件**：产品含无线电功能，并且（能直接或间接联网，或是玩具/儿童看护/可穿戴设备）。2027-12-11 之前投放市场的产品。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。完整采用 EN 18031 且未落入其限制条款时可自我声明；否则须公告机构参与。
- **来源**：[EUR-Lex：Delegated Regulation (EU) 2022/30](https://eur-lex.europa.eu/eli/reg_del/2022/30/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[EUR-Lex：Delegated Regulation (EU) 2026/339（废止 2022/30）](https://eur-lex.europa.eu/eli/reg_del/2026/339/oj/eng) · S · 2026-11-01<br>[European Commission：Radio Equipment Directive (RED)（含网络安全转入 CRA 的说明）](https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en) · A · 2026-11-01
- **疑点 / 待核实**：只通过 BLE 连手机、由 App 上网的设备算不算'间接联网'，需要按委员会指南和认证机构意见判断。
- **备注**：2027-12-11 以后投放的产品转为按 CRA 评估，现在立项的产品两边都要规划。

### EU-04 网络韧性法案 CRA（带数字元素的产品）　⚠️ **待核实**

- **依据**：Regulation (EU) 2024/2847（Cyber Resilience Act）
- **要求**：带数字元素、有数据连接的产品须满足设计开发阶段的网络安全基本要求和全生命周期漏洞处理要求，加施 CE 标志。2024-12-10 生效，2027-12-11 全面适用；第三方资料称主动被利用漏洞和严重事件的报告义务自 2026-09-11 起适用，且覆盖已上市产品。
- **适用条件**：产品有直接或间接的数据连接（Wi-Fi、BLE，可能也包括有线数据接口）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。默认类别可自我评估；附件 III"重要"类和附件 IV"关键"类产品评估更严格。产品属于哪一类待核实。
- **来源**：[EUR-Lex：Regulation (EU) 2024/2847](https://eur-lex.europa.eu/eli/reg/2024/2847/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[European Parliament Legislative Observatory：Cyber Resilience Act 摘要](https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1796083) · A · 2026-11-01<br>[Jones Day：CRA 24 小时报告义务 2026-09-11 起](https://www.jonesday.com/en/insights/2026/07/eu-cyber-resilience-act-24hour-reporting-duties-start-september-11-2026) · C · 2026-11-01
- **疑点 / 待核实**：2026-09-11 报告义务日期只来自第三方（多家一致，但没读到条款原文）；只有 USB 数据口、没有无线的产品是否属于"有数据连接"没把握。
- **备注**：报告义务现在已经生效（按第三方资料），已上市的联网产品也要有漏洞处理流程。

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

### EU-13 玩具安全：指令 2009/48/EC → 新法规 (EU) 2025/2509　⚠️ **待核实**

- **依据**：Directive 2009/48/EC；Regulation (EU) 2025/2509（Toy Safety Regulation）
- **要求**：供 14 岁以下儿童玩耍的产品须满足玩具安全基本要求（物理机械、可燃性、化学、电气等），签发符合性声明、加施 CE、附警示。新法规 (EU) 2025/2509 于 2025-12-12 公布，多数资料称 2030-08-01 起全面取代 2009/48/EC，在此之前符合旧指令的玩具仍可投放。
- **适用条件**：产品设计或预期供 14 岁以下儿童玩耍。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。完整采用协调标准（EN 71 系列、电玩具标准）时可自我声明；否则需要欧盟型式检验（公告机构）。
- **来源**：[EUR-Lex：Directive 2009/48/EC](https://eur-lex.europa.eu/eli/dir/2009/48/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[EUR-Lex：Regulation (EU) 2025/2509](https://eur-lex.europa.eu/eli/reg/2025/2509/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[European Commission：Toy safety](https://single-market-economy.ec.europa.eu/sectors/toys/toy-safety_en) · A · 2026-11-01
- **疑点 / 待核实**：新法规的适用和过渡日期各来源冲突（2026-01-01 生效；2026-08-01 / 2030-08-01 适用），以 EUR-Lex 原文为准。新法规对数字产品护照等新义务的生效日未读到。
- **备注**：带无线功能的玩具还落入 EU-03（RED 网络安全授权法规中的玩具类）。

### EU-14 纽扣电池：未查到欧盟专门针对"含纽扣电池产品"的强制法规　⚠️ **待核实**

- **依据**：未查到专门法规；由 GPSR (EU) 2023/988 一般安全要求、玩具安全法规、电池法规覆盖
- **要求**：本次没有找到类似美国 Reese's Law 的欧盟专门法规。纽扣电池误吞风险由 GPSR 一般安全义务覆盖，玩具中的电池可触及性由玩具安全要求覆盖。
- **适用条件**：产品使用纽扣/硬币电池，在欧盟销售。
- **证据形式**：一般安全义务（无固定证书，靠风险评估和技术文件）。风险评估中写明电池仓固定方式和警示。
- **来源**：[EUR-Lex：Regulation (EU) 2023/988（GPSR）](https://eur-lex.europa.eu/eli/reg/2023/988/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）
- **疑点 / 待核实**：是否有欧盟层面的纽扣电池专门标准化委托或协调标准正在实施，没查到官方页面。

## US · 美国 FCC / CPSC

### US-01 FCC Part 15 Subpart C 有意辐射体：设备认证（Certification）　✅ 已核实

- **依据**：47 CFR Part 15 Subpart C；47 CFR 2.907（Certification）
- **要求**：Wi-Fi、蓝牙等有意辐射体在销售前须取得 FCC 认证：由 FCC 认可的实验室测试，经 TCB（电信认证机构）审核后发 FCC ID 授权；产品标注 FCC ID 和 Part 15 声明（47 CFR 15.19）。
- **适用条件**：产品含无线发射功能，在美国销售。
- **证据形式**：认证 / 型号核准（由认证机构或主管部门发证）。整机自带射频设计时自己申请 FCC ID；使用已认证模组时见 US-02。
- **来源**：[eCFR：47 CFR Part 15 Subpart C—Intentional Radiators](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C) · S · 2026-11-01<br>[FCC：Certification (47 CFR Section 2.907)](https://www.fcc.gov/node/23689) · A · 2026-11-01
- **疑点 / 待核实**：2025 年起 FCC 对"受管控清单"相关实体和测试实验室有新的限制（第三方资料），选实验室时确认。

### US-02 使用已认证模组（模块化批准）的条件　✅ 已核实

- **依据**：47 CFR 15.212（Modular transmitters）；FCC KDB 996369（模组集成指南）
- **要求**：使用已取得模块化批准的无线模组时，整机通常不需要重新做有意辐射体认证，但须：按模组授权书的条件安装（天线、布线、RF 暴露限制等），模组 FCC ID 在整机外部不可见时，在整机外部标注"Contains FCC ID: xxx"或同义文字；整机作为数字设备仍需满足 Part 15 Subpart B（US-03）。有限模块化批准（LMA）只适用于授权书限定的主机。模组被封闭且不可即插即换、或不满足授权条件时，整机需要新的 FCC ID。
- **适用条件**：产品使用已认证的 Wi-Fi/BLE 模组（例如 ESP32 系列模组），在美国销售。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。整机厂负责按授权条件集成并保留证据；需要变更时做 Class II 许可变更或新认证。
- **来源**：[eCFR：47 CFR 15.212 Modular transmitters](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.212) · S · 2026-11-01<br>[Ezurio（原 Laird）：FCC Guidance for Incorporating Transmitter Modules（引用 KDB 996369）](https://www.ezurio.com/resources/white-papers/fcc-guidance-on-transmitter-modules) · C · 2026-11-01
- **疑点 / 待核实**：KDB 996369 各分册（D01/D04 等）的现行版本号没有在 FCC 官网核对（KDB 站点本次无法访问）。
- **备注**：选模组时看授权书（Grant）里的条件和天线类型；改天线常常就不满足条件了。

### US-03 FCC Part 15 Subpart B 无意辐射体（数字设备）：SDoC　⚠️ **待核实**

- **依据**：47 CFR Part 15 Subpart B；47 CFR 2.906（Supplier's Declaration of Conformity）
- **要求**：含数字电路（有时钟）的设备属于无意辐射体，B 类（家用）数字设备一般走供应商符合性声明（SDoC）：自行测试合规、由美国境内的负责方保存记录、产品附合规信息；不需要向 FCC 提交。也可以选择走认证。
- **适用条件**：所有含数字电路的电子产品（Part 15 有豁免条款，见疑点）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。由实验室按 Part 15 B 类限值测试，负责方保存测试报告和 SDoC。
- **来源**：[eCFR：47 CFR Part 15 Subpart B—Unintentional Radiators](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-B) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[eCFR：47 CFR Part 2 Subpart J—Equipment Authorization Procedures（含 2.906）](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-2/subpart-J) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[Cornell LII：47 CFR 2.906（镜像）](https://www.law.cornell.edu/cfr/text/47/2.906) · C · 2026-11-01
- **疑点 / 待核实**：Part 15 Subpart B 的设备分类表和豁免条款（例如低功耗或特定用途的数字设备）本次没有读到原文；电池供电的小设备是否落入豁免，需要实验室判断。
- **备注**：带无线的产品，非无线部分（数字电路）同样要做 Subpart B 评估。

### US-05 CPSC Reese's Law：含纽扣/硬币电池的消费品（16 CFR part 1263）　✅ 已核实

- **依据**：16 CFR part 1263（采纳 ANSI/UL 4200A-2023 并附加要求）
- **要求**：2023-10-23 及以后制造或进口、含纽扣/硬币电池的消费品须：电池仓在可预见使用和误用下保持固定（防儿童打开）、通过性能测试、产品和包装带警示标签和说明。锌空电池不适用第 1263 部分。电池本身的包装须符合防毒包装法。儿童产品须由 CPSC 认可的第三方实验室测试（2023-12-20 起）。
- **适用条件**：产品使用纽扣/硬币电池（直径大于高度的单体电池），在美国销售。
- **证据形式**：第三方测试（指定或认可的实验室出报告）。普通消费品：一般符合性证书（GCC），可自测；儿童产品：第三方测试 + 儿童产品证书（CPC）。
- **来源**：[Federal Register 2023-20334：Safety Standard for Button Cell or Coin Batteries（最终规则）](https://www.govinfo.gov/content/pkg/FR-2023-09-21/html/2023-20334.htm) · S · 2026-11-01<br>[CPSC：Button Cell and Coin Battery（企业指南）](https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Button-Cell-and-Coin-Battery) · A · 2026-11-01<br>[CPSC：Button Cell and Coin Battery FAQs](https://www.cpsc.gov/FAQ/Button-Cell-and-Coin-Battery-FAQs) · A · 2026-11-01
- **疑点 / 待核实**：符合 ASTM F963 电池要求的玩具是否豁免第 1263 部分，只在第三方资料中看到，需按 CPSC 原文确认；2026 年有修订自愿标准的征求意见（Federal Register 公示），结果未知。

### US-06 CPSIA 儿童产品：第三方测试、儿童产品证书、追踪标签；玩具 ASTM F963　✅ 已核实

- **依据**：Consumer Product Safety Improvement Act；16 CFR part 1250（玩具安全，采纳 ASTM F963）
- **要求**：主要供 12 岁及以下儿童使用的产品，须由 CPSC 认可的第三方实验室按适用规则测试，进口商或美国制造商据此签发 儿童产品证书（CPC）；产品和包装须（在可行时）永久标注追踪标签。玩具须符合 ASTM F963。
- **适用条件**：产品面向 12 岁及以下儿童，在美国销售。
- **证据形式**：第三方测试（指定或认可的实验室出报告）。CPSC 认可实验室（按测试项目逐项认可）测试；CPC 由进口商/制造商签发，不由实验室签发。
- **来源**：[eCFR：16 CFR Part 1250—Safety Standard Mandating ASTM F963 for Toys](https://www.ecfr.gov/current/title-16/chapter-II/subchapter-B/part-1250) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[CPSC：FAQs Certification and Third Party Testing](https://www.cpsc.gov/Business--Manufacturing/Testing-Certification/Third-Party-Testing/FAQs-Certification-and-Third-Party-Testing-OLD) · A · 2026-11-01<br>[CPSC 讲义：Key Procedural Requirements（2016）](https://cpsc.gov/s3fs-public/Session-2-CPSC-Key-Procedural-Requirements-China-2016-Williams-FINAL-Eng.pdf) · A · 2026-11-01
- **疑点 / 待核实**：现行 ASTM F963 的强制版本（第三方称 F963-23）没有在 CPSC 官方页面上核对；本次找到的 CPSC 页面部分是旧版（URL 带 OLD）。
- **备注**：带纽扣电池的儿童产品同时看 US-05。

### US-08 锂电池运输：49 CFR 173.185 与 UN 38.3 测试摘要　✅ 已核实

- **依据**：49 CFR 173.185；UN《试验和标准手册》第三部分 38.3
- **要求**：锂电池（含锂离子和锂金属纽扣电池）运输前须通过 UN 38.3 测试；2008-01-01 及以后制造的锂电芯/电池，其制造商和后续分销商须提供测试摘要（test summary）。含电池的设备运输有包装、标记和数量方面的要求和例外。
- **适用条件**：产品含锂离子电池，或含锂金属纽扣电池（如 CR 系列），需要运输（含快递、空运）。
- **证据形式**：第三方测试（指定或认可的实验室出报告）。向电池供应商索取 UN 38.3 测试报告和测试摘要；整机包装按承运方要求。
- **来源**：[eCFR：49 CFR 173.185 Lithium cells and batteries](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-E/section-173.185) · S · 2026-11-01<br>[PHMSA：Lithium Battery Test Summary (2024)](https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2024-09/Lithium-Battery-Test-Summary-2024.pdf) · A · 2026-11-01
- **疑点 / 待核实**：小型消费设备的例外条款（173.185(c) 等）现行文本没有读到；空运还要看 IATA DGR，本库未展开。碱性/锌空纽扣电池不属于锂电池。
- **备注**：运输要求实际上在所有市场都适用（国际空运按 IATA/ICAO），这里只列美国法规。

## UK · 英国 UKCA

### UK-01 Radio Equipment Regulations 2017（英国无线电设备条例）　✅ 已核实

- **依据**：The Radio Equipment Regulations 2017（SI 2017/1206）
- **要求**：无线电设备须满足安全、EMC、有效使用频谱等基本要求，制造商编制技术文件和符合性声明，加施 UKCA 标志（大不列颠）；北爱尔兰按欧盟规则使用 CE。
- **适用条件**：产品含无线电功能，在英国销售。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。与 EU RED 类似：采用指定标准可自我声明，否则需要英国批准机构。
- **来源**：[legislation.gov.uk：The Radio Equipment Regulations 2017](https://www.legislation.gov.uk/uksi/2017/1206/contents) · S · 2026-11-01<br>[GOV.UK：Radio Equipment Regulations 2017: Great Britain（法定指南）](https://www.gov.uk/government/publications/radio-equipment-regulations-2017/radio-equipment-regulations-2017-great-britain) · A · 2026-11-01<br>[GOV.UK：UK Government announces extension of CE mark recognition for businesses](https://www.gov.uk/government/news/uk-government-announces-extension-of-ce-mark-recognition-for-businesses) · A · 2026-11-01
- **疑点 / 待核实**：英国政府宣布对其主管的多部产品法规"无限期"继续承认 CE 标志，但本次没有读到覆盖清单，Radio Equipment Regulations 2017 是否在内待核实。
- **备注**：在大不列颠可否只用 CE 标志，以 GOV.UK 清单为准。

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

### UK-08 Toys (Safety) Regulations 2011　✅ 已核实

- **依据**：The Toys (Safety) Regulations 2011（SI 2011/1881）
- **要求**：玩具须满足安全要求，制造商编制技术文件和符合性声明、加施 UKCA（或按承认安排加施 CE）、附警示。2026-02-13 英国更新了指定标准清单（部分条目有宽限期）。
- **适用条件**：产品设计或预期供 14 岁以下儿童玩耍，在英国销售。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。采用指定标准时自我声明；否则需要英国批准机构型式检验。
- **来源**：[legislation.gov.uk：The Toys (Safety) Regulations 2011](https://www.legislation.gov.uk/uksi/2011/1881/contents) · S · 2026-11-01<br>[GOV.UK：Toys (Safety) Regulations 2011: Great Britain（法定指南）](https://www.gov.uk/government/publications/toys-safety-regulations-2011/toys-safety-regulations-2011-great-britain) · A · 2026-11-01
- **疑点 / 待核实**：14 岁年龄界限沿用欧盟玩具指令定义，本次没有在英国条例原文中逐字核对。

### UK-10 纽扣电池：未查到英国专门强制法规（PAS 7055 为自愿标准）　⚠️ **待核实**

- **依据**：无专门法规；General Product Safety Regulations 2005；PAS 7055（BSI，自愿）
- **要求**：本次没有找到英国针对含纽扣电池产品的专门强制法规；纽扣电池安全由 GPSR 2005 一般安全义务覆盖。OPSS 支持制定的 PAS 7055 规定了电池、包装和含电池产品的安全要求，属于自愿标准。
- **适用条件**：产品使用纽扣/硬币电池，在英国销售。
- **证据形式**：一般安全义务（无固定证书，靠风险评估和技术文件）。风险评估时参考 PAS 7055。
- **来源**：[GOV.UK：OPSS supports new standard for battery safety](https://www.gov.uk/government/news/opss-support-new-standard-for-battery-safety) · A · 2026-11-01
- **疑点 / 待核实**：《产品监管与计量法》2025 授权的二级立法中是否已有纽扣电池规则，未查到。

## AU · 澳大利亚 RCM

### AU-01 ACMA 低干扰潜力设备（LIPD）类别许可（使用条件）　✅ 已核实

- **依据**：Radiocommunications (Low Interference Potential Devices) Class Licence 2025；Radiocommunications Act 1992
- **要求**：Wi-Fi、蓝牙等低干扰设备在类别许可规定的频段和最大功率内使用，无需单独申请执照；2025-10-01 起施行，取代 2015 版。
- **适用条件**：产品含 Wi-Fi / BLE 等短距离无线，在澳大利亚使用和销售。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。设计时确认频段和功率在类别许可范围内；供应端义务见 AU-02。
- **来源**：[ACMA：Low interference potential devices (LIPD) class licence](https://www.acma.gov.au/licences/low-interference-potential-devices-lipd-class-licence) · A · 2026-11-01
- **疑点 / 待核实**：类别许可原文（legislation.gov.au）本次没有找到登记号。

### AU-02 ACMA 无线设备供应方义务（技术标准、符合性声明、RCM）　⚠️ **待核实**

- **依据**：ACMA 设备规则和短距离设备标准（采纳 AS/NZS 4268）
- **要求**：供应无线设备前须证明符合适用的技术标准，保存符合性记录、签发供应商符合性声明，注册为负责供应商并加施 RCM 标志。
- **适用条件**：产品含无线功能，在澳大利亚销售。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。通常用测试报告（可用国际标准测试）+ 供应商符合性声明；在 EESS 国家数据库注册为负责供应商。
- **来源**：[EESS：ACMA Requirements – Use of RCM](https://www.eess.gov.au/rcm/acma-requirements-use-of-rcm/) · A · 2026-11-01<br>[ACMA：LIPD class licence](https://www.acma.gov.au/licences/low-interference-potential-devices-lipd-class-licence) · A · 2026-11-01
- **疑点 / 待核实**：设备规则（Radiocommunications Equipment (General) Rules 2021）和短距离设备标准的原文、合规等级划分本次没有读到；AS/NZS 4268 的引用来自第三方。

### AU-03 ACMA EMC 要求（EMC 标准 + 标签通知，合规等级 1/2/3）　✅ 已核实

- **依据**：Radiocommunications Labelling (Electromagnetic Compatibility) Notice 2017 及 EMC 标准（立法登记号 F2018L00028，名称待核实）
- **要求**：电子产品须符合适用的 EMC 标准；供应商按设备风险等级（合规等级 1/2/3）保存文件，须先在国家数据库注册为负责供应商，才能加施 RCM 标志。
- **适用条件**：所有在澳大利亚销售的电子产品（含无线产品）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。等级越高要求越多（测试报告、符合性声明）；ACMA 的"等级"与 EESS 的电气安全等级不是一回事。
- **来源**：[Federal Register of Legislation：F2018L00028](https://www.legislation.gov.au/F2018L00028/latest/text) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[EESS：ACMA Requirements – Use of RCM](https://www.eess.gov.au/rcm/acma-requirements-use-of-rcm/) · A · 2026-11-01
- **疑点 / 待核实**：合规等级 1/2/3 各自的具体要求本次没有读到条文；F2018L00028 的正式名称没有确认。

### AU-05 纽扣/硬币电池强制安全标准和信息标准（2022-06-22 起强制）　✅ 已核实

- **依据**：Consumer Goods (Products Containing Button/Coin Batteries) Safety Standard 2020；Consumer Goods (Products Containing Button/Coin Batteries) Information Standard 2020（及电池本身的两项标准）
- **要求**：含纽扣/硬币电池的消费品须有安全的电池仓（例如需要工具才能打开）、通过规定测试，并在产品、包装和说明书上提供警示信息。电池本身另有包装要求。焊接固定在通信设备中的电池等有例外。
- **适用条件**：产品使用纽扣/硬币电池，在澳大利亚销售。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。供应商须确保合规；是否强制第三方测试待核实（本次只读到摘要）。
- **来源**：[Federal Register of Legislation：F2020L01658（解释性说明）](https://www.legislation.gov.au/F2020L01658/asmade/2020-12-21/es/original/pdf) · S · 2026-11-01<br>[Product Safety Australia：Button coin battery safety – a guide for business（PDF）](https://www.productsafety.gov.au/system/files/Button%20coin%20battery%20safety%20-%20a%20guide%20for%20business%20on%20the%20application%20of%20mandatory%20standards_2.pdf) · A · 2026-11-01
- **疑点 / 待核实**：安全标准正文的具体测试条款本次没有读到，只读到摘要；F2020L01658 对应四项标准中的哪一项未逐一核对。

### AU-06 36 个月及以下儿童玩具强制安全标准（小零件）　✅ 已核实

- **依据**：Consumer Goods (Toys for Children up to and including 36 Months of Age) Safety Standard 2023
- **要求**：供 36 个月及以下儿童的玩具不得含有可被小零件圆筒容纳的小零件（防窒息），并对含电池玩具有专门要求。
- **适用条件**：产品是面向 36 个月及以下儿童的玩具（更大年龄段的玩具还可能涉及其他强制标准，见疑点）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。供应商须确保合规；建议做第三方测试留证。
- **来源**：[Product Safety Australia：Toys for children up to and including 36 months of age（强制标准）](https://www.productsafety.gov.au/product-safety-laws/safety-standards-bans/mandatory-standards/toys-for-children-up-to-and-including-36-months-of-age) · A · 2026-11-01
- **疑点 / 待核实**：面向更大年龄儿童的玩具适用哪些强制标准（例如含磁铁、弹射、水上玩具等专项标准）本次没有逐一检索。
- **备注**：带纽扣电池的玩具同时看 AU-05。

## 必须找认证机构 / 检测机构确认的事项

- 上面所有标"待核实"的条目；
- 产品归类：是否属于中国 CCC 目录、欧盟通用充电器类别、玩具定义、联网/可连接产品定义；
- 使用已认证无线模组时，整机还需要做哪些测试（中国 SRRC、FCC、RED、ACMA）；
- 测试项目、样机数量、周期和费用。

> **这是资料整理，不是法律意见。** 清单只根据你给出的产品特征，从 `compliance/data/requirements.yaml` 里挑出可能相关的法规条目；是否适用、怎么做，以法规原文和认证机构/检测机构的书面意见为准。标"待核实"的条目尤其要确认。
