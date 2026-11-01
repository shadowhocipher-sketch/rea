# 合规地图（小型电子产品）

> **这是资料整理，不是法律意见，也不是合规结论。** 本文件只按产品特征列出各市场可能涉及的法规和证据形式，
> 方便提前规划。产品是否适用、具体怎么做，以法规原文和认证机构 / 检测机构的书面意见为准。

本文件由 `build_map.py` 从 `data/requirements.yaml` 生成，**不要手改**；改 YAML 后重新生成。
按产品出清单用 `checklist.py`，用法见 `.claude/skills/compliance-map/SKILL.md`。

## 查询方法和局限

2026-11-01 查询。本会话的网络策略拦截了所有官方站点的直接访问（WebFetch 报 ENOTFOUND，curl 经代理报 CONNECT 403），所以没有一条法规全文是直接打开读过的。核实方式是 WebSearch：搜索结果里出现官方域名页面（S/A 级），且搜索摘要引用该页面内容、与条目要点一致的，标"已核实"；只有第三方页面、来源互相冲突、适用范围拿不准的，标"待核实"。来源的 access 字段：search = 该 URL 出现在搜索结果里；pattern = 按官方网站的 URL 规则（如 EUR-Lex ELI、eCFR、legislation.gov.uk）拼出的原文地址，本次没有在搜索结果里看到，使用前请打开核对。

来源级别按 `.claude/skills/research-method/SKILL.md`：S = 法规原文 / 监管机构原文；A = 监管机构或政府的解读、指南、转载；C = 第三方（只作线索）。

共 57 条：已核实 33 条，待核实 24 条。

## 总表：特征 × 市场

格子里是要求编号，点击跳到正文；带 ⚠ 的是待核实。“基础”行是所有电子产品都要看的条目。

