# f01 · F 接线图 · 从 pins.csv 出图并核对每根线不多不少

**需求**：开发板原型阶段要一张接线图给人照着接线；图必须和 `pins.csv` 完全一致，核对工具要能发现漏画和多画。

**任务**：`python diagrams/wiring.py evals/tasks/f01_wiring_check/pins.csv --out <dir> --name f01`，
再用 `python diagrams/check_wiring.py pins.csv <dir>/wiring_f01.svg` 核对。

**判分**：
- `wiring.py` 退出码 0（0.2）；
- 评分脚本**自己**解析 SVG 里的 `<polyline class="wire">`（不调用 diagrams 的核对代码），
  与评分脚本自己读的 pins.csv 按（两端、net、kind）做多重集比较，15 根线完全一致（0.4）；
- 从 SVG 删掉一根线后，`check_wiring.py` 退出码 1 且报 MISSING（0.2）；
- 复制一根线（多画）后，退出码 1 且报 EXTRA（0.2）。
