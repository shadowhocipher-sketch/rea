# 一日冲刺报告：小型电子产品通用能力库

日期：2026-11-01。分支：`claude/gracious-lovelace-yl954a`（`shadowhocipher-sketch/rea`），目录 `hardware-studio/`。

## 结论

- **八条线和迁移测试都完成了。** 全库测试 465 个通过、1 个跳过（跳过的那个需要 KiCad Docker 镜像，设置镜像后能通过）。
- **自测分**：基线 **15.51 / 20**，补缺口后 **18.72 / 20**。A、B、C、F、G 五条线满分；剩下的分都卡在网络拦截上：实查价格占比、法规待核实比例。
- **迁移测试**：一个全新的子代理只拿到总流程 skill 和一句产品描述，就做完了墨水屏"答案机"的 8 步交付物。它临时补的通用能力都已回写进库并配了测试。没达到的只有成本：1000 台 ¥115/台，比 ¥99 高 17%，而且这个数主要靠待核实的价格算出来。
- **需要你做的四件事**：
  1. 把真实的 `inputs/` 案例给我；
  2. 在环境设置里放行官方站点，之后回填"待核实"；
  3. 确认是否接受 OpenCASCADE（LGPL-2.1 附例外）这类动态依赖；
  4. 确认 ¥99 指的是成本还是零售价。

## 0. 先说三件影响全局的事

1. **用户的案例材料 `inputs/` 没有找到。** 查过 `rea` 的本地和远端分支、`main`，以及账号下的其他仓库，都没有。为了能验证模拟器和流程，统筹从零写了一份**替身**放在 `products/desk-creature-standin/`，并在文件里明确标注。真实材料放进 `inputs/` 以后，按 `inputs/README.md` 里的命令复验。
2. **网络策略拦截了几乎所有官方站点。** 包括原厂（乐鑫、ST、ADI、Microchip）、分销商（立创、LCSC、JLCPCB、DigiKey、Mouser）和法规站点（EUR-Lex、eCFR、legislation.gov.uk、CNCA、工信部、ACMA、FCC）。能用的只有 GitHub 和搜索。所以：
   - 乐鑫的资料改读官方 GitHub 上的硬件设计指南源文件（S 级）；
   - 其他厂家的数据手册经第三方 GitHub 镜像读取，标"S（镜像）· 待核实"；
   - 价格来自 jlcparts 的公开数据导出（JLCPCB 元件库阶梯价），以及搜索摘要；
   - 法规的"已核实"是指：官方页面在搜索结果里出现过，并且摘要内容和条目一致。
   
   放行这些域名以后，应该优先回填这些"待核实"项。
3. **这个能力库放在 `rea` 仓库里，只是因为本会话只挂了这一个仓库。** `hardware-studio/` 是自成一体的目录，可以整体搬到独立仓库。

## 1. 每条线交了什么、怎么验证的

各线都由一个子代理完成，统筹自己重新运行检查后才提交。子代理不能写报告文件，下面的内容由统筹根据它们交回的文字整理。

### A. 元器件与模块知识库 `knowledge/`

- **交付**：
  - 19 个器件页：ESP32-S3/C3/C6；SSD1306、ST7789、SSD1680/1681；ESP32 触摸、轻触按键、LIS3DH；无源/有源蜂鸣器、MAX98357A；USB-C 受电、TP4056、DW01+FS8205A、ME6211、XC6206；Wi-Fi/BLE 功耗、天线与共存。
  - 6 张选型表、README 索引、`check_sources.py`、skill `component-knowledge`。
- **验证**：
  - `check_sources.py` 检查了 25 个文件、515 行，0 行不合格；
  - pytest 9 个通过，包括"缺来源"的反例；
  - 随机抽 5 条参数，重新下载原文核对，全部一致。顺带发现 SSD1680 手册里 2Fh 寄存器的说明前后矛盾，已经写进页面。
- **没做成**：
  - 乐鑫数据手册独有的数值（射频电流、模组尺寸等）标"未查到"；
  - 非乐鑫器件全部"待核实"；
  - 价格只有搜索摘要，全部"待核实"；
  - MCP73831、RT9080/AP2112 没做。

### B. 结构与外壳 `cad/`

- **交付**：
  - `hwcad` 包：外壳主体、止口、自攻柱和热熔螺母柱、屏幕窗、按键孔和悬臂按键、USB-C 开孔、卡扣（含应变估算）、电池仓、四种工艺的常量；
  - 工具：测量（含干涉矩阵和壁厚抽样）、导出、预览、切片检查；
  - 入口 `build_enclosure.py <yaml>`；`DFM.md`；skill `enclosure-design`。
