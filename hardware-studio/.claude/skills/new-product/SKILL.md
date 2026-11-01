---
name: new-product
description: 新产品从想法到小批量的总流程：场景和感受 → 选型 → 开发板原型 → 屏幕和交互模拟 → 外壳 → BOM 与成本 → 合规 → 小批量与出图，每步调用哪个 skill、跑哪条命令、产出放 products/<产品名>/ 哪里、怎么验收。Use when starting any new small electronic product idea in hardware-studio (desk companion, e-paper gadget, battery-powered pocket device, 3D-printed export part), when asked to take an idea to a prototype / small batch, or when checking whether a product folder has all deliverables and writing its REPORT.
---

# 新产品：从想法到小批量

这是总流程。每一步都调用一个专门的 skill；这里只写**顺序、命令、产出位置、验收和常见坑**。
所有命令在 `hardware-studio/` 下运行，先 `. .venv/bin/activate`。事实、价格、法规一律按 research-method skill 写来源。

## 什么时候用

- 有了一个新产品想法（桌面陪伴、墨水屏小设备、带电池的随身小物、外贸 3D 打印结构件……），要走到原型或小批量；
- 已有 `products/<产品名>/`，想知道还缺哪些交付物、哪一步没通过；
- 产品做完要写 REPORT，并把临时补的东西回写进库。

不适用：只查一个器件参数（直接用 component-knowledge）、只算一次成本（bom-cost）——单步需求直接用对应 skill。

## 0. 开始

```bash
cd hardware-studio && . .venv/bin/activate
python .claude/skills/new-product/product.py new <产品名>        # 复制 products/_template → products/<产品名>
python .claude/skills/new-product/product.py check products/<产品名>            # 随时看八步交付物齐不齐
python .claude/skills/new-product/product.py check products/<产品名> --step 1 2  # 只查某几步
```

`product.py check` 每项输出 `[OK]` / `[FAIL]`，退出码 0 = 所查步骤全部通过。它会重跑便宜的检查（接线核对、价格缓存、知识库来源），
重的结果（外壳、成本）读工具已经写出的报告，所以改了参数要先重跑对应工具。
产品名用小写字母、数字、连字符。产品数据只放 `products/<产品名>/`，不要改通用模块（CONVENTIONS 第 2 条）。

产品目录最终长这样：

```
products/<产品名>/
  brief.yaml                 1 场景与简报
  selection.md               2 选型结论 + 元器件包络
  pins.csv  firmware/  out/wiring_<产品名>.svg|png          3 原型
  sim/sim_*.gif|png  (firmware/stimulus.json)               4 模拟
  enclosure.yaml  cad_out/                                  5 外壳
  bom.csv  cost/                                            6 成本
  compliance.yaml  compliance_checklist.md                  7 合规
  render/render_*.png  (kicad/ kicad-report/)               8 小批量与出图
  REPORT.md                                                 交付报告
```

---

## 1. 场景和感受 → `brief.yaml`

- **调用**：不需要别的 skill。填 `products/<产品名>/brief.yaml`（模板 `products/_template/brief.yaml`，每个字段有注释）。
- **输入**：用户的想法、目标市场、价格。
- **写什么**：谁用、在哪、什么时候、多久充一次电；想要的感受（≤3 个词）；怎么互动；明确不做什么；
  市场 `market.regions`（CN/EU/US/UK/AU）；目标单台成本和至少两档数量；`features`（无线、联网、电池、适配器、儿童）。
- **验收**：`python .claude/skills/new-product/product.py check products/<产品名> --step 1` 全 OK
  （没有 TODO、场景五项都填、单台成本目标 > 0 且 ≥2 档数量、features 能通过 `compliance/checklist.py` 的取值校验）。
- **常见坑**：
  - 感受写成功能（"有屏幕"不是感受，"安静地陪着"才是）；感受决定后面屏幕类型、刷新节奏、声音、材质的取舍。
  - `connected` 拿不准：只用 BLE 连手机但数据经 App 上云的，按联网算（compliance-map skill"特征怎么判断"）。
  - "儿童用"要写年龄段：欧盟/英国玩具 <14 岁、美国 CPSIA ≤12 岁、澳洲小零件 ≤36 个月。
  - 价格目标没写，第 6 步就没法判断要不要换料。

## 2. 选型 → `selection.md`

