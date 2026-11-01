# Skill 索引

所有命令在 `hardware-studio/` 下、`. .venv/bin/activate` 之后运行。新产品从 `new-product` 开始，它按顺序调用其余 skill。

| Skill | 用途 | 入口命令 |
|---|---|---|
| [new-product](new-product/SKILL.md) | 总流程：想法 → 选型 → 原型 → 模拟 → 外壳 → 成本 → 合规 → 小批量，交付清单和 REPORT 写法 | `python .claude/skills/new-product/product.py new <产品名>`；`... check products/<产品名>` |
| [research-method](research-method/SKILL.md) | 查参数、价格、法规时的来源分级、引用格式、未查到/估算/待核实标记 | `python knowledge/check_sources.py <文件>`（事实页来源检查） |
| [component-knowledge](component-knowledge/SKILL.md) | 元器件知识库：查器件页和选型表、按模板补新器件页（A 线 `knowledge/`） | `grep -rn "<关键词>" knowledge/`；`python knowledge/check_sources.py` |
| [firmware-sim](firmware-sim/SKILL.md) | 不改代码在电脑上跑 MicroPython 显示固件（SSD1306/ST7789/墨水屏）出模拟图；固件模板（C 线 `sim/`、`firmware/`） | `python sim/run_firmware.py <固件.py> --display ssd1306\|st7789\|epaper --seconds 20 --out <dir>/sim_x.gif` |
| [enclosure-design](enclosure-design/SKILL.md) | 参数化外壳：由内而外放元器件包络，生成 STEP/STL，查干涉、壁厚、USB 插到底、切片（B 线 `cad/`） | `python cad/build_enclosure.py products/<产品名>/enclosure.yaml --out products/<产品名>/cad_out` |
| [bom-cost](bom-cost/SKILL.md) | BOM 格式、查价入缓存、多数量档成本、量产路线、KiCad ERC/DRC（D 线 `mfg/`） | `python mfg/cost.py products/<产品名>/bom.csv --qty 100 1000 --out products/<产品名>/cost` |
| [compliance-map](compliance-map/SKILL.md) | 按产品特征列 CN/EU/US/UK/AU 合规条目和证据形式（E 线 `compliance/`，资料整理不是法律意见） | `python compliance/checklist.py --product products/<产品名>/compliance.yaml --out products/<产品名>/compliance_checklist.md` |
| [product-render](product-render/SKILL.md) | 产品渲染图（多角度、爆炸、桌面场景，标"渲染图 / Render"）和由 pins.csv 自动画并核对的接线图（F 线 `render/`、`diagrams/`） | `python render/render.py --part <零件.stl>:#颜色:材质 --views front,iso --out <dir>`；`python diagrams/wiring.py products/<产品名>/pins.csv --out products/<产品名>/out` |

## 能力自测

`evals/` 有 20 道题（覆盖 A–G 各线，其中 5 道是"缺口探测"），量这个库有没有变强：

```bash
python evals/run.py --label <名字>                                   # 写 evals/results/<名字>.json / .md
python evals/run.py --compare evals/results/baseline-2026-11-01.json # 和基线比
python -m pytest evals/tests -q                                      # 判分脚本能区分对错
```

改进某条线之后重跑，看对应题的分数变化；新加题放 `evals/tasks/<编号>_<名字>/`（`task.md` + `grade.py` 的 `META/produce/score`），
标准答案必须独立得出，不能由被测工具生成，并在 `evals/tests/test_eval_graders.py` 里加一个"错误答案得 0 分"的反例。
