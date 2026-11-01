# 合规检查清单：(d) 带电源适配器的 Wi-Fi 设备

> **这是资料整理，不是法律意见。** 清单只根据你给出的产品特征，从 `compliance/data/requirements.yaml` 里挑出可能相关的法规条目；是否适用、怎么做，以法规原文和认证机构/检测机构的书面意见为准。标"待核实"的条目尤其要确认。

数据查询日期：2026-11-01。数据来源：`compliance/data/requirements.yaml`（共 57 条）。

## 产品特征

| 特征 | 取值 |
|---|---|
| 无线 | wifi |
| 联网 | 是 |
| 电池 | 无 |
| 随附电源适配器 | 是 |
| 儿童用 | 否 |
| 目标市场 | CN, EU, US, UK, AU |

共 32 条，其中待核实 14 条。

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

### CN-04 CCC：随附电源适配器 / 充电器　⚠️ **待核实**

- **依据**：强制性产品认证目录（电源适配器类产品），实施规则 CNCA-C09-01:2023《强制性产品认证实施规则 电子产品及安全附件》
- **要求**：随产品销售的电源适配器 / 充电器如属于 CCC 目录产品，须有 CCC 证书并加施标志。
- **适用条件**：产品包装内随附交流供电的电源适配器或充电器，在中国销售。
- **证据形式**：认证 / 型号核准（由认证机构或主管部门发证）。通常直接采购已有 CCC 证书的适配器，并保存证书；自己设计适配器则需要认证。
- **来源**：[香港工业贸易署转载：CCC 目录描述与界定表（2023年修订）公告](https://www.tid.gov.hk/english/aboutus/tradecircular/cic/asia/2023/files/ci2023659a.pdf) · A · 2026-11-01<br>[Raspberry Pi 27W 电源 CCC 证书（示例：按 CNCA-C09-01:2023 认证的适配器）](https://pip.raspberrypi.com/categories/900-approvals/documents/RP-005300-CF/rpi-27W-PSU-China.pdf) · C · 2026-11-01
- **疑点 / 待核实**：没有读到界定表中适配器条目的原文和适用电压/功率范围；目前的依据是厂商证书示例和转载公告。
- **备注**：采购现成适配器时，核对证书上的型号与实物一致、证书有效。

### CN-07 中国 RoHS：电器电子产品有害物质限制使用　⚠️ **待核实**

- **依据**：《电器电子产品有害物质限制使用管理办法》；《电器电子产品有害物质限制使用达标管理目录（2026年版）》；GB 26572—2025（2027-08-01 实施）
- **要求**：电器电子产品须按标准标注有害物质信息（RoHS 标识、信息披露）；列入达标管理目录的产品还须满足限量要求并纳入合格评定。2026 年版目录共 33 种产品，新增产品管控要求 2027-08-01 起实施。
- **适用条件**：所有在中国销售的电器电子产品（标识义务）；是否属于达标管理目录的 33 种产品需单独判断。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。标识和信息披露由企业自行完成；目录内产品的合格评定方式（自我声明或认证）待核实。
- **来源**：[国家科技传播中心网站：达标管理目录（2026年版）相关公告](https://www.ncsti.gov.cn/kjdt/tzgg/202605/t20260528_248133.html) · A · 2026-11-01<br>[ChemLinked：达标管理目录（2026 版）英文翻译](https://chemical.chemlinked.com/translation/qualification-management-catalogue-for-the-restriction-of-hazardous-substances-in-electrical-appliances-and-electronic-products-2026-version) · C · 2026-11-01
- **疑点 / 待核实**：工信部原文和目录附件本次无法访问，33 种产品的具体名单没有读到（第三方称新增智能手环等）；旧标准 SJ/T 11364、GB/T 26572-2011 与 GB 26572—2025 的过渡安排没查到官方说明。
- **备注**：物料选型时就要求供应商提供符合限量要求的声明或检测报告，省得后面补。

### CN-09 联网设备：个人信息保护；未查到消费类物联网网络安全强制标准　⚠️ **待核实**

- **依据**：《中华人民共和国个人信息保护法》（2021-11-01 施行）
- **要求**：设备或配套 App 处理个人信息时，适用个人信息保护法（告知同意、最小必要等处理规则和处理者义务）。本次没有找到类似英国 PSTI、澳洲智能设备规则那样针对消费类联网设备的强制性网络安全国家标准。
- **适用条件**：产品联网（直接或经手机 App），并收集、处理用户个人信息。
- **证据形式**：一般安全义务（无固定证书，靠风险评估和技术文件）。个人信息保护属于运营义务（隐私政策、同意机制、安全措施），没有产品证书。
- **来源**：[国家互联网信息办公室：中华人民共和国个人信息保护法（全文）](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) · S · 2026-11-01
- **疑点 / 待核实**：是否存在适用于消费类联网设备的强制性网络安全国家标准或认证（例如网络关键设备目录之外的消费产品），本次检索未查到，需要确认。
- **备注**：如果设备接入电信网络（蜂窝），还涉及电信设备进网许可——本库只覆盖 Wi-Fi / BLE，未展开。

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

### EU-06 低电压指令 LVD 2014/35/EU（随附市电适配器）　✅ 已核实

- **依据**：Directive 2014/35/EU
- **要求**：额定电压在交流 50–1000 V、直流 75–1500 V 范围内的电气设备须安全，签发符合性声明并加施 CE 标志。
- **适用条件**：随附交流市电输入的电源适配器。产品本体若只由 5 V USB 供电且无无线，则低于 LVD 电压范围，安全由 GPSR（EU-12）覆盖。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。内部生产控制。采购现成适配器时保存其 CE 符合性声明和测试报告。
- **来源**：[EUR-Lex：Directive 2014/35/EU](https://eur-lex.europa.eu/eli/dir/2014/35/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[BAuA（德国联邦职业安全与健康研究所）：Scope of the Low Voltage Directive](https://www.baua.de/EN/Topics/Work-design/Safe-products/Electrical-products/Requirements/Application-field) · A · 2026-11-01
- **疑点 / 待核实**：随附的第三方适配器，整机厂作为"投放者"要承担哪些文件义务，按认证机构意见。

### EU-07 外部电源生态设计（能效、空载功耗、标示）　✅ 已核实

- **依据**：Commission Regulation (EU) 2019/1782；将被 Regulation (EU) 2025/2052 自 2028-01-01 起替代（欧委会产品页）
- **要求**：输出功率不超过 250 W、用于家用和办公电子电气设备的外部电源须满足平均有效效率、空载功耗和信息标示要求。
- **适用条件**：随附外部电源（适配器）。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。适配器铭牌和技术文件中给出效率数据；采购时要求供应商提供能效测试报告。
- **来源**：[EUR-Lex：Regulation (EU) 2019/1782](https://eur-lex.europa.eu/eli/reg/2019/1782/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[European Commission：Energy-efficient products – External power supplies](https://energy-efficient-products.ec.europa.eu/product-list/external-power-supplies_en) · A · 2026-11-01
- **备注**：2028 年后的新要求需要提前看 (EU) 2025/2052 原文。

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

### EU-12 通用产品安全法规 GPSR (EU) 2023/988　✅ 已核实

- **依据**：Regulation (EU) 2023/988
- **要求**：消费品须安全（覆盖其他专门法规没管到的风险）；制造商须做内部风险分析、编制技术文件、标注识别和联系信息，在欧盟须有负责的经营者；在线销售有额外信息要求。2024-12-13 起适用，取代 2001/95/EC。
- **适用条件**：所有面向消费者的产品。
- **证据形式**：一般安全义务（无固定证书，靠风险评估和技术文件）。没有证书；靠风险评估、技术文件和标签。
- **来源**：[EUR-Lex：Regulation (EU) 2023/988](https://eur-lex.europa.eu/eli/reg/2023/988/oj) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[EU-OSHA：Regulation 2023/988/EU general product safety](https://osha.europa.eu/en/legislation/directive/regulation-2023988eu-general-product-safety) · A · 2026-11-01<br>[GOV.UK：EU Regulation 2023/988 on general product safety factsheet（北爱尔兰适用说明）](https://www.gov.uk/government/publications/general-product-safety-regulations-northern-ireland/eu-regulation-2023988-on-general-product-safety-factsheet) · A · 2026-11-01
- **疑点 / 待核实**：欧盟负责经营者的具体条款（GPSR 与市场监管法规 (EU) 2019/1020 的衔接）条款号待核实。

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

### US-04 FCC U.S. Cyber Trust Mark（自愿 IoT 网络安全标签）　⚠️ **待核实**

- **依据**：FCC 自愿网络安全标签计划（U.S. Cyber Trust Mark）
- **要求**：自愿项目：符合计划网络安全标准的物联网设备可申请使用该标签。美国联邦层面本次未查到对消费类联网设备的强制网络安全要求。
- **适用条件**：联网消费类设备，自愿参加。
- **证据形式**：自愿项目。由计划指定的认可实验室测试、管理机构审核。
- **来源**：[FCC 文件 DOC-420764A1（Cyber Trust Mark 相关）](https://docs.fcc.gov/public/attachments/DOC-420764A1.txt) · A · 2026-11-01<br>[Nextgov（2026-10）：FCC 委员称希望一年内消费者能看到带标签的产品](https://www.nextgov.com/cybersecurity/2026/10/fcc-commissioner-hopes-cyber-trust-mark-products-reach-shoppers-within-year/416878/) · C · 2026-11-01
- **疑点 / 待核实**：第三方报道称原牵头管理机构 2025 年底退出，2026-04-13 FCC 选定新的牵头管理机构，截至 2026-10 标签尚未在零售端上线；没有读到 FCC 官方的现状公告。部分州（如加州）有联网设备安全法，本库未展开。

### US-07 DOE 外部电源能效标准（10 CFR 430.32(w)，Level VI）　⚠️ **待核实**

- **依据**：10 CFR 430.32(w)
- **要求**：在美国制造和销售的外部电源须满足 10 CFR 430.32(w) 规定的能效标准（Level VI），并按 DOE 要求认证和报告。
- **适用条件**：随附外部电源（适配器）。
- **证据形式**：注册 / 备案 / 生产者责任登记。适配器制造商向 DOE 合规认证数据库报告；整机厂采购时核对适配器的 Level VI 标识和登记。
- **来源**：[eCFR：10 CFR 430.32 Energy and water conservation standards](https://www.ecfr.gov/current/title-10/chapter-II/subchapter-D/part-430/subpart-C/section-430.32) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[U.S. DOE：External Power Supplies](https://www.energy.gov/eere/buildings/external-power-supplies) · A · 2026-11-01
- **疑点 / 待核实**：DOE 页面显示有"拟废止外部电源能效法规"的通知，是否已最终生效未查到。

### US-10 适配器电气安全：未查到联邦强制认证（NRTL 列名属渠道要求）　⚠️ **待核实**

- **依据**：未查到专门联邦法规
- **要求**：本次没有找到要求消费类电源适配器必须取得 NRTL（如 UL、ETL）列名的联邦法规；但大型零售商和电商平台 普遍要求。适配器能效见 US-07，适配器作为数字设备的电磁辐射见 US-03。
- **适用条件**：随附电源适配器，在美国销售。
- **证据形式**：一般安全义务（无固定证书，靠风险评估和技术文件）。建议采购已有 UL/ETL 等列名的适配器并保存证书。
- **来源**：[eCFR：47 CFR Part 15 Subpart B（适配器开关电源的电磁辐射）](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-B) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）
- **疑点 / 待核实**：消费品适配器安全的联邦要求本次没有找到官方说明，零售渠道要求也未核实。

## UK · 英国 UKCA

### UK-01 Radio Equipment Regulations 2017（英国无线电设备条例）　✅ 已核实

- **依据**：The Radio Equipment Regulations 2017（SI 2017/1206）
- **要求**：无线电设备须满足安全、EMC、有效使用频谱等基本要求，制造商编制技术文件和符合性声明，加施 UKCA 标志（大不列颠）；北爱尔兰按欧盟规则使用 CE。
- **适用条件**：产品含无线电功能，在英国销售。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。与 EU RED 类似：采用指定标准可自我声明，否则需要英国批准机构。
- **来源**：[legislation.gov.uk：The Radio Equipment Regulations 2017](https://www.legislation.gov.uk/uksi/2017/1206/contents) · S · 2026-11-01<br>[GOV.UK：Radio Equipment Regulations 2017: Great Britain（法定指南）](https://www.gov.uk/government/publications/radio-equipment-regulations-2017/radio-equipment-regulations-2017-great-britain) · A · 2026-11-01<br>[GOV.UK：UK Government announces extension of CE mark recognition for businesses](https://www.gov.uk/government/news/uk-government-announces-extension-of-ce-mark-recognition-for-businesses) · A · 2026-11-01
- **疑点 / 待核实**：英国政府宣布对其主管的多部产品法规"无限期"继续承认 CE 标志，但本次没有读到覆盖清单，Radio Equipment Regulations 2017 是否在内待核实。
- **备注**：在大不列颠可否只用 CE 标志，以 GOV.UK 清单为准。

### UK-03 Electrical Equipment (Safety) Regulations 2016（随附市电适配器）　✅ 已核实

- **依据**：The Electrical Equipment (Safety) Regulations 2016（SI 2016/1101）
- **要求**：规定电压范围内的电气设备须满足安全目标，制造商编制技术文件和符合性声明，加施 UKCA（或按承认安排加施 CE）。
- **适用条件**：随附交流市电输入的电源适配器。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。采购现成适配器时保存其符合性声明和测试报告。
- **来源**：[legislation.gov.uk：The Electrical Equipment (Safety) Regulations 2016](https://www.legislation.gov.uk/uksi/2016/1101/contents) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[GOV.UK：Electrical Equipment (Safety) Regulations 2016（法定指南）](https://www.gov.uk/government/publications/electrical-equipment-safety-regulations-2016) · A · 2026-11-01
- **疑点 / 待核实**：法定指南页面只在归档快照里看到标题，现行内容没有读到。

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

### UK-07 General Product Safety Regulations 2005（大不列颠一般产品安全）　✅ 已核实

- **依据**：The General Product Safety Regulations 2005（SI 2005/1803）；Product Regulation and Metrology Act 2025（授权法）
- **要求**：在大不列颠投放的消费品须安全，生产者须提供警示信息、标注识别信息、配合召回。北爱尔兰自 2024-12-13 起适用欧盟 GPSR。2025 年《产品监管与计量法》已获御准，授权政府以二级立法制定新的产品安全要求（包括在线市场）。
- **适用条件**：所有面向消费者的产品。
- **证据形式**：一般安全义务（无固定证书，靠风险评估和技术文件）。无证书；风险评估和技术文件。
- **来源**：[legislation.gov.uk：The General Product Safety Regulations 2005](https://www.legislation.gov.uk/uksi/2005/1803/contents) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）<br>[GOV.UK：General Product Safety Regulations 2005: Great Britain](https://www.gov.uk/government/publications/general-product-safety-regulations-2005/general-product-safety-regulations-2005-great-britain) · A · 2026-11-01<br>[Jones Day：Product Regulation and Metrology Bill receives Royal Assent](https://www.jonesday.com/en/insights/2025/07/product-regulation-and-metrology-bill-receives-royal-assent) · C · 2026-11-01
- **疑点 / 待核实**：《产品监管与计量法》下已经发布了哪些二级立法，未查到。

### UK-09 PSTI 产品安全制度（联网消费品网络安全）　✅ 已核实

- **依据**：Product Security and Telecommunications Infrastructure Act 2022；The Product Security and Telecommunications Infrastructure (Security Requirements for Relevant Connectable Products) Regulations 2023（SI 2023/1007）
- **要求**：2024-04-29 起，在英国供应的消费类可联网产品须满足附表 1 的安全要求（基于 ETSI EN 303 645：禁止通用默认密码、公布漏洞报告途径、公布最短安全更新期），并随附符合性声明（statement of compliance）。附表 3 列出例外产品。
- **适用条件**：产品可联网（互联网可连接或网络可连接），面向消费者，在英国销售。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。制造商签发符合性声明随产品提供；进口商、分销商有核查义务。
- **来源**：[legislation.gov.uk：SI 2023/1007](https://www.legislation.gov.uk/uksi/2023/1007) · S · 2026-11-01<br>[legislation.gov.uk：SI 2023/1007 附表 1（安全要求）](https://www.legislation.gov.uk/uksi/2023/1007/schedule/1/made) · S · 2026-11-01
- **疑点 / 待核实**：只通过 BLE 与手机通信的产品是否属于"网络可连接产品"，按附表和指南判断；GOV.UK 指南页本次未在搜索结果中出现。

### UK-11 外部电源生态设计（大不列颠保留的 2019/1782）　⚠️ **待核实**

- **依据**：Commission Regulation (EU) 2019/1782（英国保留法版本）
- **要求**：外部电源的能效、空载功耗和信息标示要求在大不列颠以保留法形式继续适用。
- **适用条件**：随附外部电源（适配器），在大不列颠销售。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。采购时要求供应商提供能效测试数据。
- **来源**：[legislation.gov.uk：Commission Regulation (EU) 2019/1782（英国版本）](https://www.legislation.gov.uk/eur/2019/1782/contents) · S · 2026-11-01（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）
- **疑点 / 待核实**：大不列颠版本是否有修订、是否跟随欧盟 2025/2052 更新，未查到。

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

### AU-04 电气安全 EESS（随附市电适配器，等级 3 申报类）　✅ 已核实

- **依据**：电气设备安全系统（EESS），AS/NZS 4417.1 / 4417.2，及各州电气安全法
- **要求**：低电压（市电）在范围内电气设备按风险等级管理；等级 3（高风险，含电源类申报产品）须取得认证证书、由负责供应商在 EESS 注册并加施 RCM。只由特低电压供电的产品本体不在 EESS 范围内。
- **适用条件**：随附交流市电输入的电源适配器。
- **证据形式**：认证 / 型号核准（由认证机构或主管部门发证）。适配器须有 EESS 认可的认证证书并注册；通常采购已注册的适配器。
- **来源**：[EESS：Level 3 – Electrical Equipment](https://eess.gov.au/registration/registration-in-scope-electrical-equipment/level-3) · A · 2026-11-01<br>[EESS：In-Scope Electrical Equipment（风险等级定义）](https://eess.gov.au/equipment/risk-level-definition) · A · 2026-11-01<br>[EESS 信息公告 21-030：Power supply / battery charger standards v2.0](https://www.eess.gov.au/wp-content/uploads/2026/07/21-030-Information-Bulletin-Power-supply-battery-charger-standards-v2.0.pdf) · A · 2026-11-01
- **疑点 / 待核实**：适配器属于等级 3 来自认证机构资料，EESS 页面确认了等级 3 的注册/认证要求，但没读到 AS/NZS 4417.2 的产品清单原文；各州法规的覆盖范围待核实。

### AU-07 智能设备网络安全标准（Cyber Security Act 2024 下的规则，2026-03-04 起）　✅ 已核实

- **依据**：Cyber Security (Security Standards for Smart Devices) Rules 2025（F2025L00276）
- **要求**：2026-03-04 及以后制造、面向个人/家庭使用的可联网产品须满足最低网络安全要求：禁止通用默认密码、提供漏洞报告机制、公布最短安全更新支持期，并提供符合性声明。台式机和笔记本电脑除外。
- **适用条件**：产品可直接或间接连接互联网，面向消费者，在澳大利亚销售。
- **证据形式**：自我声明（制造商自测或委托测试后签发符合性声明）。制造商提供符合性声明（statement of compliance）。
- **来源**：[Federal Register of Legislation：Cyber Security (Security Standards for Smart Devices) Rules 2025](https://www.legislation.gov.au/F2025L00276/asmade) · S · 2026-11-01<br>[Department of Home Affairs：Security standards for smart devices](https://www.homeaffairs.gov.au/cyber-security-subsite/Pages/security-standards-for-smart-devices.aspx) · A · 2026-11-01
- **疑点 / 待核实**：三项要求的具体条文（例如支持期如何声明）本次只读到摘要。

## 必须找认证机构 / 检测机构确认的事项

- 上面所有标"待核实"的条目；
- 产品归类：是否属于中国 CCC 目录、欧盟通用充电器类别、玩具定义、联网/可连接产品定义；
- 使用已认证无线模组时，整机还需要做哪些测试（中国 SRRC、FCC、RED、ACMA）；
- 测试项目、样机数量、周期和费用。

> **这是资料整理，不是法律意见。** 清单只根据你给出的产品特征，从 `compliance/data/requirements.yaml` 里挑出可能相关的法规条目；是否适用、怎么做，以法规原文和认证机构/检测机构的书面意见为准。标"待核实"的条目尤其要确认。