- **调用**：component-knowledge（查器件页和各类 `selection.md`）+ research-method（补资料时的来源规则）。
- **输入**：`brief.yaml` 的 `hardware_intent`、`features`、价格目标。
- **做法**：
  1. 按功能块（主控、屏、输入、声音、电源/电池、无线）各看 `knowledge/<类>/selection.md` 的"场景 → 推荐 → 价格区间 → 取舍"；
  2. 点进器件页核对引脚、电压、电流、易踩的坑；把结论写进 `selection.md` 的表（每行指向一个 `knowledge/...md` 页）；
  3. 库里没有的器件：按 component-knowledge 的"新增一个器件页"补到 `knowledge/<类>/`，补完跑来源检查；
  4. 列**元器件包络**（PCB/开发板、屏幕模组、电池、按键、USB-C 插座……的外形尺寸 + 来源/实测/估算），第 5 步直接用。
- **验收**：`product.py check ... --step 2`（无 TODO、引用的知识库页都存在、`python knowledge/check_sources.py` 全库通过）。
  新补的页再单独跑 `python knowledge/check_sources.py knowledge/<类>/<页>.md`，并随机打开 2–3 个链接核对数值，写进 REPORT。
- **常见坑**：
  - 模组参数和芯片参数混用（ST7789 芯片电流不含背光；开发板引脚因卖家而异）。
  - 选了 strapping 引脚接按键/LED（ESP32-S3：GPIO0/3/45/46；C3：GPIO2/8/9），见各 MCU 页。
  - 深睡产品用了静态电流 60 μA 的 LDO；带 Wi-Fi 又用了只有 200 mA 的 LDO（见 `knowledge/power/selection.md`）。
  - 价格只当量级：知识库里的价格多数"待核实"，第 6 步以 `mfg/prices/` 为准。
  - 缺页时不要凭记忆补参数；查不到写"未查到"并说明查过哪里。

## 3. 开发板原型 → `pins.csv`、`firmware/`、接线图

- **调用**：firmware-sim（模板）+ product-render（接线图部分）+ component-knowledge（引脚限制）。
- **输入**：第 2 步选型；开发板/模块的引脚图。
- **做法**：
  1. 写 `pins.csv`（每行一根线，格式见 CONVENTIONS 第 2 节；`kind` = power/ground/signal）；
  2. 从模板起固件：`cp firmware/templates/state_machine.py products/<产品名>/firmware/main.py`
     （按键用 `buttons.py`，摇一摇/加速度计用 `shake.py`，休眠用 `power.py`，开机自检用 `selftest.py`），只改开头的 `CONFIG`，引脚和 `pins.csv` 一致；
  3. 出接线图：`python diagrams/wiring.py products/<产品名>/pins.csv --out products/<产品名>/out`
     （替身/未确认的引脚加 `--subtitle "替身数据 / stand-in data"`）。
- **验收**：`wiring.py` 输出 `OK: every wire drawn exactly once`、退出码 0；`product.py check ... --step 3` 全 OK；
  用 Read 打开 `out/wiring_<产品名>.png` 看一遍。
- **常见坑**：同一引脚写成两个 net 会被拒（按报错改）；I2C 共用总线要每个器件各写一行；
  pins.csv 里出现的零件在 BOM 里都要有行；GPIO 是否支持深睡唤醒（RTC GPIO）要查 MCU 页。

## 4. 屏幕和交互模拟 → `sim/sim_*.gif|png`

- **调用**：firmware-sim。
- **命令**：

  ```bash
  python sim/run_firmware.py products/<产品名>/firmware/main.py --display ssd1306|st7789|epaper \
      --seconds 20 --seed 1 [--inputs products/<产品名>/firmware/stimulus.json] \
      --out products/<产品名>/sim/sim_main.gif --out products/<产品名>/sim/sim_main.png --log products/<产品名>/sim/log.json
  ```
  墨水屏 `--seconds` 要给够（全刷 2–3 s/次），GIF 加 `--speed 10`。有按键/触摸/ADC/传感器的写 `stimulus.json`（格式见 `sim/README.md`）。
- **验收**：退出码 0；摘要 `stop_reason` 是 `frame_limit/time_limit/finished/sleep_forever`；`frames > 0`、`frame_size` 等于面板；
  墨水屏的刷新次数（摘要 `epaper` 行）和你按固件逻辑手算的一致；Read 打开 PNG 拼图逐帧看；`product.py check ... --step 4`。
- **常见坑**：模拟器不支持 `uasyncio`、`bluetooth`、`neopixel` 等（一用就 `SimUnsupported`）——把逻辑和外设隔开，模拟时用配置绕过；
  没有屏幕的固件不要加 `--out`；模拟图不能当实拍、不能证明真机能跑（时序、功耗、刷新时间都是模型），报告里写"模拟"。