| 特征 \ 市场 | CN 中国 | EU 欧盟 CE | US 美国 FCC / CPSC | UK 英国 UKCA | AU 澳大利亚 RCM |
|---|---|---|---|---|---|
| 基础（所有带电子电路的产品） | [CN-03](#CN-03)⚠、[CN-07](#CN-07)⚠ | [EU-05](#EU-05)、[EU-08](#EU-08)、[EU-09](#EU-09)⚠、[EU-12](#EU-12) | [US-03](#US-03)⚠ | [UK-02](#UK-02)、[UK-04](#UK-04)、[UK-05](#UK-05)、[UK-07](#UK-07) | [AU-03](#AU-03) |
| 无线（Wi-Fi / BLE 等） | [CN-01](#CN-01)⚠、[CN-02](#CN-02)⚠ | [EU-01](#EU-01)、[EU-02](#EU-02)⚠ | [US-01](#US-01)、[US-02](#US-02) | [UK-01](#UK-01) | [AU-01](#AU-01)、[AU-02](#AU-02)⚠ |
| 联网（网络安全） | [CN-09](#CN-09)⚠ | [EU-03](#EU-03)、[EU-04](#EU-04)⚠ | [US-04](#US-04)⚠ | [UK-09](#UK-09) | [AU-07](#AU-07) |
| 锂电池（可充电锂离子/锂聚合物） | [CN-05](#CN-05)⚠、[CN-10](#CN-10)、[CN-11](#CN-11)⚠ | [EU-02](#EU-02)⚠、[EU-10](#EU-10)⚠、[EU-11](#EU-11)、[EU-15](#EU-15) | [US-08](#US-08)、[US-09](#US-09)⚠ | [UK-06](#UK-06)、[UK-12](#UK-12) | [AU-08](#AU-08)⚠、[AU-09](#AU-09) |
| 纽扣电池 | [CN-08](#CN-08)⚠、[CN-10](#CN-10)、[CN-11](#CN-11)⚠ | [EU-10](#EU-10)⚠、[EU-11](#EU-11)、[EU-14](#EU-14)⚠、[EU-15](#EU-15) | [US-05](#US-05)、[US-08](#US-08) | [UK-06](#UK-06)、[UK-10](#UK-10)⚠、[UK-12](#UK-12) | [AU-05](#AU-05)、[AU-09](#AU-09) |
| 随附电源适配器 | [CN-04](#CN-04)⚠ | [EU-06](#EU-06)、[EU-07](#EU-07) | [US-07](#US-07)⚠、[US-10](#US-10)⚠ | [UK-03](#UK-03)、[UK-11](#UK-11)⚠ | [AU-04](#AU-04) |
| 儿童用（玩具/儿童产品） | [CN-06](#CN-06) | [EU-03](#EU-03)、[EU-13](#EU-13)⚠ | [US-05](#US-05)、[US-06](#US-06) | [UK-08](#UK-08) | [AU-06](#AU-06) |

证据形式：self_declaration = 自我声明（制造商自测或委托测试后签发符合性声明）；third_party_test = 第三方测试（指定或认可的实验室出报告）；certification = 认证 / 型号核准（由认证机构或主管部门发证）；registration = 注册 / 备案 / 生产者责任登记；voluntary = 自愿项目；general_duty = 一般安全义务（无固定证书，靠风险评估和技术文件）；unknown = 未确定。

## 正文

## CN · 中国

<a id="CN-01"></a>
### CN-01 SRRC 无线电发射设备型号核准（2.4 GHz / 5 GHz Wi-Fi、蓝牙）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：无线（Wi-Fi / BLE 等）
- 依据：工信部《关于加强和规范2400MHz、5100MHz和5800MHz频段无线电管理有关事宜的通知》（工信部无〔2021〕129号）
- 要求：在 2400–2483.5 MHz、5150–5350 MHz、5725–5850 MHz 频段工作的蓝牙、无线局域网等设备，除微功率短距离设备外，应取得无线电发射设备型号核准证（SRRC），并满足通知附件的技术要求（第三方资料称新增了自适应等测试要求）。5100 MHz 频段限室内使用。
- 适用条件：产品含 Wi-Fi 或蓝牙等无线发射功能，在中国销售。
- 证据形式：认证 / 型号核准（由认证机构或主管部门发证）。向工信部无线电管理机构申请型号核准，样机需在指定检测机构测试。用已取得核准的模组时整机是否还要单独核准，待核实。
- 来源：
  - 原文转载：[工信部无〔2021〕129号 转载 PDF（TI E2E 论坛附件，非官方）](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/968/_E55DE14FE890E0651430_2021_1530_129_F7530A30E55D1A4E8C54E14F6F601653E89073518E4EA0523A5F8C54C4890383_2400MHz_0130_5100MHz_8C54_5800MHz_9198B56BE065BF7E3575A17B0674096773518B4E9C5B84761A90E5770B30_.pdf) · C · 2026-11-01
  - 第三方解读：[In Compliance Magazine：MIIT 2021 No. 129 解读](https://incompliancemag.com/chinas-latest-regulation-on-2-4-ghz-and-5-ghz-equipment/) · C · 2026-11-01
- 疑点：工信部官网原文页面本次未能定位（搜索摘要提到工信部页面的成文日期 2021-09-08、发布日期 2021-10-13，但没给出 URL）。实施和过渡期日期各来源不一致（2022-01-01 起施行、过渡期至 2023-10-15 / 两年）。使用已核准模组的整机是否需要单独核准，需要向检测机构确认。
- 备注：与 CN-02 一起看：蓝牙低功率设备是否可按微功率设备免核准，是本条最大的疑点。

<a id="CN-02"></a>
### CN-02 微功率短距离无线电发射设备目录和技术要求（免型号核准的边界）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：无线（Wi-Fi / BLE 等）
- 依据：工业和信息化部公告 2019 年第 52 号《微功率短距离无线电发射设备目录和技术要求》
- 要求：列入目录且符合技术要求的微功率设备，生产或进口后在国内销售和使用，无需取得无线电频率使用许可、无线电台执照和型号核准，但仍须符合产品质量等法律法规、国家标准和无线电管理规定。
- 适用条件：产品含无线发射功能，想判断能否按微功率设备免于型号核准（例如低功率 2.4 GHz 私有协议或 BLE）。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。免核准不等于免要求：仍须满足目录中对应类别的频率、功率等技术指标，没有统一的证书。
- 来源：
  - 原文转载：[IT之家 转载公告全文](https://www.ithome.com/0/459/757.htm) · C · 2026-11-01
  - 原文转载：[维基文库：微功率短距离无线电发射设备目录和技术要求](https://zh.wikisource.org/wiki/%E5%BE%AE%E5%8A%9F%E7%8E%87%E7%9F%AD%E8%B7%9D%E7%A6%BB%E6%97%A0%E7%BA%BF%E7%94%B5%E5%8F%91%E5%B0%84%E8%AE%BE%E5%A4%87%E7%9B%AE%E5%BD%95%E5%92%8C%E6%8A%80%E6%9C%AF%E8%A6%81%E6%B1%82) · C · 2026-11-01
- 疑点：工信部官网原文本次未能定位，只看到转载。目录 2.4 GHz 类别的具体功率限值本次没有读到原文；Wi-Fi / 蓝牙产品是否可以落入微功率类别（与 CN-01 的 129 号通知如何衔接）没把握，必须问检测机构。
- 备注：公告日期各来源写法不同（2019-11-19 附件 / 2019-11-28 生效）。

<a id="CN-03"></a>
### CN-03 CCC 强制性产品认证（产品本体是否在目录内）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：市场监管总局《强制性产品认证目录描述与界定表（2023年修订）》（2023 年第 36 号公告）及后续调整
- 要求：列入 CCC 目录的产品，未获得认证证书（或按规定完成自我声明）并加施 CCC 标志的，不得出厂、销售、进口。2023 年修订版共 16 大类 96 种产品，部分产品实行自我声明程序 A / B；2024 年后目录又有增补。
- 适用条件：任何在中国销售的电子产品都要先按《描述与界定表》判断本体是否属于目录产品（例如信息技术设备、音视频设备）。
- 证据形式：认证 / 型号核准（由认证机构或主管部门发证）。目录内产品由指定认证机构认证，或按目录标注走自我声明（报送系统 sdoc.cnca.cn）；目录外产品不需要 CCC。
- 来源：
  - 官方转载：[香港工业贸易署转载：强制性产品认证目录描述与界定表（2023年修订）公告](https://www.tid.gov.hk/english/aboutus/tradecircular/cic/asia/2023/files/ci2023659a.pdf) · A · 2026-11-01
  - 地方政府文件：[汕头市政府文件（提到截至 2024 年底目录为 16 大类 105 种）](https://www.shantou.gov.cn/attachment/0/135/135589/2446285.docx) · A · 2026-11-01
- 疑点：认监委官网（cnca.gov.cn）原文附件本次无法访问，没有读到具体条目。USB 供电的小型桌面电子产品 是否落入"信息技术设备""音视频设备"等目录类别，取决于产品功能和界定表的描述，必须让认证机构判断。
- 备注：产品本体不在目录内时，其随附的适配器（CN-04）、内置锂电池（CN-05）仍可能各自需要 CCC。

<a id="CN-04"></a>
### CN-04 CCC：随附电源适配器 / 充电器

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：随附电源适配器
- 依据：强制性产品认证目录（电源适配器类产品），实施规则 CNCA-C09-01:2023《强制性产品认证实施规则 电子产品及安全附件》
- 要求：随产品销售的电源适配器 / 充电器如属于 CCC 目录产品，须有 CCC 证书并加施标志。
- 适用条件：产品包装内随附交流供电的电源适配器或充电器，在中国销售。
- 证据形式：认证 / 型号核准（由认证机构或主管部门发证）。通常直接采购已有 CCC 证书的适配器，并保存证书；自己设计适配器则需要认证。
- 来源：
  - 官方转载：[香港工业贸易署转载：CCC 目录描述与界定表（2023年修订）公告](https://www.tid.gov.hk/english/aboutus/tradecircular/cic/asia/2023/files/ci2023659a.pdf) · A · 2026-11-01
  - 企业证书示例：[Raspberry Pi 27W 电源 CCC 证书（示例：按 CNCA-C09-01:2023 认证的适配器）](https://pip.raspberrypi.com/categories/900-approvals/documents/RP-005300-CF/rpi-27W-PSU-China.pdf) · C · 2026-11-01
- 疑点：没有读到界定表中适配器条目的原文和适用电压/功率范围；目前的依据是厂商证书示例和转载公告。
- 备注：采购现成适配器时，核对证书上的型号与实物一致、证书有效。

<a id="CN-05"></a>
### CN-05 CCC：锂离子电池和电池组（GB 31241）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）
- 依据：市场监管总局 2023 年公告（对锂离子电池和电池组、移动电源实施 CCC 管理）；国家标准 GB 31241-2022；实施规则 CNCA-C09-01:2023
- 要求：自 2023-08-01 起对便携式电子产品用锂离子电池和电池组、移动电源实施 CCC 管理；自 2024-08-01 起，未获 CCC 证书和未标注认证标志的，不得出厂、销售、进口或在其他经营活动中使用。锂离子电池和电池组依据 GB 31241。
- 适用条件：产品内置可充电锂离子 / 锂聚合物电池（便携式电子产品用），在中国销售。
- 证据形式：认证 / 型号核准（由认证机构或主管部门发证）。电池（或电池组）由指定认证机构认证；整机厂通常采购已获 CCC 的电芯/电池组并保存证书。
- 来源：
  - 官方转载：[香港工业贸易署转载：市场监管总局关于对锂离子电池等产品实施 CCC 管理的公告（2023）](https://www.tid.gov.hk/english/aboutus/tradecircular/cic/asia/2023/files/ci2023409a.pdf) · A · 2026-11-01
  - 媒体报道：[人民网：8月起对锂电池实施CCC认证（2023-07-31）](https://paper.people.com.cn/zgnybwap/html/2023-07/31/content_26009869.htm) · C · 2026-11-01
- 疑点：市场监管总局官网原文本次无法访问；公告文号和发布日期各来源不一致（3 月 / 7 月，"第10号"）。内置于整机中的电池是否必须单独持有 CCC 证书（还是只对单独销售的电池），以及小容量电池是否有豁免，没有读到原文条款。
- 备注：2026 年工信部公示了《移动电源安全技术规范》强制性国家标准报批稿（第三方报道），只影响移动电源（充电宝）类产品。

<a id="CN-06"></a>
### CN-06 CCC：玩具（含电玩具），新版实施规则 CNCA-C22-02:2026

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：儿童用（玩具/儿童产品）
- 依据：国家认监委 2026 年第 8 号公告；《强制性产品认证实施规则 玩具》CNCA-C22-02:2026；GB 6675 系列（2025 版，第三方资料）
- 要求：属于 CCC 目录的玩具须取得 CCC 证书。2026-11-01 起，CCC 认证活动应当按新版实施规则开展；已颁发的有效证书可继续使用，通过变更、到期换证等方式逐步转换。
- 适用条件：产品面向儿童、属于玩具（第三方资料称适用于面向 14 岁以下儿童的电玩具、塑胶玩具、金属玩具、弹射玩具等目录类别）。
- 证据形式：认证 / 型号核准（由认证机构或主管部门发证）。由指定认证机构按实施规则做型式试验 + 工厂检查，发 CCC 证书。
- 来源：
  - 官方转载：[香港工业贸易署转载：国家认监委关于发布电动自行车、童车、玩具 CCC 实施规则的公告（2026）](https://www.tid.gov.hk/en/tradecircular/files/2026/ci4972026a.pdf) · A · 2026-11-01
  - 第三方解读：[STC：New CCC Implementation Rules for Electric Bicycles, Toys, and Children's Vehicle Products](https://stc.group/en/media/detail/2380) · C · 2026-11-01
- 疑点：公告日期两个来源写法不同（2026-05-29 / 2026-05-31）；产品是否属于"玩具"目录类别需按界定表判断；新版 GB 6675 的版本号仅来自第三方。
- 备注：今天（2026-11-01）正好是新规则强制执行日，新申请按新规则做。

<a id="CN-07"></a>
### CN-07 中国 RoHS：电器电子产品有害物质限制使用

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：《电器电子产品有害物质限制使用管理办法》；《电器电子产品有害物质限制使用达标管理目录（2026年版）》；GB 26572—2025（2027-08-01 实施）
- 要求：电器电子产品须按标准标注有害物质信息（RoHS 标识、信息披露）；列入达标管理目录的产品还须满足限量要求并纳入合格评定。2026 年版目录共 33 种产品，新增产品管控要求 2027-08-01 起实施。
- 适用条件：所有在中国销售的电器电子产品（标识义务）；是否属于达标管理目录的 33 种产品需单独判断。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。标识和信息披露由企业自行完成；目录内产品的合格评定方式（自我声明或认证）待核实。
- 来源：
  - 政府网站转载：[国家科技传播中心网站：达标管理目录（2026年版）相关公告](https://www.ncsti.gov.cn/kjdt/tzgg/202605/t20260528_248133.html) · A · 2026-11-01
  - 第三方翻译：[ChemLinked：达标管理目录（2026 版）英文翻译](https://chemical.chemlinked.com/translation/qualification-management-catalogue-for-the-restriction-of-hazardous-substances-in-electrical-appliances-and-electronic-products-2026-version) · C · 2026-11-01
- 疑点：工信部原文和目录附件本次无法访问，33 种产品的具体名单没有读到（第三方称新增智能手环等）；旧标准 SJ/T 11364、GB/T 26572-2011 与 GB 26572—2025 的过渡安排没查到官方说明。
- 备注：物料选型时就要求供应商提供符合限量要求的声明或检测报告，省得后面补。

<a id="CN-08"></a>
### CN-08 纽扣电池：未查到中国针对"含纽扣电池产品"的专门强制要求

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：纽扣电池
- 依据：未查到
- 要求：本次没有找到中国市场监管总局发布的、针对含纽扣电池产品防误吞（电池仓固定、警示标签等）的专门强制性国家标准。玩具类产品的电池要求在玩具 CCC（CN-06）所用的 GB 6675 / 电玩具标准中。
- 适用条件：产品使用纽扣/硬币电池，在中国销售。
- 证据形式：未确定。未查到。
- 来源：
  - 检索入口：[国家标准全文公开系统（建议在此按'纽扣电池'检索）](https://openstd.samr.gov.cn/) · S · 2026-11-01
- 疑点：查过：WebSearch 中文检索"纽扣电池 强制性国家标准 儿童 误吞"，结果只有澳大利亚和美国的资料。不能据此认为中国没有要求，需要认证机构确认。
- 备注：即便没有专门要求，也建议参照 AU-05 / US-05 的做法设计电池仓（螺丝固定）和警示。

<a id="CN-09"></a>
### CN-09 联网设备：个人信息保护；未查到消费类物联网网络安全强制标准

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：联网（网络安全）
- 依据：《中华人民共和国个人信息保护法》（2021-11-01 施行）
- 要求：设备或配套 App 处理个人信息时，适用个人信息保护法（告知同意、最小必要等处理规则和处理者义务）。本次没有找到类似英国 PSTI、澳洲智能设备规则那样针对消费类联网设备的强制性网络安全国家标准。
- 适用条件：产品联网（直接或经手机 App），并收集、处理用户个人信息。
- 证据形式：一般安全义务（无固定证书，靠风险评估和技术文件）。个人信息保护属于运营义务（隐私政策、同意机制、安全措施），没有产品证书。
- 来源：
  - 法律原文：[国家互联网信息办公室：中华人民共和国个人信息保护法（全文）](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) · S · 2026-11-01
- 疑点：是否存在适用于消费类联网设备的强制性网络安全国家标准或认证（例如网络关键设备目录之外的消费产品），本次检索未查到，需要确认。
- 备注：如果设备接入电信网络（蜂窝），还涉及电信设备进网许可——本库只覆盖 Wi-Fi / BLE，未展开。

<a id="CN-10"></a>
### CN-10 锂电池出口：出境危险货物运输包装使用鉴定（"危包证"）与 UN 38.3

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）、纽扣电池
- 依据：《中华人民共和国进出口商品检验法》第十七条；UN《试验和标准手册》第三部分 38.3；海运按《国际海运危险货物规则》（IMDG Code）
- 要求：进出口商品检验法第十七条：为出口危险货物生产包装容器的企业，须申请商检机构（现为海关）做包装容器的性能鉴定；生产出口危险货物的企业，须申请包装容器的使用鉴定；使用未经鉴定合格的包装容器的危险货物，不准出口。按海关答疑（媒体转述），大部分锂电池属于危险货物，出口前要完成 UN 38.3 测试，由电池生产厂或出口商向属地海关申请 《出境危险货物运输包装使用鉴定结果单》（俗称危包证），海运订舱和危险品申报时都要提供；包装要有 UN 包装标记、锂电池标记 / 9 类危险品标签，电池须标额定能量（Wh）。
- 适用条件：产品含锂离子电池或锂金属纽扣电池，从中国出口（空运、海运、快递）。
- 证据形式：认证 / 型号核准（由认证机构或主管部门发证）。危包证由属地海关出具；UN 38.3 测试报告和测试摘要向电芯/电池组供应商索取，整机出口时由货代/承运人核对。
- 来源：
  - 官方转载：[香港工业贸易署转载：《中华人民共和国进出口商品检验法》全文（2018 年修正文本，节录自全国人大信息中心网站）](https://www.tid.gov.hk/english/aboutus/tradecircular/cic/asia/2019/files/ci201952a.pdf) · A · 2026-11-01
  - 第三方转载：[维基文库：中华人民共和国进出口商品检验法（2021 年）](https://zh.wikisource.org/wiki/%E4%B8%AD%E5%8D%8E%E4%BA%BA%E6%B0%91%E5%85%B1%E5%92%8C%E5%9B%BD%E8%BF%9B%E5%87%BA%E5%8F%A3%E5%95%86%E5%93%81%E6%A3%80%E9%AA%8C%E6%B3%95_(2021%E5%B9%B4)) · C · 2026-11-01
  - 媒体报道（转述广州海关答疑）：[人民日报海外版：锂电池出口有哪些要求？（海关答疑，2024-07-20）](https://paper.people.com.cn/hwbwap/html/2024-07/20/content_26070303.htm) · C · 2026-11-01
- 疑点：已核实的只是第十七条"出口危险货物包装须经使用鉴定"（A 级转载为 2018 年修正文本，2021 年修正后的现行文本只在第三方转载里见到，条文一致）。以下只有第三方或媒体来源：危包证办理流程和材料；锂电池哪些情况算危险货物、哪些按 UN 特殊规定 188（小电芯 ≤20 Wh、小电池 ≤100 Wh、锂金属电芯 ≤1 g 等，第三方资料）可以免除危险品包装要求；装在设备里的小电池（UN 3481 / UN 3091）出口时是否仍需危包证。海关总署原文（customs.gov.cn）本次无法访问，需要向属地海关或货代确认。
- 备注：中国境内运输和空运要求见 CN-11；进口国在途要求见 EU-15、UK-12、US-08、AU-09。

<a id="CN-11"></a>
### CN-11 锂电池航空运输（中国民航）：MH/T 1020 与 UN 38.3；运输安全国标 GB 21966

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）、纽扣电池
- 依据：民航行业标准 MH/T 1020-2018《锂电池航空运输规范》；国际民航组织《危险物品安全航空运输技术细则》（ICAO TI，Doc 9284）；GB 21966-2008《锂原电池和蓄电池在运输中的安全要求》
- 要求：按第三方提供的 MH/T 1020-2018 译本：锂电池（芯）交付航空运输前须通过 UN《试验和标准手册》第三部分 38.3 的系列试验。ICAO 技术细则把锂电池列为危险物品，按包装说明（例如装在设备中的锂离子电池为 PI 967、与设备包装在一起为 PI 966）规定数量限制和包装要求。GB 21966-2008 等同采用 IEC 62281:2004，规定锂电池运输中的安全试验方法和要求。
- 适用条件：产品含锂离子电池或锂金属纽扣电池，在中国境内空运、快递，或从中国空运出口。
- 证据形式：第三方测试（指定或认可的实验室出报告）。UN 38.3 测试报告 / 测试摘要向电池供应商索取；空运还要货代按承运人要求出具运输条件鉴定或危险品申报，所需文件以承运人为准。
- 来源：
  - 第三方标准译本：[codeofchina：MH/T 1020-2018 英文译本页面](https://codeofchina.com/standard/MHT1020-2018.html) · C · 2026-11-01
  - 第三方标准译本：[chinesestandard.net：GB 21966-2008 英文译本](https://www.chinesestandard.net/PDF-EN/GB21966-2008EN-P06P-H4752H-175950.pdf) · C · 2026-11-01
  - 国际组织工作文件：[ICAO DGP 工作文件（中文）：锂电池客货运相关修订](https://www.icao.int:443/safety/DangerousGoods/DGP25/DGP.25.WP.033.5.ch.pdf) · A · 2026-11-01
- 疑点：民航局（caac.gov.cn）原文和 MH/T 1020 现行版本本次都没读到，只有第三方译本；MH/T 1020 是否已有 2018 版之后的修订未查到。GB 21966-2008 是否现行、是否为强制性标准、是否会按 IEC 62281 新版修订，搜索结果没有直接说明。ICAO 工作文件只是修订讨论材料，不是技术细则现行文本；IATA 2026 版锂电池指南（PI 965–970、Section II 变化、30% 荷电状态）本次只见到第三方摘要。快递（邮政）渠道对含锂电池物品的收寄规定未查。
- 备注：选电芯时就要求供应商提供 UN 38.3 测试报告和测试摘要，型号要与实物一致。

## EU · 欧盟 CE

<a id="EU-01"></a>
### EU-01 无线电设备指令 RED 2014/53/EU（安全、EMC、频谱）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：无线（Wi-Fi / BLE 等）
- 依据：Directive 2014/53/EU（RED）
- 要求：无线电设备须满足基本要求：健康与安全（第 3(1)(a) 条，无低电压下限）、电磁兼容（第 3(1)(b) 条）、有效使用无线电频谱（第 3(2) 条）；编制技术文件、签发欧盟符合性声明、加施 CE 标志。
- 适用条件：产品含任何有意发射/接收无线电的功能（Wi-Fi、BLE、NFC 等）。含无线的产品走 RED，不再单独适用 EMC 指令和 LVD。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。完整采用协调标准时可按附件 II（内部生产控制）自我声明；第 3(2) 条未完整采用协调标准时须公告机构参与（附件 III / IV）。
- 来源：
  - 法规原文：[EUR-Lex：Directive 2014/53/EU](https://eur-lex.europa.eu/eli/dir/2014/53/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[European Commission：Radio Equipment Directive (RED)](https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en) · A · 2026-11-01
- 备注：用已有 CE 资料的无线模组，整机仍需自己做 RED 评估（模组报告可以复用一部分）。

<a id="EU-02"></a>
### EU-02 RED 通用充电器要求（USB Type-C）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：无线（Wi-Fi / BLE 等）、锂电池（可充电锂离子/锂聚合物）
- 依据：Directive (EU) 2022/2380（修订 RED）
- 要求：列入类别的可有线充电的无线电设备须配 USB Type-C 充电口并支持相关快充协议、提供不带充电器的销售选项和标签信息。类别包括手机、平板、相机、头戴/入耳耳机、便携音箱、电子阅读器、键盘、鼠标、手持游戏机、便携导航等，2024-12-28 起适用；笔记本电脑 2026-04-28 起。
- 适用条件：产品是无线电设备、内置可充电电池且通过有线充电，并且属于指令列出的产品类别。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。作为 RED 基本要求的一部分，在符合性声明中覆盖。
- 来源：
  - 法规原文：[EUR-Lex：Directive (EU) 2022/2380](https://eur-lex.europa.eu/eli/dir/2022/2380/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[European Commission：One common charging solution for all](https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red/one-common-charging-solution-all_en) · A · 2026-11-01
- 疑点：小型桌面摆件、口袋小设备、玩具不在常见类别列表里，是否适用取决于产品归类；本库没有读到指令附件原文的完整类别定义。
- 备注：即使不在范围内，用 USB-C 充电通常也是低成本的稳妥选择（这是建议，不是法规要求）。

<a id="EU-03"></a>
### EU-03 RED 网络安全授权法规（第 3(3)(d)(e)(f) 条）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：联网（网络安全）、儿童用（玩具/儿童产品）
- 依据：Delegated Regulation (EU) 2022/30；被 Delegated Regulation (EU) 2026/339 废止，废止自 2027-12-11 生效
- 要求：自 2025-08-01 起，能直接或间接联网的无线电设备、以及玩具类/儿童看护类/可穿戴类无线电设备，须满足网络保护、个人数据与隐私保护、防欺诈的基本要求。协调标准为 EN 18031-1/-2/-3（部分条款有限制）。2026/339 号授权法规于 2026-04-29 公布，自 2027-12-11 起废止 2022/30，届时由网络韧性法案（EU-04）接管；2025-08-01 至 2027-12-10 投放的设备仍按 2022/30 监管。
- 适用条件：产品含无线电功能，并且（能直接或间接联网，或是玩具/儿童看护/可穿戴设备）。2027-12-11 之前投放市场的产品。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。完整采用 EN 18031 且未落入其限制条款时可自我声明；否则须公告机构参与。
- 来源：
  - 法规原文：[EUR-Lex：Delegated Regulation (EU) 2022/30](https://eur-lex.europa.eu/eli/reg_del/2022/30/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 法规原文：[EUR-Lex：Delegated Regulation (EU) 2026/339（废止 2022/30）](https://eur-lex.europa.eu/eli/reg_del/2026/339/oj/eng) · S · 2026-11-01
  - 官方解读：[European Commission：Radio Equipment Directive (RED)（含网络安全转入 CRA 的说明）](https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en) · A · 2026-11-01
- 疑点：只通过 BLE 连手机、由 App 上网的设备算不算'间接联网'，需要按委员会指南和认证机构意见判断。
- 备注：2027-12-11 以后投放的产品转为按 CRA 评估，现在立项的产品两边都要规划。

<a id="EU-04"></a>
### EU-04 网络韧性法案 CRA（带数字元素的产品）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：联网（网络安全）
- 依据：Regulation (EU) 2024/2847（Cyber Resilience Act）
- 要求：带数字元素、有数据连接的产品须满足设计开发阶段的网络安全基本要求和全生命周期漏洞处理要求，加施 CE 标志。2024-12-10 生效，2027-12-11 全面适用；第三方资料称主动被利用漏洞和严重事件的报告义务自 2026-09-11 起适用，且覆盖已上市产品。
- 适用条件：产品有直接或间接的数据连接（Wi-Fi、BLE，可能也包括有线数据接口）。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。默认类别可自我评估；附件 III"重要"类和附件 IV"关键"类产品评估更严格。产品属于哪一类待核实。
- 来源：
  - 法规原文：[EUR-Lex：Regulation (EU) 2024/2847](https://eur-lex.europa.eu/eli/reg/2024/2847/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方摘要：[European Parliament Legislative Observatory：Cyber Resilience Act 摘要](https://oeil.europarl.europa.eu/oeil/en/document-summary?id=1796083) · A · 2026-11-01
  - 第三方解读：[Jones Day：CRA 24 小时报告义务 2026-09-11 起](https://www.jonesday.com/en/insights/2026/07/eu-cyber-resilience-act-24hour-reporting-duties-start-september-11-2026) · C · 2026-11-01
- 疑点：2026-09-11 报告义务日期只来自第三方（多家一致，但没读到条款原文）；只有 USB 数据口、没有无线的产品是否属于"有数据连接"没把握。
- 备注：报告义务现在已经生效（按第三方资料），已上市的联网产品也要有漏洞处理流程。

<a id="EU-05"></a>
### EU-05 电磁兼容指令 EMC 2014/30/EU（无无线功能的产品）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：Directive 2014/30/EU
- 要求：设备的电磁骚扰不得超出限值、并有足够的抗扰度；编制技术文件和欧盟符合性声明，加施 CE 标志；文件保存 10 年。
- 适用条件：不含无线电功能的电子产品（含无线的产品由 RED 第 3(1)(b) 条覆盖 EMC）。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。内部生产控制（自我声明），通常按协调标准测试。
- 来源：
  - 法规原文：[EUR-Lex：Directive 2014/30/EU](https://eur-lex.europa.eu/eli/dir/2014/30/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[European Commission：Electromagnetic compatibility (EMC) Directive](https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/electromagnetic-compatibility-emc-directive_en) · A · 2026-11-01

<a id="EU-06"></a>
### EU-06 低电压指令 LVD 2014/35/EU（随附市电适配器）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：随附电源适配器
- 依据：Directive 2014/35/EU
- 要求：额定电压在交流 50–1000 V、直流 75–1500 V 范围内的电气设备须安全，签发符合性声明并加施 CE 标志。
- 适用条件：随附交流市电输入的电源适配器。产品本体若只由 5 V USB 供电且无无线，则低于 LVD 电压范围，安全由 GPSR（EU-12）覆盖。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。内部生产控制。采购现成适配器时保存其 CE 符合性声明和测试报告。
- 来源：
  - 法规原文：[EUR-Lex：Directive 2014/35/EU](https://eur-lex.europa.eu/eli/dir/2014/35/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 成员国主管机构解读：[BAuA（德国联邦职业安全与健康研究所）：Scope of the Low Voltage Directive](https://www.baua.de/EN/Topics/Work-design/Safe-products/Electrical-products/Requirements/Application-field) · A · 2026-11-01
- 疑点：随附的第三方适配器，整机厂作为"投放者"要承担哪些文件义务，按认证机构意见。

<a id="EU-07"></a>
### EU-07 外部电源生态设计（能效、空载功耗、标示）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：随附电源适配器
- 依据：Commission Regulation (EU) 2019/1782；将被 Regulation (EU) 2025/2052 自 2028-01-01 起替代（欧委会产品页）
- 要求：输出功率不超过 250 W、用于家用和办公电子电气设备的外部电源须满足平均有效效率、空载功耗和信息标示要求。
- 适用条件：随附外部电源（适配器）。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。适配器铭牌和技术文件中给出效率数据；采购时要求供应商提供能效测试报告。
- 来源：
  - 法规原文：[EUR-Lex：Regulation (EU) 2019/1782](https://eur-lex.europa.eu/eli/reg/2019/1782/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[European Commission：Energy-efficient products – External power supplies](https://energy-efficient-products.ec.europa.eu/product-list/external-power-supplies_en) · A · 2026-11-01
- 备注：2028 年后的新要求需要提前看 (EU) 2025/2052 原文。

<a id="EU-08"></a>
### EU-08 RoHS 2011/65/EU（有害物质限制）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：Directive 2011/65/EU 及其附件 II 的修订（如 Delegated Directive (EU) 2015/863）
- 要求：电子电气设备中限用物质（铅、汞、镉、六价铬、多溴联苯、多溴二苯醚及后续增加的邻苯二甲酸酯类）不得超过最大浓度值；纳入符合性声明并加施 CE 标志。
- 适用条件：所有在欧盟销售的电子电气产品（含随附适配器、线缆）。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。技术文件里保存物料合规声明 / 检测报告。
- 来源：
  - 法规原文：[EUR-Lex：Directive 2011/65/EU](https://eur-lex.europa.eu/eli/dir/2011/65/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[European Commission (DG ENV)：RoHS Directive](https://environment.ec.europa.eu/topics/waste-and-recycling/rohs-directive_en) · A · 2026-11-01
- 疑点：限用物质总数各来源说法不一（6 种 / 10 种），以附件 II 现行版本为准。

<a id="EU-09"></a>
### EU-09 WEEE 2012/19/EU（废弃电子电气设备生产者责任）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：Directive 2012/19/EU
- 要求：生产者须在销售所在的每个成员国登记、承担回收处理费用并报告数量；产品标注带叉垃圾桶符号。
- 适用条件：所有在欧盟销售的电子电气产品。
- 证据形式：注册 / 备案 / 生产者责任登记。各成员国分别登记（例如德国 EAR、法国等），远程销售者可能需要授权代表。
- 来源：
  - 法规原文：[EUR-Lex：Directive 2012/19/EU](https://eur-lex.europa.eu/eli/dir/2012/19/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[European Commission (DG ENV)：Waste from Electrical and Electronic Equipment (WEEE)](https://environment.ec.europa.eu/topics/waste-and-recycling/waste-electrical-and-electronic-equipment-weee_en) · A · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
- 疑点：DG ENV 的 WEEE 页面本次未在搜索结果中出现（只在 RoHS 页面摘要中看到"WEEE 指令与 RoHS 配合促进回收"），登记义务按法规原文核对；各成员国登记的具体流程和费用不在本库范围，需逐国确认。

<a id="EU-10"></a>
### EU-10 电池法规 (EU) 2023/1542：生产者责任、标签、合规义务

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）、纽扣电池
- 依据：Regulation (EU) 2023/1542
- 要求：投放含电池的产品（便携式电池包括纽扣电池和内置锂电池）须承担电池的生产者延伸责任（登记、回收），满足标签与信息要求、有害物质限制等，各项义务按法规分阶段适用。
- 适用条件：产品含任何电池（内置可充电锂电池或纽扣电池）。
- 证据形式：注册 / 备案 / 生产者责任登记。各成员国电池生产者登记；电池本身的合规文件向电池供应商索取。
- 来源：
  - 法规原文：[EUR-Lex：Regulation (EU) 2023/1542](https://eur-lex.europa.eu/eli/reg/2023/1542/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方指南：[EUR-Lex：Commission Notice C/2025/214（第 11 条可拆卸性指南）](https://eur-lex.europa.eu/eli/C/2025/214/oj/eng) · A · 2026-11-01
- 疑点：各项义务（标签、二维码、CE 标志等）的具体适用日期本次没有逐条读到原文。
- 备注：第 11 条可拆卸要求单独列在 EU-11。

<a id="EU-11"></a>
### EU-11 电池法规第 11 条：便携式电池可由终端用户拆卸更换（2027-02-18 起）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）、纽扣电池
- 依据：Regulation (EU) 2023/1542 第 11 条；委员会指南 C/2025/214
- 要求：自 2027-02-18 起，含便携式电池的产品须设计成终端用户可用市售工具拆卸、更换电池（有例外情形，2026 年有授权法规增加了可由独立专业人员更换的产品类别）。义务在投放该产品的制造商/进口商。
- 适用条件：产品含便携式电池（含纽扣电池、内置锂电池），计划 2027-02-18 以后在欧盟投放。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。设计要求，写进技术文件；例外情形需要论证。
- 来源：
  - 法规原文：[EUR-Lex：Regulation (EU) 2023/1542](https://eur-lex.europa.eu/eli/reg/2023/1542/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方指南：[EUR-Lex：Commission Notice C/2025/214（第 11 条指南）](https://eur-lex.europa.eu/eli/C/2025/214/oj/eng) · A · 2026-11-01
- 疑点：2026 年新增例外（如可穿戴设备）的最终文本和状态没读到；外壳用卡扣/胶粘的产品要尽早评估。
- 备注：对外壳设计（B 线）影响大：电池仓要能用普通工具打开。

<a id="EU-12"></a>
### EU-12 通用产品安全法规 GPSR (EU) 2023/988

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：Regulation (EU) 2023/988
- 要求：消费品须安全（覆盖其他专门法规没管到的风险）；制造商须做内部风险分析、编制技术文件、标注识别和联系信息，在欧盟须有负责的经营者；在线销售有额外信息要求。2024-12-13 起适用，取代 2001/95/EC。
- 适用条件：所有面向消费者的产品。
- 证据形式：一般安全义务（无固定证书，靠风险评估和技术文件）。没有证书；靠风险评估、技术文件和标签。
- 来源：
  - 法规原文：[EUR-Lex：Regulation (EU) 2023/988](https://eur-lex.europa.eu/eli/reg/2023/988/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 欧盟机构页面：[EU-OSHA：Regulation 2023/988/EU general product safety](https://osha.europa.eu/en/legislation/directive/regulation-2023988eu-general-product-safety) · A · 2026-11-01
  - 官方解读：[GOV.UK：EU Regulation 2023/988 on general product safety factsheet（北爱尔兰适用说明）](https://www.gov.uk/government/publications/general-product-safety-regulations-northern-ireland/eu-regulation-2023988-on-general-product-safety-factsheet) · A · 2026-11-01
- 疑点：欧盟负责经营者的具体条款（GPSR 与市场监管法规 (EU) 2019/1020 的衔接）条款号待核实。

<a id="EU-13"></a>
### EU-13 玩具安全：指令 2009/48/EC → 新法规 (EU) 2025/2509

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：儿童用（玩具/儿童产品）
- 依据：Directive 2009/48/EC；Regulation (EU) 2025/2509（Toy Safety Regulation）
- 要求：供 14 岁以下儿童玩耍的产品须满足玩具安全基本要求（物理机械、可燃性、化学、电气等），签发符合性声明、加施 CE、附警示。新法规 (EU) 2025/2509 于 2025-12-12 公布，多数资料称 2030-08-01 起全面取代 2009/48/EC，在此之前符合旧指令的玩具仍可投放。
- 适用条件：产品设计或预期供 14 岁以下儿童玩耍。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。完整采用协调标准（EN 71 系列、电玩具标准）时可自我声明；否则需要欧盟型式检验（公告机构）。
- 来源：
  - 法规原文：[EUR-Lex：Directive 2009/48/EC](https://eur-lex.europa.eu/eli/dir/2009/48/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 法规原文：[EUR-Lex：Regulation (EU) 2025/2509](https://eur-lex.europa.eu/eli/reg/2025/2509/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[European Commission：Toy safety](https://single-market-economy.ec.europa.eu/sectors/toys/toy-safety_en) · A · 2026-11-01
- 疑点：新法规的适用和过渡日期各来源冲突（2026-01-01 生效；2026-08-01 / 2030-08-01 适用），以 EUR-Lex 原文为准。新法规对数字产品护照等新义务的生效日未读到。
- 备注：带无线功能的玩具还落入 EU-03（RED 网络安全授权法规中的玩具类）。

<a id="EU-14"></a>
### EU-14 纽扣电池：未查到欧盟专门针对"含纽扣电池产品"的强制法规

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：纽扣电池
- 依据：未查到专门法规；由 GPSR (EU) 2023/988 一般安全要求、玩具安全法规、电池法规覆盖
- 要求：本次没有找到类似美国 Reese's Law 的欧盟专门法规。纽扣电池误吞风险由 GPSR 一般安全义务覆盖，玩具中的电池可触及性由玩具安全要求覆盖。
- 适用条件：产品使用纽扣/硬币电池，在欧盟销售。
- 证据形式：一般安全义务（无固定证书，靠风险评估和技术文件）。风险评估中写明电池仓固定方式和警示。
- 来源：
  - 法规原文：[EUR-Lex：Regulation (EU) 2023/988（GPSR）](https://eur-lex.europa.eu/eli/reg/2023/988/oj) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
- 疑点：是否有欧盟层面的纽扣电池专门标准化委托或协调标准正在实施，没查到官方页面。

<a id="EU-15"></a>
### EU-15 锂电池运输：ADR（经 2008/68/EC 在欧盟境内适用）与 UN 38.3 测试摘要

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）、纽扣电池
- 依据：Directive 2008/68/EC（内陆危险货物运输）附件 I 第 I.1 节 = ADR；Commission Delegated Directive (EU) 2025/149（适用 ADR 2025）；空运 ICAO TI / IATA DGR，海运 IMDG Code
- 要求：Directive 2008/68/EC 规定欧盟境内公路、铁路、内河危险货物运输适用 ADR / RID / ADN；2025/149 号授权指令把附件更新为 2025-01-01 起适用的 ADR 版本（过渡期到 2025-06-30）。锂电池在 ADR 中属于第 9 类危险货物：运输前须通过 UN 38.3 测试，制造商和后续分销商须提供测试摘要（第三方资料：ADR 2.2.9.1.7，2020-01-01 起）。小电芯/小电池按特殊规定 188 可以简化包装和文件。进出欧盟的空运按 ICAO 技术细则 / IATA DGR，海运按 IMDG Code。
- 适用条件：产品含锂离子电池或锂金属纽扣电池，运进欧盟或在欧盟境内运输（含电商发货、退货）。
- 证据形式：第三方测试（指定或认可的实验室出报告）。UN 38.3 测试报告和测试摘要向电池供应商索取；包装、标记、文件按承运人和货代要求。
- 来源：
  - 官方页面：[EU-OSHA：Directive 2008/68/EC on the inland transport of dangerous goods](https://osha.europa.eu/en/legislation/directives/directive-2008-68-ec) · A · 2026-11-01
  - 法规原文：[EUR-Lex：Commission Delegated Directive (EU) 2025/149](https://eur-lex.europa.eu/eli/dir_del/2025/149/oj/eng/pdf) · S · 2026-11-01
  - 第三方解读：[TÜV Rheinland：Lithium batteries transport（2025-01）](https://tuv.com/content-media-files/germany/bs-products/pdfs/other/tuev-rheinland-lithiumbatteries-transport-01-2025-en.pdf) · C · 2026-11-01
- 疑点：已核实的是"欧盟境内运输适用 ADR，且已更新到 ADR 2025"。ADR 中锂电池的具体条款号（2.2.9.1.7、测试摘要义务、特殊规定 188 的 Wh / 锂含量门限）只来自第三方资料，UNECE ADR 原文本次没有读到。2027 年起 ADR 是否再改锂电池条款未查。
- 备注：测试摘要义务与美国 US-08 相同，可以共用一份供应商文件。

## US · 美国 FCC / CPSC

<a id="US-01"></a>
### US-01 FCC Part 15 Subpart C 有意辐射体：设备认证（Certification）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：无线（Wi-Fi / BLE 等）
- 依据：47 CFR Part 15 Subpart C；47 CFR 2.907（Certification）
- 要求：Wi-Fi、蓝牙等有意辐射体在销售前须取得 FCC 认证：由 FCC 认可的实验室测试，经 TCB（电信认证机构）审核后发 FCC ID 授权；产品标注 FCC ID 和 Part 15 声明（47 CFR 15.19）。
- 适用条件：产品含无线发射功能，在美国销售。
- 证据形式：认证 / 型号核准（由认证机构或主管部门发证）。整机自带射频设计时自己申请 FCC ID；使用已认证模组时见 US-02。
- 来源：
  - 法规原文：[eCFR：47 CFR Part 15 Subpart C—Intentional Radiators](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C) · S · 2026-11-01
  - 官方解读：[FCC：Certification (47 CFR Section 2.907)](https://www.fcc.gov/node/23689) · A · 2026-11-01
- 疑点：2025 年起 FCC 对"受管控清单"相关实体和测试实验室有新的限制（第三方资料），选实验室时确认。

<a id="US-02"></a>
### US-02 使用已认证模组（模块化批准）的条件

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：无线（Wi-Fi / BLE 等）
- 依据：47 CFR 15.212（Modular transmitters）；FCC KDB 996369（模组集成指南）
- 要求：使用已取得模块化批准的无线模组时，整机通常不需要重新做有意辐射体认证，但须：按模组授权书的条件安装（天线、布线、RF 暴露限制等），模组 FCC ID 在整机外部不可见时，在整机外部标注"Contains FCC ID: xxx"或同义文字；整机作为数字设备仍需满足 Part 15 Subpart B（US-03）。有限模块化批准（LMA）只适用于授权书限定的主机。模组被封闭且不可即插即换、或不满足授权条件时，整机需要新的 FCC ID。
- 适用条件：产品使用已认证的 Wi-Fi/BLE 模组（例如 ESP32 系列模组），在美国销售。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。整机厂负责按授权条件集成并保留证据；需要变更时做 Class II 许可变更或新认证。
- 来源：
  - 法规原文：[eCFR：47 CFR 15.212 Modular transmitters](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.212) · S · 2026-11-01
  - 第三方解读：[Ezurio（原 Laird）：FCC Guidance for Incorporating Transmitter Modules（引用 KDB 996369）](https://www.ezurio.com/resources/white-papers/fcc-guidance-on-transmitter-modules) · C · 2026-11-01
- 疑点：KDB 996369 各分册（D01/D04 等）的现行版本号没有在 FCC 官网核对（KDB 站点本次无法访问）。
- 备注：选模组时看授权书（Grant）里的条件和天线类型；改天线常常就不满足条件了。

<a id="US-03"></a>
### US-03 FCC Part 15 Subpart B 无意辐射体（数字设备）：SDoC

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：47 CFR Part 15 Subpart B；47 CFR 2.906（Supplier's Declaration of Conformity）
- 要求：含数字电路（有时钟）的设备属于无意辐射体，B 类（家用）数字设备一般走供应商符合性声明（SDoC）：自行测试合规、由美国境内的负责方保存记录、产品附合规信息；不需要向 FCC 提交。也可以选择走认证。
- 适用条件：所有含数字电路的电子产品（Part 15 有豁免条款，见疑点）。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。由实验室按 Part 15 B 类限值测试，负责方保存测试报告和 SDoC。
- 来源：
  - 法规原文：[eCFR：47 CFR Part 15 Subpart B—Unintentional Radiators](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-B) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 法规原文：[eCFR：47 CFR Part 2 Subpart J—Equipment Authorization Procedures（含 2.906）](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-2/subpart-J) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 法规镜像：[Cornell LII：47 CFR 2.906（镜像）](https://www.law.cornell.edu/cfr/text/47/2.906) · C · 2026-11-01
- 疑点：Part 15 Subpart B 的设备分类表和豁免条款（例如低功耗或特定用途的数字设备）本次没有读到原文；电池供电的小设备是否落入豁免，需要实验室判断。
- 备注：带无线的产品，非无线部分（数字电路）同样要做 Subpart B 评估。

<a id="US-04"></a>
### US-04 FCC U.S. Cyber Trust Mark（自愿 IoT 网络安全标签）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：联网（网络安全）
- 依据：FCC 自愿网络安全标签计划（U.S. Cyber Trust Mark）
- 要求：自愿项目：符合计划网络安全标准的物联网设备可申请使用该标签。美国联邦层面本次未查到对消费类联网设备的强制网络安全要求。
- 适用条件：联网消费类设备，自愿参加。
- 证据形式：自愿项目。由计划指定的认可实验室测试、管理机构审核。
- 来源：
  - 官方文件：[FCC 文件 DOC-420764A1（Cyber Trust Mark 相关）](https://docs.fcc.gov/public/attachments/DOC-420764A1.txt) · A · 2026-11-01
  - 媒体报道：[Nextgov（2026-10）：FCC 委员称希望一年内消费者能看到带标签的产品](https://www.nextgov.com/cybersecurity/2026/10/fcc-commissioner-hopes-cyber-trust-mark-products-reach-shoppers-within-year/416878/) · C · 2026-11-01
- 疑点：第三方报道称原牵头管理机构 2025 年底退出，2026-04-13 FCC 选定新的牵头管理机构，截至 2026-10 标签尚未在零售端上线；没有读到 FCC 官方的现状公告。部分州（如加州）有联网设备安全法，本库未展开。

<a id="US-05"></a>
### US-05 CPSC Reese's Law：含纽扣/硬币电池的消费品（16 CFR part 1263）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：纽扣电池、儿童用（玩具/儿童产品）
- 依据：16 CFR part 1263（采纳 ANSI/UL 4200A-2023 并附加要求）
- 要求：2023-10-23 及以后制造或进口、含纽扣/硬币电池的消费品须：电池仓在可预见使用和误用下保持固定（防儿童打开）、通过性能测试、产品和包装带警示标签和说明。锌空电池不适用第 1263 部分。电池本身的包装须符合防毒包装法。儿童产品须由 CPSC 认可的第三方实验室测试（2023-12-20 起）。
- 适用条件：产品使用纽扣/硬币电池（直径大于高度的单体电池），在美国销售。
- 证据形式：第三方测试（指定或认可的实验室出报告）。普通消费品：一般符合性证书（GCC），可自测；儿童产品：第三方测试 + 儿童产品证书（CPC）。
- 来源：
  - 法规原文：[Federal Register 2023-20334：Safety Standard for Button Cell or Coin Batteries（最终规则）](https://www.govinfo.gov/content/pkg/FR-2023-09-21/html/2023-20334.htm) · S · 2026-11-01
  - 官方解读：[CPSC：Button Cell and Coin Battery（企业指南）](https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Button-Cell-and-Coin-Battery) · A · 2026-11-01
  - 官方 FAQ：[CPSC：Button Cell and Coin Battery FAQs](https://www.cpsc.gov/FAQ/Button-Cell-and-Coin-Battery-FAQs) · A · 2026-11-01
- 疑点：符合 ASTM F963 电池要求的玩具是否豁免第 1263 部分，只在第三方资料中看到，需按 CPSC 原文确认；2026 年有修订自愿标准的征求意见（Federal Register 公示），结果未知。

<a id="US-06"></a>
### US-06 CPSIA 儿童产品：第三方测试、儿童产品证书、追踪标签；玩具 ASTM F963

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：儿童用（玩具/儿童产品）
- 依据：Consumer Product Safety Improvement Act；16 CFR part 1250（玩具安全，采纳 ASTM F963）
- 要求：主要供 12 岁及以下儿童使用的产品，须由 CPSC 认可的第三方实验室按适用规则测试，进口商或美国制造商据此签发 儿童产品证书（CPC）；产品和包装须（在可行时）永久标注追踪标签。玩具须符合 ASTM F963。
- 适用条件：产品面向 12 岁及以下儿童，在美国销售。
- 证据形式：第三方测试（指定或认可的实验室出报告）。CPSC 认可实验室（按测试项目逐项认可）测试；CPC 由进口商/制造商签发，不由实验室签发。
- 来源：
  - 法规原文：[eCFR：16 CFR Part 1250—Safety Standard Mandating ASTM F963 for Toys](https://www.ecfr.gov/current/title-16/chapter-II/subchapter-B/part-1250) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方 FAQ：[CPSC：FAQs Certification and Third Party Testing](https://www.cpsc.gov/Business--Manufacturing/Testing-Certification/Third-Party-Testing/FAQs-Certification-and-Third-Party-Testing-OLD) · A · 2026-11-01
  - 官方培训材料：[CPSC 讲义：Key Procedural Requirements（2016）](https://cpsc.gov/s3fs-public/Session-2-CPSC-Key-Procedural-Requirements-China-2016-Williams-FINAL-Eng.pdf) · A · 2026-11-01
- 疑点：现行 ASTM F963 的强制版本（第三方称 F963-23）没有在 CPSC 官方页面上核对；本次找到的 CPSC 页面部分是旧版（URL 带 OLD）。
- 备注：带纽扣电池的儿童产品同时看 US-05。

<a id="US-07"></a>
### US-07 DOE 外部电源能效标准（10 CFR 430.32(w)，Level VI）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：随附电源适配器
- 依据：10 CFR 430.32(w)
- 要求：在美国制造和销售的外部电源须满足 10 CFR 430.32(w) 规定的能效标准（Level VI），并按 DOE 要求认证和报告。
- 适用条件：随附外部电源（适配器）。
- 证据形式：注册 / 备案 / 生产者责任登记。适配器制造商向 DOE 合规认证数据库报告；整机厂采购时核对适配器的 Level VI 标识和登记。
- 来源：
  - 法规原文：[eCFR：10 CFR 430.32 Energy and water conservation standards](https://www.ecfr.gov/current/title-10/chapter-II/subchapter-D/part-430/subpart-C/section-430.32) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[U.S. DOE：External Power Supplies](https://www.energy.gov/eere/buildings/external-power-supplies) · A · 2026-11-01
- 疑点：DOE 页面显示有"拟废止外部电源能效法规"的通知，是否已最终生效未查到。

<a id="US-08"></a>
### US-08 锂电池运输：49 CFR 173.185 与 UN 38.3 测试摘要

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）、纽扣电池
- 依据：49 CFR 173.185；UN《试验和标准手册》第三部分 38.3
- 要求：锂电池（含锂离子和锂金属纽扣电池）运输前须通过 UN 38.3 测试；2008-01-01 及以后制造的锂电芯/电池，其制造商和后续分销商须提供测试摘要（test summary）。含电池的设备运输有包装、标记和数量方面的要求和例外。
- 适用条件：产品含锂离子电池，或含锂金属纽扣电池（如 CR 系列），需要运输（含快递、空运）。
- 证据形式：第三方测试（指定或认可的实验室出报告）。向电池供应商索取 UN 38.3 测试报告和测试摘要；整机包装按承运方要求。
- 来源：
  - 法规原文：[eCFR：49 CFR 173.185 Lithium cells and batteries](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-C/part-173/subpart-E/section-173.185) · S · 2026-11-01
  - 官方指南：[PHMSA：Lithium Battery Test Summary (2024)](https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2024-09/Lithium-Battery-Test-Summary-2024.pdf) · A · 2026-11-01
- 疑点：小型消费设备的例外条款（173.185(c) 等）现行文本没有读到；空运还要看 IATA DGR，本库未展开。碱性/锌空纽扣电池不属于锂电池。
- 备注：运输要求在所有市场都适用：中国出口和空运见 CN-10、CN-11，欧盟 EU-15，英国 UK-12，澳大利亚 AU-09。

<a id="US-09"></a>
### US-09 锂电池产品安全：未查到联邦层面的专门强制标准（一般安全义务）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）
- 依据：未查到专门联邦法规；适用 CPSC 一般产品安全管辖
- 要求：本次没有找到适用于一般小型消费电子内置锂电池的联邦强制安全标准（UL 2054 / UL 62133 等为自愿标准，但零售渠道常作为准入条件）。CPSC 可对存在缺陷的产品要求召回。
- 适用条件：产品内置可充电锂电池，在美国销售。
- 证据形式：一般安全义务（无固定证书，靠风险评估和技术文件）。未查到强制证书；建议电池选用有 UL/IEC 62133 报告的电芯/电池组。
- 来源：
  - 官方页面：[CPSC 企业指南示例页（纽扣电池；未找到锂电池专页，仅作 CPSC 官方指南入口）](https://www.cpsc.gov/Business--Manufacturing/Business-Education/Business-Guidance/Button-Cell-and-Coin-Battery) · A · 2026-11-01
- 疑点：只能说"未查到"，不能证明不存在；部分州（如纽约州对电动出行设备电池）有州法，小型消费电子是否受影响未查。

<a id="US-10"></a>
### US-10 适配器电气安全：未查到联邦强制认证（NRTL 列名属渠道要求）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：随附电源适配器
- 依据：未查到专门联邦法规
- 要求：本次没有找到要求消费类电源适配器必须取得 NRTL（如 UL、ETL）列名的联邦法规；但大型零售商和电商平台 普遍要求。适配器能效见 US-07，适配器作为数字设备的电磁辐射见 US-03。
- 适用条件：随附电源适配器，在美国销售。
- 证据形式：一般安全义务（无固定证书，靠风险评估和技术文件）。建议采购已有 UL/ETL 等列名的适配器并保存证书。
- 来源：
  - 法规原文：[eCFR：47 CFR Part 15 Subpart B（适配器开关电源的电磁辐射）](https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-B) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
- 疑点：消费品适配器安全的联邦要求本次没有找到官方说明，零售渠道要求也未核实。

## UK · 英国 UKCA

<a id="UK-01"></a>
### UK-01 Radio Equipment Regulations 2017（英国无线电设备条例）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：无线（Wi-Fi / BLE 等）
- 依据：The Radio Equipment Regulations 2017（SI 2017/1206）
- 要求：无线电设备须满足安全、EMC、有效使用频谱等基本要求，制造商编制技术文件和符合性声明，加施 UKCA 标志（大不列颠）；北爱尔兰按欧盟规则使用 CE。
- 适用条件：产品含无线电功能，在英国销售。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。与 EU RED 类似：采用指定标准可自我声明，否则需要英国批准机构。
- 来源：
  - 法规原文：[legislation.gov.uk：The Radio Equipment Regulations 2017](https://www.legislation.gov.uk/uksi/2017/1206/contents) · S · 2026-11-01
  - 官方解读：[GOV.UK：Radio Equipment Regulations 2017: Great Britain（法定指南）](https://www.gov.uk/government/publications/radio-equipment-regulations-2017/radio-equipment-regulations-2017-great-britain) · A · 2026-11-01
  - 官方公告：[GOV.UK：UK Government announces extension of CE mark recognition for businesses](https://www.gov.uk/government/news/uk-government-announces-extension-of-ce-mark-recognition-for-businesses) · A · 2026-11-01
- 疑点：英国政府宣布对其主管的多部产品法规"无限期"继续承认 CE 标志，但本次没有读到覆盖清单，Radio Equipment Regulations 2017 是否在内待核实。
- 备注：在大不列颠可否只用 CE 标志，以 GOV.UK 清单为准。

<a id="UK-02"></a>
### UK-02 Electromagnetic Compatibility Regulations 2016（无无线功能的产品）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：The Electromagnetic Compatibility Regulations 2016
- 要求：设备须满足电磁兼容基本要求，编制技术文件和符合性声明，加施 UKCA（或按承认安排加施 CE）。
- 适用条件：不含无线电功能的电子产品（含无线的由 UK-01 覆盖）。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。内部生产控制。
- 来源：
  - 官方解读：[GOV.UK：Electromagnetic Compatibility Regulations 2016: Great Britain（法定指南）](https://www.gov.uk/government/publications/electromagnetic-compatibility-regulations-2016/electromagnetic-compatibility-regulations-2016-great-britain) · A · 2026-11-01
- 疑点：本次没有在搜索结果里看到该条例在 legislation.gov.uk 的原文链接（SI 编号未核对）。

<a id="UK-03"></a>
### UK-03 Electrical Equipment (Safety) Regulations 2016（随附市电适配器）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：随附电源适配器
- 依据：The Electrical Equipment (Safety) Regulations 2016（SI 2016/1101）
- 要求：规定电压范围内的电气设备须满足安全目标，制造商编制技术文件和符合性声明，加施 UKCA（或按承认安排加施 CE）。
- 适用条件：随附交流市电输入的电源适配器。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。采购现成适配器时保存其符合性声明和测试报告。
- 来源：
  - 法规原文：[legislation.gov.uk：The Electrical Equipment (Safety) Regulations 2016](https://www.legislation.gov.uk/uksi/2016/1101/contents) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[GOV.UK：Electrical Equipment (Safety) Regulations 2016（法定指南）](https://www.gov.uk/government/publications/electrical-equipment-safety-regulations-2016) · A · 2026-11-01
- 疑点：法定指南页面只在归档快照里看到标题，现行内容没有读到。

<a id="UK-04"></a>
### UK-04 RoHS Regulations 2012（英国有害物质限制）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：The Restriction of the Use of Certain Hazardous Substances in Electrical and Electronic Equipment Regulations 2012（SI 2012/3032）
- 要求：电子电气设备中限用物质不得超标；纳入符合性声明。大不列颠有独立的豁免制度。
- 适用条件：所有在英国销售的电子电气产品。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。物料合规声明 / 检测报告存入技术文件。
- 来源：
  - 法规原文：[legislation.gov.uk：SI 2012/3032](https://www.legislation.gov.uk/uksi/2012/3032/contents) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[GOV.UK：RoHS Regulations 2012 (as amended): Great Britain](https://www.gov.uk/government/publications/restriction-of-hazardous-substances-rohs-regulations/rohs-regulations-2012-as-amended-great-britain) · A · 2026-11-01

<a id="UK-05"></a>
### UK-05 WEEE Regulations 2013（生产者责任）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：The Waste Electrical and Electronic Equipment Regulations 2013（SI 2013/3113）
- 要求：电子电气设备生产者每年登记，承担家用废弃设备的回收处理费用；年投放量低于 5 吨的小生产者可直接向环境主管机构登记。
- 适用条件：所有在英国销售的电子电气产品。
- 证据形式：注册 / 备案 / 生产者责任登记。加入生产者合规计划或按小生产者直接登记。
- 来源：
  - 法规原文：[legislation.gov.uk：SI 2013/3113](https://www.legislation.gov.uk/uksi/2013/3113/contents) · S · 2026-11-01
  - 官方解读：[GOV.UK：Regulations: waste electrical and electronic equipment (WEEE)](https://www.gov.uk/guidance/regulations-waste-electrical-and-electronic-equipment) · A · 2026-11-01
- 疑点：2025 年有修订（GOV.UK 提到），修订内容本次未读。

<a id="UK-06"></a>
### UK-06 英国电池法规（投放市场条例 2008、废电池条例 2009）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）、纽扣电池
- 依据：The Batteries and Accumulators (Placing on the Market) Regulations 2008；The Waste Batteries and Accumulators Regulations 2009（SI 2009/890）
- 要求：首次在英国投放电池（含装在产品里的电池）的生产者须登记、承担便携式电池的回收责任（通常加入电池合规计划），电池须满足设计、标记等投放市场要求。
- 适用条件：产品含任何电池（内置锂电池或纽扣电池），在英国销售。
- 证据形式：注册 / 备案 / 生产者责任登记。在国家包装废物数据库（NPWD）登记，通常通过电池合规计划。
- 来源：
  - 法规原文：[legislation.gov.uk：The Waste Batteries and Accumulators Regulations 2009](https://www.legislation.gov.uk/uksi/2009/890/contents) · S · 2026-11-01
  - 官方解读：[GOV.UK：Waste batteries: producer responsibility](https://www.gov.uk/guidance/waste-batteries-producer-responsibility) · A · 2026-11-01
  - 官方解读：[GOV.UK：Regulations: batteries and waste batteries](https://www.gov.uk/guidance/regulations-batteries-and-waste-batteries) · A · 2026-11-01
- 疑点：Defra 曾就修订电池法规征求意见，结果和新法规状态未查到。

<a id="UK-07"></a>
### UK-07 General Product Safety Regulations 2005（大不列颠一般产品安全）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：The General Product Safety Regulations 2005（SI 2005/1803）；Product Regulation and Metrology Act 2025（授权法）
- 要求：在大不列颠投放的消费品须安全，生产者须提供警示信息、标注识别信息、配合召回。北爱尔兰自 2024-12-13 起适用欧盟 GPSR。2025 年《产品监管与计量法》已获御准，授权政府以二级立法制定新的产品安全要求（包括在线市场）。
- 适用条件：所有面向消费者的产品。
- 证据形式：一般安全义务（无固定证书，靠风险评估和技术文件）。无证书；风险评估和技术文件。
- 来源：
  - 法规原文：[legislation.gov.uk：The General Product Safety Regulations 2005](https://www.legislation.gov.uk/uksi/2005/1803/contents) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[GOV.UK：General Product Safety Regulations 2005: Great Britain](https://www.gov.uk/government/publications/general-product-safety-regulations-2005/general-product-safety-regulations-2005-great-britain) · A · 2026-11-01
  - 第三方解读：[Jones Day：Product Regulation and Metrology Bill receives Royal Assent](https://www.jonesday.com/en/insights/2025/07/product-regulation-and-metrology-bill-receives-royal-assent) · C · 2026-11-01
- 疑点：《产品监管与计量法》下已经发布了哪些二级立法，未查到。

<a id="UK-08"></a>
### UK-08 Toys (Safety) Regulations 2011

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：儿童用（玩具/儿童产品）
- 依据：The Toys (Safety) Regulations 2011（SI 2011/1881）
- 要求：玩具须满足安全要求，制造商编制技术文件和符合性声明、加施 UKCA（或按承认安排加施 CE）、附警示。2026-02-13 英国更新了指定标准清单（部分条目有宽限期）。
- 适用条件：产品设计或预期供 14 岁以下儿童玩耍，在英国销售。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。采用指定标准时自我声明；否则需要英国批准机构型式检验。
- 来源：
  - 法规原文：[legislation.gov.uk：The Toys (Safety) Regulations 2011](https://www.legislation.gov.uk/uksi/2011/1881/contents) · S · 2026-11-01
  - 官方解读：[GOV.UK：Toys (Safety) Regulations 2011: Great Britain（法定指南）](https://www.gov.uk/government/publications/toys-safety-regulations-2011/toys-safety-regulations-2011-great-britain) · A · 2026-11-01
- 疑点：14 岁年龄界限沿用欧盟玩具指令定义，本次没有在英国条例原文中逐字核对。

<a id="UK-09"></a>
### UK-09 PSTI 产品安全制度（联网消费品网络安全）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：联网（网络安全）
- 依据：Product Security and Telecommunications Infrastructure Act 2022；The Product Security and Telecommunications Infrastructure (Security Requirements for Relevant Connectable Products) Regulations 2023（SI 2023/1007）
- 要求：2024-04-29 起，在英国供应的消费类可联网产品须满足附表 1 的安全要求（基于 ETSI EN 303 645：禁止通用默认密码、公布漏洞报告途径、公布最短安全更新期），并随附符合性声明（statement of compliance）。附表 3 列出例外产品。
- 适用条件：产品可联网（互联网可连接或网络可连接），面向消费者，在英国销售。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。制造商签发符合性声明随产品提供；进口商、分销商有核查义务。
- 来源：
  - 法规原文：[legislation.gov.uk：SI 2023/1007](https://www.legislation.gov.uk/uksi/2023/1007) · S · 2026-11-01
  - 法规原文：[legislation.gov.uk：SI 2023/1007 附表 1（安全要求）](https://www.legislation.gov.uk/uksi/2023/1007/schedule/1/made) · S · 2026-11-01
- 疑点：只通过 BLE 与手机通信的产品是否属于"网络可连接产品"，按附表和指南判断；GOV.UK 指南页本次未在搜索结果中出现。

<a id="UK-10"></a>
### UK-10 纽扣电池：未查到英国专门强制法规（PAS 7055 为自愿标准）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：纽扣电池
- 依据：无专门法规；General Product Safety Regulations 2005；PAS 7055（BSI，自愿）
- 要求：本次没有找到英国针对含纽扣电池产品的专门强制法规；纽扣电池安全由 GPSR 2005 一般安全义务覆盖。OPSS 支持制定的 PAS 7055 规定了电池、包装和含电池产品的安全要求，属于自愿标准。
- 适用条件：产品使用纽扣/硬币电池，在英国销售。
- 证据形式：一般安全义务（无固定证书，靠风险评估和技术文件）。风险评估时参考 PAS 7055。
- 来源：
  - 官方公告：[GOV.UK：OPSS supports new standard for battery safety](https://www.gov.uk/government/news/opss-support-new-standard-for-battery-safety) · A · 2026-11-01
- 疑点：《产品监管与计量法》2025 授权的二级立法中是否已有纽扣电池规则，未查到。

<a id="UK-11"></a>
### UK-11 外部电源生态设计（大不列颠保留的 2019/1782）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：随附电源适配器
- 依据：Commission Regulation (EU) 2019/1782（英国保留法版本）
- 要求：外部电源的能效、空载功耗和信息标示要求在大不列颠以保留法形式继续适用。
- 适用条件：随附外部电源（适配器），在大不列颠销售。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。采购时要求供应商提供能效测试数据。
- 来源：
  - 法规原文：[legislation.gov.uk：Commission Regulation (EU) 2019/1782（英国版本）](https://www.legislation.gov.uk/eur/2019/1782/contents) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
- 疑点：大不列颠版本是否有修订、是否跟随欧盟 2025/2052 更新，未查到。

<a id="UK-12"></a>
### UK-12 锂电池运输：Carriage of Dangerous Goods Regulations 2009（ADR 适用于国内运输）与 UN 38.3

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）、纽扣电池
- 依据：The Carriage of Dangerous Goods and Use of Transportable Pressure Equipment Regulations 2009（SI 2009/1348）；ADR；空运 ICAO TI，海运 IMDG Code
- 要求：SI 2009/1348 把 ADR（公路）、RID（铁路）、ADN（内河）的适用范围扩大到英国国内运输（"按不时修订的版本"）。锂电池在 ADR 中属于第 9 类危险货物，运输前须通过 UN 38.3 测试并由制造商和后续分销商提供测试摘要（第三方资料，见 EU-15）。进出英国的空运按 ICAO 技术细则 / IATA DGR，海运按 IMDG Code。
- 适用条件：产品含锂离子电池或锂金属纽扣电池，运进英国或在英国境内运输。
- 证据形式：第三方测试（指定或认可的实验室出报告）。同 EU-15：UN 38.3 测试报告和测试摘要向电池供应商索取。
- 来源：
  - 法规原文：[legislation.gov.uk：SI 2009/1348 The Carriage of Dangerous Goods and Use of Transportable Pressure Equipment Regulations 2009](https://www.legislation.gov.uk/uksi/2009/1348/contents) · S · 2026-11-01
  - 第三方解读：[TÜV Rheinland：Lithium batteries transport（2025-01）](https://tuv.com/content-media-files/germany/bs-products/pdfs/other/tuev-rheinland-lithiumbatteries-transport-01-2025-en.pdf) · C · 2026-11-01
- 疑点：已核实的是 SI 2009/1348 让 ADR 适用于英国国内运输；legislation.gov.uk 提示修订文本可能未完全更新，现行版本没有逐条核对。锂电池具体条款同 EU-15，只有第三方资料。英国民航局（CAA）空运危险品规定本次没查。

## AU · 澳大利亚 RCM

<a id="AU-01"></a>
### AU-01 ACMA 低干扰潜力设备（LIPD）类别许可（使用条件）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：无线（Wi-Fi / BLE 等）
- 依据：Radiocommunications (Low Interference Potential Devices) Class Licence 2025；Radiocommunications Act 1992
- 要求：Wi-Fi、蓝牙等低干扰设备在类别许可规定的频段和最大功率内使用，无需单独申请执照；2025-10-01 起施行，取代 2015 版。
- 适用条件：产品含 Wi-Fi / BLE 等短距离无线，在澳大利亚使用和销售。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。设计时确认频段和功率在类别许可范围内；供应端义务见 AU-02。
- 来源：
  - 官方解读：[ACMA：Low interference potential devices (LIPD) class licence](https://www.acma.gov.au/licences/low-interference-potential-devices-lipd-class-licence) · A · 2026-11-01
- 疑点：类别许可原文（legislation.gov.au）本次没有找到登记号。

<a id="AU-02"></a>
### AU-02 ACMA 无线设备供应方义务（技术标准、符合性声明、RCM）

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：无线（Wi-Fi / BLE 等）
- 依据：ACMA 设备规则和短距离设备标准（采纳 AS/NZS 4268）
- 要求：供应无线设备前须证明符合适用的技术标准，保存符合性记录、签发供应商符合性声明，注册为负责供应商并加施 RCM 标志。
- 适用条件：产品含无线功能，在澳大利亚销售。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。通常用测试报告（可用国际标准测试）+ 供应商符合性声明；在 EESS 国家数据库注册为负责供应商。
- 来源：
  - 官方解读：[EESS：ACMA Requirements – Use of RCM](https://www.eess.gov.au/rcm/acma-requirements-use-of-rcm/) · A · 2026-11-01
  - 官方解读：[ACMA：LIPD class licence](https://www.acma.gov.au/licences/low-interference-potential-devices-lipd-class-licence) · A · 2026-11-01
- 疑点：设备规则（Radiocommunications Equipment (General) Rules 2021）和短距离设备标准的原文、合规等级划分本次没有读到；AS/NZS 4268 的引用来自第三方。

<a id="AU-03"></a>
### AU-03 ACMA EMC 要求（EMC 标准 + 标签通知，合规等级 1/2/3）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：基础（所有带电子电路的产品）
- 依据：Radiocommunications Labelling (Electromagnetic Compatibility) Notice 2017 及 EMC 标准（立法登记号 F2018L00028，名称待核实）
- 要求：电子产品须符合适用的 EMC 标准；供应商按设备风险等级（合规等级 1/2/3）保存文件，须先在国家数据库注册为负责供应商，才能加施 RCM 标志。
- 适用条件：所有在澳大利亚销售的电子产品（含无线产品）。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。等级越高要求越多（测试报告、符合性声明）；ACMA 的"等级"与 EESS 的电气安全等级不是一回事。
- 来源：
  - 法规原文：[Federal Register of Legislation：F2018L00028](https://www.legislation.gov.au/F2018L00028/latest/text) · S · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
  - 官方解读：[EESS：ACMA Requirements – Use of RCM](https://www.eess.gov.au/rcm/acma-requirements-use-of-rcm/) · A · 2026-11-01
- 疑点：合规等级 1/2/3 各自的具体要求本次没有读到条文；F2018L00028 的正式名称没有确认。

<a id="AU-04"></a>
### AU-04 电气安全 EESS（随附市电适配器，等级 3 申报类）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：随附电源适配器
- 依据：电气设备安全系统（EESS），AS/NZS 4417.1 / 4417.2，及各州电气安全法
- 要求：低电压（市电）在范围内电气设备按风险等级管理；等级 3（高风险，含电源类申报产品）须取得认证证书、由负责供应商在 EESS 注册并加施 RCM。只由特低电压供电的产品本体不在 EESS 范围内。
- 适用条件：随附交流市电输入的电源适配器。
- 证据形式：认证 / 型号核准（由认证机构或主管部门发证）。适配器须有 EESS 认可的认证证书并注册；通常采购已注册的适配器。
- 来源：
  - 官方解读：[EESS：Level 3 – Electrical Equipment](https://eess.gov.au/registration/registration-in-scope-electrical-equipment/level-3) · A · 2026-11-01
  - 官方解读：[EESS：In-Scope Electrical Equipment（风险等级定义）](https://eess.gov.au/equipment/risk-level-definition) · A · 2026-11-01
  - 官方公告：[EESS 信息公告 21-030：Power supply / battery charger standards v2.0](https://www.eess.gov.au/wp-content/uploads/2026/07/21-030-Information-Bulletin-Power-supply-battery-charger-standards-v2.0.pdf) · A · 2026-11-01
- 疑点：适配器属于等级 3 来自认证机构资料，EESS 页面确认了等级 3 的注册/认证要求，但没读到 AS/NZS 4417.2 的产品清单原文；各州法规的覆盖范围待核实。

<a id="AU-05"></a>
### AU-05 纽扣/硬币电池强制安全标准和信息标准（2022-06-22 起强制）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：纽扣电池
- 依据：Consumer Goods (Products Containing Button/Coin Batteries) Safety Standard 2020；Consumer Goods (Products Containing Button/Coin Batteries) Information Standard 2020（及电池本身的两项标准）
- 要求：含纽扣/硬币电池的消费品须有安全的电池仓（例如需要工具才能打开）、通过规定测试，并在产品、包装和说明书上提供警示信息。电池本身另有包装要求。焊接固定在通信设备中的电池等有例外。
- 适用条件：产品使用纽扣/硬币电池，在澳大利亚销售。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。供应商须确保合规；是否强制第三方测试待核实（本次只读到摘要）。
- 来源：
  - 法规解释性说明：[Federal Register of Legislation：F2020L01658（解释性说明）](https://www.legislation.gov.au/F2020L01658/asmade/2020-12-21/es/original/pdf) · S · 2026-11-01
  - 官方指南：[Product Safety Australia：Button coin battery safety – a guide for business（PDF）](https://www.productsafety.gov.au/system/files/Button%20coin%20battery%20safety%20-%20a%20guide%20for%20business%20on%20the%20application%20of%20mandatory%20standards_2.pdf) · A · 2026-11-01
- 疑点：安全标准正文的具体测试条款本次没有读到，只读到摘要；F2020L01658 对应四项标准中的哪一项未逐一核对。

<a id="AU-06"></a>
### AU-06 36 个月及以下儿童玩具强制安全标准（小零件）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：儿童用（玩具/儿童产品）
- 依据：Consumer Goods (Toys for Children up to and including 36 Months of Age) Safety Standard 2023
- 要求：供 36 个月及以下儿童的玩具不得含有可被小零件圆筒容纳的小零件（防窒息），并对含电池玩具有专门要求。
- 适用条件：产品是面向 36 个月及以下儿童的玩具（更大年龄段的玩具还可能涉及其他强制标准，见疑点）。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。供应商须确保合规；建议做第三方测试留证。
- 来源：
  - 官方解读：[Product Safety Australia：Toys for children up to and including 36 months of age（强制标准）](https://www.productsafety.gov.au/product-safety-laws/safety-standards-bans/mandatory-standards/toys-for-children-up-to-and-including-36-months-of-age) · A · 2026-11-01
- 疑点：面向更大年龄儿童的玩具适用哪些强制标准（例如含磁铁、弹射、水上玩具等专项标准）本次没有逐一检索。
- 备注：带纽扣电池的玩具同时看 AU-05。

<a id="AU-07"></a>
### AU-07 智能设备网络安全标准（Cyber Security Act 2024 下的规则，2026-03-04 起）

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：联网（网络安全）
- 依据：Cyber Security (Security Standards for Smart Devices) Rules 2025（F2025L00276）
- 要求：2026-03-04 及以后制造、面向个人/家庭使用的可联网产品须满足最低网络安全要求：禁止通用默认密码、提供漏洞报告机制、公布最短安全更新支持期，并提供符合性声明。台式机和笔记本电脑除外。
- 适用条件：产品可直接或间接连接互联网，面向消费者，在澳大利亚销售。
- 证据形式：自我声明（制造商自测或委托测试后签发符合性声明）。制造商提供符合性声明（statement of compliance）。
- 来源：
  - 法规原文：[Federal Register of Legislation：Cyber Security (Security Standards for Smart Devices) Rules 2025](https://www.legislation.gov.au/F2025L00276/asmade) · S · 2026-11-01
  - 官方解读：[Department of Home Affairs：Security standards for smart devices](https://www.homeaffairs.gov.au/cyber-security-subsite/Pages/security-standards-for-smart-devices.aspx) · A · 2026-11-01
- 疑点：三项要求的具体条文（例如支持期如何声明）本次只读到摘要。

<a id="AU-08"></a>
### AU-08 锂电池产品：未查到联邦层面针对小型消费电子的强制标准

- 状态：**待核实** · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）
- 依据：未查到专门强制标准；适用澳大利亚消费者法一般安全义务
- 要求：本次没有找到适用于一般小型消费电子内置锂电池的联邦强制安全标准（电动出行设备电池有州层面规定，不在本库范围）。
- 适用条件：产品内置可充电锂电池，在澳大利亚销售。
- 证据形式：一般安全义务（无固定证书，靠风险评估和技术文件）。未查到。
- 来源：
  - 官方清单：[Product Safety Australia：Mandatory standards（强制标准清单入口）](https://www.productsafety.gov.au/product-safety-laws/safety-standards-bans/mandatory-standards) · A · 2026-11-01（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）
- 疑点：查过：WebSearch "lithium-ion batteries mandatory standard consumer products Australia 2026"，只找到旧报告和部长声明；需在强制标准清单中再核对。随附的电池充电器若为市电供电，见 AU-04。

<a id="AU-09"></a>
### AU-09 锂电池运输：空运按 CASR Part 92 + ICAO 技术细则；陆运按 ADG Code

- 状态：已核实 · 查询日期 2026-11-01
- 总表位置：锂电池（可充电锂离子/锂聚合物）、纽扣电池
- 依据：Civil Aviation Safety Regulations 1998 Part 92（危险物品航空运输）；ICAO《危险物品安全航空运输技术细则》；Australian Dangerous Goods Code（ADG Code 7.8，公路 / 铁路）
- 要求：航空运输危险物品受 CASR Part 92 管辖，其中"技术细则"指 ICAO《危险物品安全航空运输技术细则》；锂电池在技术细则中是危险物品，有包装说明和数量限制，运输前须通过 UN 38.3 测试（第三方资料，澳大利亚原文未单独核实）。公路 / 铁路运输按 ADG Code（第三方资料：7.8 版向国际规则靠拢、增加了锂电池 UN 编号；按特殊规定 188 运输的小电池仍属危险货物，单件含 2 个以上电池或 4 个以上电芯的设备需随附特殊规定 188 要求的文件）。
- 适用条件：产品含锂离子电池或锂金属纽扣电池，运进澳大利亚或在澳大利亚境内运输。
- 证据形式：第三方测试（指定或认可的实验室出报告）。UN 38.3 测试报告和测试摘要向电池供应商索取；包装和文件按承运人要求。
- 来源：
  - 法规文书：[Federal Register of Legislation：F2022N00318（引用 CASR Part 92 与 ICAO 技术细则的 CASA 文书）](https://www.legislation.gov.au/F2022N00318/asmade/2022-12-20/text/original/pdf) · S · 2026-11-01
  - 第三方解读：[Master Instruments：Sea and road freight compliance summary（锂电池，IMDG 2018 / ADG）](https://www.master-instruments.com.au/files/knowledge-centre/transportation/lithium_battery_summary_for_sea__road_imdg2018_v3___2020_edn.pdf) · C · 2026-11-01
  - 第三方解读：[TT Club：TT Talk - Lithium complexities](https://www.ttclub.com/news-and-resources/news/article/tt-talk-lithium-complexities/) · C · 2026-11-01
- 疑点：已核实的是"空运受 CASR Part 92 管辖、技术细则指 ICAO 文件"（来自一份引用 Part 92 的 CASA 文书，不是 Part 92 本身）。ADG Code 现行版本和锂电池条款本次没有在 ntc.gov.au 读到，只有第三方摘要；UN 38.3 测试摘要在澳大利亚陆运中的要求未单独核实。
- 备注：澳大利亚市场的产品安全（非运输）要求见 AU-08。

---

再次说明：这是资料整理，不是法律意见。
