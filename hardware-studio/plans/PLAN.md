# 八条工作线计划

日期：2026-11-01。统筹：主会话。每条线交给一个子代理并行做，G 是 A/D/E 的前提，由统筹先完成。
所有线共同遵守 [CONVENTIONS.md](../CONVENTIONS.md)。

依赖顺序：

```
G（统筹先做）─┬→ A 知识库 ─────┐
              ├→ D 量产 ───────┤
              └→ E 合规 ───────┤
B 外壳 ──→ F 出图（先用自带测试模型，B 完成后渲染 B 的模型）
C 固件与模拟器 ────────────────┤
                               └→ H 总流程 + 20 道自测 + 基线分 ─→ 迁移测试（新会话按总流程做墨水屏产品）
```

---

## A. 元器件与模块知识库 `knowledge/`

**交付物**
- 每类一个目录：`mcu/` `display/` `input/` `audio/` `power/` `wireless/`；
- 每个器件一页（统一模板：概述、引脚、电压、电流、接口时序要点、易踩的坑、来源）；
- 每类一张 `selection.md` 选型表：场景 → 推荐 → 价格区间（带来源或标"估算"）→ 取舍；
- `knowledge/README.md` 索引；`knowledge/check_sources.py` 来源检查脚本；
- `.claude/skills/component-knowledge/SKILL.md`。

**覆盖范围（优先级从高到低）**：ESP32-S3、C3、C6；SSD1306、ST7789、SSD1680/SSD1681 类墨水屏；
ESP32 自带电容触摸、轻触按键、LIS3DH 类加速度计；无源/有源蜂鸣器、MAX98357A；
USB-C 受电 CC 电阻、TP4056/MCP73831 类充电芯片、DW01A 类保护、低静态电流 LDO；Wi-Fi/BLE 天线与共存。

**检查方法**：`check_sources.py` 扫描所有表格行，每条事实都要有链接、级别、日期；随机抽 5 条，打开链接核对。

**停止条件**：六类都有至少 2 个器件页和 1 张选型表，来源检查全部通过。

## B. 结构与外壳 `cad/`

**交付物**
- `cad/hwcad/` Python 包：固定柱、屏幕窗、按键孔、USB-C 开孔、卡扣、电池仓、外壳主体（壁厚、公差参数化）；
- 工具：预览渲染、测量（尺寸、体积、最小壁厚抽样、干涉）、导出 STL/STEP、切片检查（装得上切片命令行就做）；
- `cad/DFM.md`：FDM、光固化、MJF、注塑各自的规则和批量切换点（带来源）；
- `cad/tests/` pytest；`.claude/skills/enclosure-design/SKILL.md`。

**检查方法**：pytest 全部通过；用模块拼出一个示例外壳，导出、测量、预览都实际生成文件。

**停止条件**：七类模块都有测试；示例外壳能导出并通过干涉检查。

## C. 固件模式库与显示模拟器 `firmware/`、`sim/`

**交付物**
- `sim/`：在电脑上模拟 MicroPython 的 `machine`、`time`、`framebuf`、`ssd1306`，以及彩色 LCD 和墨水屏驱动；
  同一份固件不改代码即可运行，输出 PNG/GIF（文件名 `sim_` 开头，图上标"模拟"）；
- `sim/run_firmware.py` 命令行入口；
- `firmware/templates/`：状态机、按键和触摸消抖、低功耗与休眠、开机自检；每个模板写清验证状态；
- pytest；`.claude/skills/firmware-sim/SKILL.md`。

**检查方法**：用替身眼睛固件生成 GIF；三种屏幕各有一个示例生成图片；pytest 通过。

**停止条件**：三种屏幕都能出图；四个模板都能在模拟器里跑通（真机验证状态如实标注）。

## D. 从原型到量产 `mfg/`

**交付物**
- BOM 结构（CSV 列定义）和 `mfg/cost.py`：输入数量档位，输出单价和总价；
- 价格查询固定流程和价格缓存（每条价格带链接、日期；查不到标"估算"并写依据）；
- `mfg/production-routes.md`：开发板 / 模组加小板 / 自画整板的决策表；
- `mfg/esp32s3-min-system.md`：最小系统要点，附乐鑫官方参考设计链接；
- KiCad 命令行装得上就加 ERC/DRC 检查脚本，装不上写明原因；
- pytest；`.claude/skills/bom-cost/SKILL.md`。

**检查方法**：pytest；用示例 BOM 跑出两档数量的成本表；价格行全部有来源或"估算"标记。

**停止条件**：成本工具能处理任意 BOM，至少一份真实查价的价格缓存。

## E. 合规地图 `compliance/`

**交付物**
- `compliance/map.md`：按产品特征（无线、电池、电源适配器、儿童用）× 市场（中国 3C/SRRC 等，CE、FCC、UKCA、RCM）列出要求，每条附官方链接；
- `compliance/checklist.py`：输入产品特征，输出该查的清单；
- pytest；`.claude/skills/compliance-map/SKILL.md`。

**检查方法**：每条要求都有官方链接或"待核实"；checklist 对四种典型产品输出的结果合理。

**停止条件**：四个特征 × 五个市场都填写或标明待核实；只整理资料，不下法律结论。

## F. 出图 `render/`、`diagrams/`

**交付物**
- `render/`：从 STEP/STL 渲染多角度图和桌面场景图（不用 bpy，见 CONVENTIONS 第 5 条）；文件名 `render_` 开头，图上标"渲染图"；
- `diagrams/`：从 `pins.csv` 自动生成接线图（SVG + PNG）；
- pytest；`.claude/skills/product-render/SKILL.md`。

**检查方法**：用自带测试模型和 B 的示例外壳实际出图并目视检查；接线图和 pins.csv 的连线一一对应（脚本核对）。

**停止条件**：多角度图、场景图、接线图都实际生成。

## G. 研究方法（统筹已完成）

**交付物**：`.claude/skills/research-method/SKILL.md`。来源分级、交叉核实、引用格式、四种标记、网络受限时的做法、检查清单。

**检查方法**：A/D/E 按它执行；H 的自测里有一道题检查来源格式。

## H. 新产品流程与自测 `.claude/skills/`、`evals/`

**交付物**
- 审核各线的 SKILL.md（什么时候用、怎么用、怎么检查结果）；
- `.claude/skills/new-product/SKILL.md` 总流程：场景和感受 → 选型 → 开发板原型 → 屏幕和交互模拟 → 外壳 → BOM 与成本 → 合规 → 小批量；
- `evals/`：20 道题覆盖 A–G，每道一个判分脚本，`evals/run.py` 汇总；跑一次，记录基线分。

**检查方法**：`python evals/run.py` 能跑完并输出分数；每道题的判分脚本能区分对和错（做一次反例测试）。

**停止条件**：20 道题都能自动判分，基线分已记录。

## 迁移测试

由一个新开的子代理只拿"总流程 skill + 第二产品描述"去做墨水屏答案机，
交出选型、显示模拟图、外壳模型和渲染图、两档数量的 BOM 与成本、合规清单。
统筹记录哪些步骤直接复用、哪些临时补了、补的是否回写进能力库。