## 5. 外壳 → `enclosure.yaml`、`cad_out/`

- **调用**：enclosure-design。元器件包络来自第 2 步 `selection.md`。
- **命令**：

  ```bash
  cp cad/examples/generic_box.yaml products/<产品名>/enclosure.yaml      # 起点，按 cad/README.md 改
  python cad/build_enclosure.py products/<产品名>/enclosure.yaml --out products/<产品名>/cad_out --no-slice --no-preview   # 反复改时
  python cad/build_enclosure.py products/<产品名>/enclosure.yaml --out products/<产品名>/cad_out                           # 定稿（含切片）
  ```
- **验收**：退出码 0；`cad_out/check_report.json` 里 `ok = true`（几何有效、干涉 0、USB 插头插到底、能放上打印平台、参数警告 0）；
  切片每个零件 `ok`，记下耗材克数（给第 6 步 `ENC1`）；Read 看 `preview_*.png`；`product.py check ... --step 5`。
- **常见坑**：
  - 层叠高度算错（底板内表面 = 壁厚 → 电池膨胀后 → 支柱 → PCB → 器件 → 屏 → 顶板内表面），先在纸上列 Z 再写 YAML；
  - 分模面 `split_z` 取 USB-C 插座中心高度；FDM 止口要求壁厚 ≥ 2.7 mm；
  - USB-C 插座/插头外壳尺寸、电池膨胀 10% 是估算默认值，换成数据手册或实测值；
  - 干涉报出来先挪位置，确实允许接触的才写 `ignore_pairs` 并写理由；
  - 首件打样后按实测改配合间隙。

## 6. BOM 与成本 → `bom.csv`、`cost/`

- **调用**：bom-cost（+ research-method 查价）。
- **做法**：按 `mfg/README.md` 第 2 节写 `bom.csv`（模板已带 PCB、贴片、钢网、焊点、换料、外壳、人工、包装行）；
  缺价格的按 `mfg/pricing.md` 查并写进 `mfg/prices/`（通用价格缓存，回写给以后用）。
- **命令**：

  ```bash
  python mfg/cost.py --check-prices
  python mfg/cost.py products/<产品名>/bom.csv --qty 100 1000 --out products/<产品名>/cost      # 数量档取 brief.yaml 的 quantities
  ```
- **验收**：至少两档；`summary.csv` 的 `missing_lines` 全为 0（或在 REPORT 列出缺什么）；最大数量档单台 ≤ brief 的目标，否则回第 2 步换料或在 REPORT 写原因；
  看 `quote_share`（实查占比），低于 50% 时结论必须写"估算"并列出金额最大的待核实/估算项；`product.py check ... --step 6`。
- **常见坑**：漏写加工费和包装（最常见的低估）；混币种不给 `--fx`；外壳克数和组装分钟数留 0；电池写了 DNP 却忘了单独算；
  价格结论不带日期。

## 7. 合规 → `compliance.yaml`、`compliance_checklist.md`

- **调用**：compliance-map。
- **命令**：

  ```bash
  python .claude/skills/new-product/product.py compliance-yaml products/<产品名>      # 从 brief.yaml 的 features/market 生成
  python compliance/checklist.py --product products/<产品名>/compliance.yaml --out products/<产品名>/compliance_checklist.md
  ```
- **验收**：退出码 0；清单条目和产品特征对得上（没电池却出现电池法规、有无线却出现单独的 EMC 指令 → 特征写错了）；
  `compliance.yaml` 与 `brief.yaml` 一致（`product.py check ... --step 7`）；"待核实"条目列进 REPORT 要问检测机构的问题。
- **常见坑**：这是资料整理不是法律意见；联网拿不准时 `connected` 真假各跑一次对比；用已认证模组也不等于整机免测（SRRC、FCC 模组授权条件、RED 整机评估都要问）。

## 8. 小批量 → 量产路线、DFM、KiCad 检查、渲染图

