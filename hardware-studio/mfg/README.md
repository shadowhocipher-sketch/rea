# mfg/ 从原型到量产

| 文件 | 内容 |
|---|---|
| `cost.py` | BOM 成本计算：多数量档、阶梯价、MOQ、损耗、一次性费用、实查/待核实/估算金额占比 |
| `prices/` | 价格缓存（YAML），每条带链接、日期、状态 |
| `pricing.md` | 价格查询固定流程 |
| `jlcparts_import.py` | 打不开分销商网站时，从 jlcparts 镜像按立创编号导出阶梯价 |
| `production-routes.md` | 开发板 / 模组加底板 / 芯片整板的决策表 |
| `esp32s3-min-system.md` | ESP32-S3 最小系统设计要点（附乐鑫硬件设计指南章节链接） |
| `kicad_check.py`、`kicad/minimal/` | KiCad ERC/DRC 检查脚本和最小测试工程 |
| `examples/` | 通用示例 BOM 和它们的成本输出（`examples/out/`） |
| `tests/` | pytest |
| `LICENSES-THIRD-PARTY.md` | 本目录用到的第三方程序、数据和文档的许可证 |

具体产品的 BOM 放在 `products/<产品名>/bom.csv`，不放在这里。

## 1. 快速使用

```bash
. .venv/bin/activate
python mfg/cost.py --check-prices                                   # 检查价格缓存
python mfg/cost.py products/<产品名>/bom.csv --qty 10 100 1000 --out products/<产品名>/cost
pytest mfg/tests
```

输出：`cost_<数量>.csv`（每档明细）、`summary.csv`（每档一行）、`cost.md`（汇总 + 明细，Markdown）。
退出码：0 正常；2 输入格式错误；3 有缺价格的行且加了 `--strict`。

常用参数：`--attrition 0.02`（默认损耗率）、`--currency USD --fx CNY=0.139`（混用币种时必须给汇率，汇率要写来源）、`--no-optimize-breaks`（不自动"多买到下一档更便宜"）、`--strict`。

## 2. BOM 格式（CSV，UTF-8）

第一行是列名（英文，便于程序读取），每行一个物料。必需列：`ref`、`name`、`qty_per_unit`、`category`。

| 列 | 中文 | 必需 | 说明 |
|---|---|---|---|
| `ref` | 位号 | 是 | `U1`、`R1,R2`、`C1-C6`；非电子件自己编，如 `ENC1`、`PKG1`、`SMT1` |
| `name` | 名称 | 是 | 人看的名字 |
| `mpn` | 厂商型号 | | 例 `ME6211C33M5G-N` |
| `manufacturer` | 厂商 | | |
| `package` | 封装 | | `0402`、`SOT-23-5`、`模块` |
| `qty_per_unit` | 每台用量 | 是 | 数字；单位跟着价格走：元件按个，3D 打印按克，人工按分钟 |
| `category` | 类别 | 是 | `electronic` 电子件 / `mechanical` 结构件 / `module` 外购模块 / `packaging` 包装 / `process` 加工费（中英文都可以） |
| `lcsc` | 立创编号 | | 例 `C82942`；`price_key` 为空时自动用 `lcsc:<编号>` 查价 |
| `price_key` | 价格来源键 | | 价格缓存里的 key，例 `jlcpcb:pcba-setup`、`est:oled-0.96-module` |
| `cost_mode` | 计费方式 | | `unit`（默认，每台用量 × 数量）/ `batch`（每批一次，用量与数量无关，如工程费、钢网、模具）/ `per_joint`（按焊点：本行用量 × 每台焊点数 × 数量）/ `per_extended_type`（按扩展料种数：本行用量 × 扩展料种数） |
| `attrition` | 损耗率 | | 覆盖默认损耗，`0.05` 或 `5%`。`process` 类别默认不计损耗 |
| `joints` | 焊点数 | | 每个器件的焊点数，覆盖价格缓存里的 joints，给 `per_joint` 行用 |
| `dnp` | 不贴 | | `y` 表示这一行不装、不计价 |
| `note` | 备注 | | |

五类物料的写法：

```csv
ref,name,mpn,manufacturer,package,qty_per_unit,category,lcsc,price_key,cost_mode,attrition,joints,dnp,note
U4,3.3V LDO,ME6211C33M5G-N,MICRONE,SOT-23-5,1,电子件,C82942,,unit,,,,
ENC1,外壳 MJF PA12（克）,,,,15,结构件,,jlc3dp:mjf-pa12-per-gram,unit,,,,按克计价
DS1,0.96 寸 OLED 模块,,,模块,1,外购模块,,est:oled-0.96-module,unit,,,,
PKG1,基础包装,,,,1,包装,,est:packaging-basic,unit,,,,
SMT1,贴片工程费,,,,1,加工费,,jlcpcb:pcba-setup,batch,,,,每批一次
SMT3,贴片焊点费,,,,1,加工费,,jlcpcb:smt-joint,per_joint,,,,
```