- **验证**：
  - pytest 37 个通过；
  - 示例外壳实际生成：干涉为 0，USB 插头能插到底，能放上打印平台；
  - PrusaSlicer 2.7.2 已用 apt 装上，三个零件都能切片，并给出耗材和时间估算。
- **没做成**：
  - DFM 的数值只来自官方页面的搜索摘要；
  - USB-IF 插头外壳尺寸、MJF 原版手册、卡扣许用应变都没查到；
  - 只支持垂直于 Z 轴的分模面。

### C. 固件模式库与显示模拟器 `firmware/`、`sim/`

- **交付**：
  - 模拟器在电脑上运行 MicroPython 固件，不用改代码，使用虚拟时钟；
  - 覆盖 machine、time、framebuf（7 种格式、全部绘图方法）、esp32、ssd1306、st7789、墨水屏（SSD1680/1681，记录全刷/局刷次数，能模拟残影）；
  - 输出的 PNG/GIF 都标"模拟"；
  - 四个固件模板：状态机、按键和触摸消抖、低功耗、开机自检；skill `firmware-sim`。
- **验证**：
  - pytest 60 个通过；
  - 替身眼睛固件生成 `sim_eyes.gif`，统筹复跑了一次：6 秒虚拟时间用了 0.7 秒；
  - 彩色 LCD 和墨水屏的示例都出了图，目视检查正确。
- **没做成**：
  - 不支持 asyncio，用到时会明确报"不支持"；
  - 模板只在模拟器里跑过，没有上真机；
  - 墨水屏刷新时间待核实；
  - 用户的真实固件缺失。

### D. 从原型到量产 `mfg/`

- **交付**：
  - BOM 格式，分五类物料、四种计费方式；
  - `cost.py`：阶梯价、最小起订量、损耗、一次性费用，统计"实查 / 待核实 / 估算"各占的金额比例；
  - 价格缓存 36 条：实查 25、待核实 8、估算 3；
  - 查价流程 `pricing.md`、`jlcparts_import.py`、量产路线决策表、ESP32-S3 最小系统要点；
  - `kicad_check.py`（KiCad 9 官方 Docker 镜像）；skill `bom-cost`。
- **验证**：
  - pytest 26 个通过、1 个跳过（需要 KiCad 镜像），设置镜像后 27 个全部通过；
  - 示例 BOM 跑出 100 台和 1000 台两档成本；
  - KiCad ERC/DRC 在最小工程和 KiCad 自带的演示工程上都实际运行过。
- **没做成**：
  - 没有一条价格是直接打开商品页核对的；
  - 示例 BOM 里实查金额只占约 12%，因为模组、外壳和贴片费都还是待核实；
  - KiCad 的"错误级违规返回 1"只在单元测试里用模拟报告验证过。

### E. 合规地图 `compliance/`

- **交付**：
  - 52 条要求，覆盖 CN / EU / US / UK / AU；
  - 唯一数据源是 `requirements.yaml`，`map.md` 由它生成；
  - `checklist.py` 输入产品特征，输出要查的清单；skill `compliance-map`。
- **验证**：
  - pytest 186 个通过；
  - 四个典型产品的清单都实际生成；
  - `build_map.py --check` 确认 `map.md` 和数据源一致。
- **没做成**：
  - 待核实 23 条，其中中国 9 条里有 8 条，最大疑点是 SRRC 和微功率设备的边界；
  - 法规原文一条都没能直接读到。

### F. 出图 `render/`、`diagrams/`

- **交付**：
  - 自写的 numpy 渲染器：软阴影、studio 和桌面两种场景、书和铅笔做尺寸参照、爆炸图；文件名以 `render_` 开头，图上标"渲染图 / Render"；
  - 接线图生成器：从 `pins.csv` 生成 SVG/PNG，并逐根核对；skill `product-render`。
- **验证**：
  - pytest 69 个通过；
  - 测试模型和 B 的示例外壳都渲染了多角度图和桌面图，统筹看过；
  - 接线核对：替身 4/4 根，复杂示例 24/24 根；删掉一根线时核对失败，说明检查有效。
- **没做成**：透明材质、贴图和丝印。

### G. 研究方法

- **交付**：skill `research-method`，由统筹写（它是 A、D、E 的前提）。内容：来源四级、交叉核实、引用格式，以及"未查到 / 估算 / 待核实 / 未运行"四种标记的用法。
- **验证**：A、D、E 都按它执行；`knowledge/check_sources.py` 和 `mfg/cost.py --check-prices` 会自动检查格式。