- **调用**：bom-cost（`mfg/production-routes.md`、`mfg/esp32s3-min-system.md`、`kicad_check.py`）、enclosure-design（`cad/DFM.md`）、product-render。
- **做法与命令**：
  1. 路线：按 `mfg/production-routes.md` 决策表在"开发板直接装 / 模组加底板 / 芯片整板"里选，必要时各写一份 BOM 用 `cost.py` 同数量档比较；
  2. 外壳工艺：按 `cad/DFM.md` 第 10 节的批量切换点选 FDM/光固化/MJF/注塑，改 `process` 重跑第 5 步；
  3. 自画板子时：KiCad 工程放 `products/<产品名>/kicad/`，
     `python mfg/kicad_check.py products/<产品名>/kicad/ --docker kicad/kicad:9.0 --out products/<产品名>/kicad-report`
     （本机有 KiCad 8+ 可去掉 `--docker`；ESP32-S3 板对照 `mfg/esp32s3-min-system.md` 自检清单）；
  4. 渲染图：
     ```bash
     python render/render.py --part products/<产品名>/cad_out/bottom.stl:#C9A27C:matte \
       --part products/<产品名>/cad_out/top.stl:#EFE9DF:satin:0,0,25 \
       --views front,iso --exploded --exploded-views iso --out products/<产品名>/render --name <产品名>
     python render/render.py ...同上... --scene desk --props book,pencil --views iso
     ```
     先 `--quality draft --size 800x600` 看效果，再出 1600×1200 正式图。
- **验收**：`kicad_check.py` 退出码 0（有 kicad/ 时）；渲染图文件名 `render_` 开头、Read 打开看到右下角"渲染图 / Render"、零件位置和爆炸方向对；
  `product.py check ... --step 8`。
- **常见坑**：渲染图不能裁掉标注、不能写"实拍"；只有 KiCad 7 时 `kicad_check.py` 返回 4，用 `--docker`；
  零件文件必须是装配坐标（`cad_out/` 导出的就是）；路线结论依赖待核实价格时要明说。

---

## 交付清单

`python .claude/skills/new-product/product.py check products/<产品名>` 全部 OK，即：

| # | 交付物 | 位置 | 检查 |
|---|---|---|---|
| 1 | 简报 | `brief.yaml` | 无 TODO、场景五项、目标成本、≥2 档、features 合法 |
| 2 | 选型 + 元器件包络 | `selection.md`（+ 新补的 `knowledge/` 页） | 引用页存在、`check_sources.py` 通过 |
| 3 | 接线表、固件、接线图 | `pins.csv`、`firmware/`、`out/wiring_*` | `wiring.py` 退出码 0 |
| 4 | 模拟图 | `sim/sim_*.gif/png` | 有图；刷新/事件与手算一致（人工） |
| 5 | 外壳模型 + 检查报告 | `enclosure.yaml`、`cad_out/` | `check_report.json` 的 `ok = true` |
| 6 | BOM + 两档成本 | `bom.csv`、`cost/` | ≥2 档、缺价格 0、单台 ≤ 目标 |
| 7 | 合规清单 | `compliance.yaml`、`compliance_checklist.md` | 与 brief 一致 |
| 8 | 渲染图（+ KiCad 报告） | `render/render_*.png`（`kicad-report/`） | 有图（有 kicad/ 时有报告） |
| 9 | 报告 | `REPORT.md` | 结论、交付清单、复用表 8 行、待核实 |

## 怎么写 REPORT（`products/<产品名>/REPORT.md`，模板已给好标题）

1. **结论**：做到哪一步、单台多少（哪个数量档、实查占比多少、日期）、外壳和模拟是否通过、最大的风险。
2. **交付清单**：上表每一项的实际文件路径；没做的写原因。
3. **复用 / 临时补 / 回写**（每步一行，共 8 行）：
   - *直接复用*：用了哪个 skill、工具、模板、知识库页、价格条目，没改就能用；
   - *临时补*：这次为产品临时写的东西（新器件页、新价格条目、固件绕过、工具参数、手工步骤）；
   - *是否回写*：补的东西如果对以后的产品也有用，**必须回写进库**并写明位置——器件页回 `knowledge/<类>/`、价格回 `mfg/prices/`、
     法规回 `compliance/data/requirements.yaml`、通用固件模式回 `firmware/templates/`、模拟器缺的 API 回 `sim/mpsim/`、外壳新模块回 `cad/hwcad/`；
     只对本产品有意义的留在 `products/<产品名>/`。没回写的写原因（例如"只查到 C 级来源，先放产品目录"）。
     改了别的线的代码要跑那条线的 pytest。
4. **待核实和风险**：所有"待核实/估算/未运行"的项（价格、法规、真机未验证的固件、估算的包络尺寸），以及准备问供应商/检测机构的问题。
5. **下一步**：真机验证、打样、报价。
6. 回写之后跑 `python evals/run.py --compare evals/results/<上次结果>.json`，把总分变化写进 REPORT（例如补了 MCP73831 页后 a03 应上升）。

报告里区分"实际运行过的"和"只是推理的"；数字都带来源和日期；模拟图、渲染图注明不是实拍。