完整例子：`examples/generic-esp32s3-gadget.bom.csv`（通用示例，不对应具体产品；电池标了 DNP，因为型号因产品而异）。

## 3. 价格缓存格式（`prices/*.yaml`）

目录下所有 `.yaml` 一起读取，key 不能重复。每个文件是条目列表：

```yaml
- key: lcsc:C82942              # 必需，BOM 的 price_key 引用它；元件用 lcsc:<立创编号>
  mpn: ME6211C33M5G-N
  manufacturer: MICRONE Nanjing Micro One Elec
  package: SOT-23-5
  jlc_class: Extended           # Basic / Extended / Preferred，决定换料费
  joints: 5                     # 焊点数（可选）
  currency: USD                 # 必需
  unit: 个                      # 可选，说明计价单位（个、g、分钟、次/批）
  moq: 1                        # 最小起订量；不写则取第一档数量
  order_multiple: 1             # 包装倍数（可选，整盘时填盘数量）
  breaks:                       # 必需，阶梯价：qty 是该档起始数量
  - {qty: 1, price: 0.0617}
  - {qty: 100, price: 0.05}
  status: quote                 # 必需：quote 实查 / unverified 待核实 / estimate 估算
  level: B                      # 来源级别（research-method）
  access: mirror                # direct / mirror / search-snippet
  source_url: https://jlcpcb.com/partdetail/C82942   # quote、unverified 必需
  alt_url: https://www.lcsc.com/product-detail/C82942.html
  mirror: https://github.com/yaqwsx/jlcparts/tree/gh-pages @ 028c436（快照 2026-10-31）
  date: '2026-11-01'            # 必需，查询日期
  basis: ''                     # unverified、estimate 必需：依据和公式
  note: ''
```

`cost.py --check-prices` 和 pytest 会检查：status 合法、有 currency/breaks/date、实查和待核实有 source_url、待核实和估算有 basis、key 不重复。

当前文件：

| 文件 | 内容 |
|---|---|
| `prices/jlcpcb-parts.yaml` | 25 条元件阶梯价，JLCPCB 元件库数据（经 jlcparts 镜像，快照 2026-10-31），`quote` |
| `prices/unverified.yaml` | 2 条模组价，只有搜索摘要，`unverified` |
| `prices/fees.yaml` | 6 条 JLCPCB/JLC3DP 加工费，只有搜索摘要且有冲突，`unverified` |
| `prices/estimates.yaml` | 3 条估算（OLED 模块、组装人工、包装） |

## 4. 计算规则

对每个数量档 N、每一行：

1. 需求量：`unit` = 每台用量 × N × (1 + 损耗率)；`batch` = 每台用量；`per_joint` = 每台用量 × 每台焊点数 × N；`per_extended_type` = 每台用量 × 扩展料种数。
   - 每台焊点数 = 所有 `electronic`、`unit`、非 DNP 行的（焊点数 × 每台用量）之和；焊点数未知的行会出现在警告里。
   - 扩展料种数 = 上述行里 jlc_class 为 Extended 的不同价格条目数。
2. 采购量：需求量向上取整 → 不低于 MOQ → 按包装倍数取整 → 如果多买到下一档总价反而更低，就多买（可关）。
3. 单价：采购量落在哪一档就用哪一档；小计 = 采购量 × 单价（MOQ 和多买的部分全部算进成本，剩余量在明细的 `leftover` 列）。
4. 汇总：总价、单台价、一次性费用（`batch` 和 `per_extended_type`）、按类别小计，以及**实查 / 待核实 / 估算金额各占多少**。
5. 缺价格的行：不计入总价，明细里标"缺价格"，汇总里数出行数，并写警告；加 `--strict` 时退出码为 3。

## 5. 依赖和许可证

- Python：PyYAML（MIT）、pytest（MIT），见 `requirements.txt`。
- 外部程序：git；KiCad 8+ 的 `kicad-cli`（GPL，只作为外部命令调用，不复制代码、不随库分发），或 Docker 镜像 `kicad/kicad:9.0`。
- 数据：价格数据来自 JLCPCB 元件库，经 [yaqwsx/jlcparts](https://github.com/yaqwsx/jlcparts) 的公开导出读取；本库只存少量价格条目，不包含该项目的代码。
- 乐鑫硬件设计指南：只引用和摘要，不复制原文和图片。