### H. 新产品流程与自测

- **交付**：
  - 审核了 7 个 skill，每个都实际运行过示例命令。修了 3 处：bom-cost 的 KiCad 命令改成以 Docker 为主；component-knowledge 的工作目录统一；firmware-sim 写明 `buttons.py` 模板没有屏幕，不要加 `--out`。
  - skill 索引 `.claude/skills/README.md`；
  - 总流程 skill `new-product`（8 步，每步写清调用哪个 skill、哪条命令、产出放哪、怎么验收、常见坑），配套 `product.py`（`new` / `compliance-yaml` / `check`）和模板 `products/_template/`；
  - `evals/`：20 道题，每道都有题面和判分脚本，由 `run.py` 汇总，`--compare` 对比基线。
- **验证**：
  - `evals/tests` 共 29 个测试，证明判分能区分对错：每道题的错误答案都得 0 分，用标准答案构造的正确答案得 1 分，判分脚本崩溃时记 0 分；
  - 标准答案都是手算或按资料独立整理的，不由被测工具生成。
- **统筹做过的一处更正**：c03（asyncio）原标准答案写 5 帧。micropython-lib 的 `ssd1306.py`（提交 660ddd8，第 77 行）在构造时会 `show()` 一次，正确答案应为 6 帧。已在题面和判分脚本里改正并注明依据。

## 2. 自测分

`python evals/run.py --compare evals/results/baseline-2026-11-01.json`，结果在 `evals/results/`：

| 题 | 线 | 考什么 | 基线 | 最终 |
|---|---|---|---:|---:|
| a01 | A | ESP32-S3 strapping 引脚，带来源 | 0.85 | 1.00 |
| a02 | A | 锂电随身设备的充电与保护方案 | 1.00 | 1.00 |
| a03 | A | 缺口：MCP73831 与电量计器件页 | 0.00 | 1.00 |
| a04 | A | 墨水屏控制器 BUSY、深睡、命令字 | 1.00 | 1.00 |
| b01 | B | USB-C + 电池仓外壳：干涉 0、插头插到底 | 1.00 | 1.00 |
| b02 | B | 干涉检查报对碰撞的零件和体积 | 1.00 | 1.00 |
| c01 | C | 墨水屏固件的刷新次数和节奏 | 1.00 | 1.00 |
| c02 | C | 按键/触摸消抖的事件时序 | 1.00 | 1.00 |
| c03 | C | 缺口：模拟器支持 uasyncio | 0.00 | 1.00 |
| c04 | C | 缺口：加速度计摇一摇模板 | 0.00 | 1.00 |
| d01 | D | 100/1000 台成本与手算核对 | 1.00 | 1.00 |
| d02 | D | 缺口：成本中实查价格占比 ≥ 50% | 0.24 | 0.24 |
| d03 | D | 价格缓存来源规则校验 | 1.00 | 1.00 |
| e01 | E | Wi-Fi 桌面摆件合规清单的必含/不得含 | 1.00 | 1.00 |
| e02 | E | BLE 纽扣电池玩具合规清单的必含/不得含 | 1.00 | 1.00 |
| e03 | E | 缺口：法规待核实比例 ≤ 20% | 0.45 | 0.47 |
| f01 | F | 接线图与 pins.csv 一一对应 | 1.00 | 1.00 |
| f02 | F | 渲染图的标注、命名、尺寸 | 1.00 | 1.00 |
| g01 | G | 来源检查器抓出缺来源的行 | 1.00 | 1.00 |
| g02 | G | 全库事实记录来源合规率 | 0.96 | 1.00 |
| **合计** | | | **15.51** | **18.72** |

说明：
- 能力题在基线时大多已经满分，偏回归性质。"变强"主要体现在 5 道缺口题和 a01、g02 上。
- d02 和 e03 只有放行官方站点、能直接核对商品页和法规原文后才能提高。

## 3. 迁移测试

**做法**：新开一个子代理，只给它总流程 skill 的路径和一句产品描述（口袋墨水屏、摇一摇显示答案、锂电池、充电口、不联网、¥99 以内），不告诉它各条线的细节。完整报告在 `products/answer-box/REPORT.md`。

**交出的东西**：

