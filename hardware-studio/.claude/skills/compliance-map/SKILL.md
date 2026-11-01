---
name: compliance-map
description: 小型电子产品的合规资料地图：按产品特征（无线、联网、锂电池、纽扣电池、随附适配器、儿童用）列出中国、欧盟 CE、美国 FCC/CPSC、英国 UKCA、澳洲 RCM 可能涉及的法规、适用条件和证据形式，并生成某个产品的检查清单。Use when planning certification/compliance for a new gadget, estimating which tests or certificates a product needs per market, or updating the regulation entries in compliance/. 只整理资料，不下法律结论。
---

# 合规地图

**这是资料整理，不是法律意见。** 用它提前知道"大概要查哪些法规、要什么形式的证据"，
最终是否适用、怎么做，以法规原文和认证机构 / 检测机构的书面意见为准。

## 什么时候用

- 新产品立项或选型时：判断加不加无线、用锂电池还是纽扣电池、随不随附适配器、是不是玩具，对合规工作量的影响；
- 准备找检测机构报价前：先列出要问的项目；
- 法规有变化、需要更新条目时（见最后一节）。

## 文件

| 文件 | 作用 |
|---|---|
| `compliance/data/requirements.yaml` | 唯一数据源：每条要求的市场、触发条件、证据形式、来源链接、级别、日期、状态 |
| `compliance/map.md` | 由 YAML 生成的总表（特征 × 市场）和正文，**不要手改** |
| `compliance/build_map.py` | 生成 / 检查 map.md（`--check`） |
| `compliance/checklist.py` | 按产品特征输出检查清单（Markdown） |
| `compliance/examples/` | 四个典型产品的输入（`.yaml`）和输出清单（`.md`） |
| `compliance/tests/` | pytest：数据完整性、触发逻辑、map.md 一致性、示例清单是否最新 |

## 怎么输入产品特征

写一个产品 YAML（可以放在 `products/<产品名>/compliance.yaml`）：

```yaml
name: 我的桌面摆件
wireless: [wifi]        # wifi / ble / other；没有无线写 []
connected: true         # 直接或经手机 App 间接上网就写 true；省略时"有 Wi-Fi 即联网"
batteries: []           # lithium（可充电锂离子/锂聚合物）/ coin（纽扣电池）
adapter: false          # 包装里是否随附电源适配器/充电器
children: false         # 是否给儿童用（玩具/儿童产品）
markets: [CN, EU, US, UK, AU]
```

然后运行（在 `hardware-studio/` 下，先 `. .venv/bin/activate`）：

```bash
python compliance/checklist.py --product products/<产品名>/compliance.yaml --out products/<产品名>/compliance_checklist.md
# 或者直接用命令行参数：
python compliance/checklist.py --wireless ble --battery coin --children --markets CN,EU
```

输入值不合法时退出码为 2 并给出提示。检查数据和总表是否一致（不改文件）：`python compliance/build_map.py --check`（退出码 0 = 一致）。

怎么检查结果：清单开头"共 N 条，其中待核实 M 条"；逐条看标题是否符合产品特征——例如没有电池却出现电池法规、
有无线却出现单独的 EMC 指令（无线产品的 EMC 由 RED 覆盖），说明特征写错了，回去改产品 YAML。

特征怎么判断：

- **联网**：只用 BLE 连手机、但数据经 App 上云的，各地法规可能都算"间接联网"。拿不准时分别用
  `connected: true` 和 `false` 跑两次，把差异条目拿去问认证机构。
- **随附适配器**：只有充电口、包装里不给充电器的，写 `false`。
- **儿童用**：欧盟/英国玩具定义按"14 岁以下儿童玩耍"，美国 CPSIA 按"12 岁及以下"，澳洲小零件标准按"36 个月及以下"——年龄段不同，都要看。

## 怎么读结果

- 清单开头和结尾都有免责声明；中间按市场列条目，每条有：依据、要求、适用条件、证据形式、来源链接（级别 S/A/C + 查询日期）、疑点、备注。
- **✅ 已核实**：在搜索结果里见到了官方（S/A 级）页面，要点一致。仍然不等于"适用于你的产品"。
- **⚠️ 待核实**：只有第三方来源、来源冲突、或适用范围拿不准；"疑点"里写了具体问题。
- 来源后面标"按官方 URL 规则拼出"的链接，本次没有实际打开过，用前先点开核对。
- 证据形式：自我声明 / 第三方测试 / 认证（型号核准）/ 注册登记 / 一般安全义务 / 自愿项目。
- "按当前特征没有匹配的条目"不代表没有要求。

## 哪些必须找认证机构确认

1. 所有"待核实"条目；
2. 产品归类：中国 CCC 目录（CN-03/04/05/06）、中国 RoHS 达标管理目录（CN-07）、欧盟通用充电器类别（EU-02）、玩具定义、"可联网产品"定义（EU-03/04、UK-09、AU-07）；
3. 无线：用已认证模组时整机要做的测试——中国 SRRC 与微功率免核准的边界（CN-01/02，最大疑点）、FCC 模组授权条件（US-02）、RED 整机评估（EU-01）、ACMA（AU-02）；
4. 测试项目、样机数量、周期、费用。

## 怎么更新法规条目

1. 按 `.claude/skills/research-method/SKILL.md` 查资料：法规条款必须来自 S 级（法规原文、监管机构原文），再附一个 A 级官方解读；
   只有第三方资料或理解没把握的，`status: 待核实` 并在 `doubts` 写清楚疑点。不凭记忆写条款号。
2. 改 `compliance/data/requirements.yaml`（字段说明在 `build_map.py` 顶部）：
   - 新条目编号用市场前缀 + 两位序号（如 `EU-15`），不要重用旧编号；
   - `trigger` 用 `all` / `any` / `none` 组合以下条件：`always`、`wireless`、`wifi`、`ble`、`connected`、`lithium`、`coin`、`adapter`、`children`；
   - `features` 决定条目出现在总表的哪一行；
   - 每个来源写 `level`（S/A/B/C）和 `access`（`search` = 在搜索/打开中实际见到；`pattern` = 按 URL 规则拼出）；
   - 改 `checked` 为查询日期。
3. 重新生成并检查：

   ```bash
   cd compliance
   python build_map.py
   for f in examples/*.yaml; do python checklist.py --product "$f" --out "${f%.yaml}.md"; done
   python -m pytest tests -q
   ```

   测试会检查：每条都有链接；没有 S/A 级来源的必须是待核实且写了疑点；已核实的至少有一个实际见到的 S/A 来源；
   总表每格都有条目；map.md 和示例清单与 YAML 一致；触发逻辑（无线、电池、玩具、适配器、联网）。

## 已知局限（2026-11-01）

- 本次所有官方站点都无法直接打开（网络策略拦截），核实依赖搜索结果中的官方页面摘要；
- 时效性强的条目：欧盟 RED 网络安全授权法规 2027-12-11 废止并由 CRA 接管（EU-03/04）、电池法规第 11 条 2027-02-18 起（EU-11）、
  中国玩具 CCC 新规则 2026-11-01 起（CN-06）、中国 RoHS 新目录和 GB 26572—2025 于 2027-08-01 起（CN-07）、
  欧盟玩具安全新法规过渡期（EU-13）。使用时先确认这些日期之后有没有变化。