| 交付物 | 结果 |
|---|---|
| 选型 | ESP32-C3-MINI-1 模组（射频不开）、1.54 寸 200×200 墨水屏（SSD1681）、LIS3DH（INT1 接能唤醒深睡的 GPIO3）、TP4056 充电（130 mA）、带保护板的约 200 mAh 电芯、XC6206 稳压（静态电流 1 μA）、USB-C 只取 5 V |
| 显示模拟图 | `sim/sim_main.gif`、`.png`：摇一摇换答案，闲置后深睡，INT1 唤醒。全刷 3 次、局刷 6 次、共 7560 ms，与手算一致 |
| 外壳模型和渲染图 | 58×42×16.6 mm，MJF；干涉 0，USB 插头能插到底；5 张 `render_*.png` |
| 两档 BOM 与成本 | 100 台 ¥120.33/台，1000 台 ¥115.43/台，比 ¥99 高 17–22%；实查金额只占约 23% |
| 合规清单 | 按"无无线、锂电池、只卖中国"生成。补缺口后 5 条：CN-03/05/07，加上锂电池运输的 CN-10/11 |
| 产品检查 | `product.py check answer-box` 28 项通过 27 项，没过的就是单台 ≤ ¥99 |

**哪些直接复用、哪些临时补、是否回写**：

| 步骤 | 直接复用 | 临时补的 | 回写进库了吗 |
|---|---|---|---|
| 1 简报 | 模板、`product.py` | 无 | 不需要 |
| 2 选型 | C3、SSD1681、LIS3DH、TP4056、XC6206、USB-C 的器件页和选型表 | LIS3DH 寄存器位、1.54 寸屏外形、电池尺寸 | 寄存器位和屏外形已回写到 `knowledge/`；电池尺寸只有 C 级来源，留在产品目录 |
| 3 原型 | `diagrams/wiring.py`（一次通过） | **摇一摇固件模板** | 已回写：`firmware/templates/shake.py` + 7 个测试 |
| 4 模拟 | 模拟器、墨水屏模拟、深睡唤醒 | 修了模拟器的一个 bug：深睡重启后刷新计数被清零 | 已回写：修复 + 回归测试 |
| 5 外壳 | 外壳模块全部复用，只调了 2 次参数 | MJF 外壳克数是用体积手算的 | 库代码没改 |
| 6 成本 | `cost.py`、已有价格 | 屏模块价（待核实）、电池价（估算）、汇率（待核实） | 两条价格已进价格缓存；汇率只写在产品报告里 |
| 7 合规 | `checklist.py` | 比较了"射频在但不开"算不算无线 | 发现缺锂电池运输条目，补缺口阶段已回写（见下） |
| 8 出图 | 渲染器 | 屏幕替身 STL | 只对本产品有用，没回写 |

**迁移测试暴露的缺口，后续怎么处理的**：

| 缺口 | 处理 |
|---|---|
| 没有摇一摇模板 | 迁移测试中已回写（c04 0 → 1） |
| 墨水屏只有模拟器接口，没有真机驱动 | 补了 `firmware/drivers/ssd168x.py`，API 和模拟器一致，用"录下命令序列"的假 SPI 对照数据手册测试过；**未上真机** |
| 合规库缺锂电池运输条目 | 补了 CN-10、CN-11、EU-15、UK-12、AU-09，有电池时自动触发；answer-box 的清单已重新生成 |
| `product.py check <名字>` 不认产品名 | 已修复，加了测试 |
| 中文点阵字库 | **没补**：需要许可证明确的 CJK 点阵字体，体积也大，超出本次范围 |
| 不带射频的低价 MCU | **没补**：知识库只有 ESP32 系列；不联网的产品用 C3 偏贵 |
| 成本超 ¥99 | **没解决**：最贵两项（屏模块 ¥38、MJF 外壳 ¥26）都是待核实价；改用裸屏、注塑或无射频 MCU 都需要先核实数据 |

## 4. 补缺口（用剩余额度，只补没过的自测题和迁移缺口）

- **模拟器**：支持 asyncio/uasyncio（虚拟时钟）；没出帧时给出清楚提示，不再抛异常；新增墨水屏真机驱动 `firmware/drivers/ssd168x.py`。
- **知识库**：新增 MCP73831、MAX17048（电量计）器件页。ESP32-S3 的 GPIO3 作用在 esp-idf 官方文档里找到了：它是 JTAG 信号源选择，只在烧了 eFuse 时起作用；同时发现 esp-idf 的 eFuse 表说明与文档冲突，已写进页面。
- **来源**：`mfg/esp32s3-min-system.md`、`cad/DFM.md` 里写"同上"的行全部补成完整来源。g02 现在 806/806 合规。
- **合规**：新增 5 条锂电池运输条目。
- **工具小修**：外壳报告在没有 USB 口时显示"不适用"；`product.py check` 能用产品名。

## 5. 没做成的和原因

- **用户案例 `inputs/`**：本会话里找不到，只用替身验证了。
- **网络**：官方站点被拦截，所以：
  - 实查价格占比只有约 12%（通用示例）到 23%（答案机）；
  - 法规 57 条里有 24 条待核实；
  - 非乐鑫器件的数据手册全部经镜像读取、标待核实。
- **没有真机**：固件模板、墨水屏驱动、摇一摇检测都只在模拟器里运行过。
- **外壳**：只支持垂直于 Z 轴的分模面；没有脱模斜度造型；卡扣许用应变缺少可靠来源。
- **渲染**：没有透明、贴图和丝印。
- **自测覆盖不均**：A、C 各 4 道，B、F、G 各 2 道；外壳题没覆盖切片、卡扣应变和壁厚；没有 KiCad 题，因为跑一次 Docker 要几十秒。
- **"连续修 3 次不过"的情况**：没有发生。D 线有一个问题没查清：想在 KiCad 9 里人为制造短路，DRC 却没报错。已经改用警告来测试失败路径，"有错误级违规时返回 1"只在单元测试里验证过。
- **子代理不能写报告文件**：系统规定子代理只能用文字交回结果。所以各条线没有单独的 `plans/report-*.md`，内容由统筹整理进本文件。

## 6. 许可证

见 [LICENSES-THIRD-PARTY.md](LICENSES-THIRD-PARTY.md)。要点：
- 没有复制任何 GPL/LGPL/AGPL 代码；
- KiCad、PrusaSlicer、git 只作为外部命令调用；
- 不用 Blender bpy；
- build123d 依赖的 OpenCASCADE 内核是 LGPL-2.1 附例外，通过动态调用使用，**需要你确认是否接受**；
- GxEPD2（GPL-3.0）只引用了两个数值作线索，没有复制代码。

## 7. 在本地怎么用

**第一步：取得代码和环境**

```bash
git clone https://github.com/shadowhocipher-sketch/rea.git
cd rea
git checkout claude/gracious-lovelace-yl954a
cd hardware-studio
python -m venv .venv
.venv\Scripts\activate            # Windows；macOS/Linux 用 . .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q               # 应为 465 passed, 1 skipped
python evals/run.py               # 自测打分
```

**第二步：让 Claude Code 读到这些 skill**（二选一）

- **推荐**：直接在 `hardware-studio/` 目录里启动 Claude Code。项目级 skill（`hardware-studio/.claude/skills/`）会自动加载，不用拷贝。
- **想在任何目录都能用**：把下面 8 个文件夹拷到本机的 `%USERPROFILE%\.claude\skills\`（macOS/Linux 是 `~/.claude/skills/`）：

  ```
  hardware-studio\.claude\skills\new-product\           ← 总流程（含 product.py）
  hardware-studio\.claude\skills\research-method\
  hardware-studio\.claude\skills\component-knowledge\
  hardware-studio\.claude\skills\enclosure-design\
  hardware-studio\.claude\skills\firmware-sim\
  hardware-studio\.claude\skills\bom-cost\
  hardware-studio\.claude\skills\compliance-map\
  hardware-studio\.claude\skills\product-render\
  ```

  注意：skill 里的命令都按"当前目录是 `hardware-studio/`"来写，工具和知识也在这个目录里。所以拷到用户目录后，运行时仍要先 `cd` 到你本机的 `hardware-studio/`。

**第三步：开始一个新产品**

在 Claude Code 里说："按 new-product skill 做一个新产品：<一句话描述>"。或者手动执行：

```bash
python .claude/skills/new-product/product.py new <产品名>
python .claude/skills/new-product/product.py check <产品名>
```

**外部工具**（可选，没有时工具会给出提示，不会崩溃）：
- 切片检查：PrusaSlicer 命令行；
- KiCad 检查：KiCad 9 的 `kicad-cli`，或 Docker 镜像 `kicad/kicad:9.0`（`--docker kicad/kicad:9.0`）；
- 图上的中文标注：Windows 会找微软雅黑或黑体，Linux 找 Noto Sans CJK。**在 Windows 上没有运行验证过。**

**真实案例到位以后**：把材料放进 `hardware-studio/inputs/`，按 `inputs/README.md` 的命令复验模拟器。
