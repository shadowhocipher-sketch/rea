# b02 · B 外壳 · 干涉检查能不能抓到真实的碰撞

**需求**：选型改了模块尺寸后，元器件包络可能互相重叠或扎进底板。外壳检查必须报出来，而且体积要对，
否则"干涉为 0"的结论不可信。

**任务**：用 `cad/build_enclosure.py` 生成本目录的 `enclosure.yaml`（三个模块包络 + 一个扎进底板的模块），
读 `check_report.json` 的 `interference`。

**判分**（标准答案由盒子坐标手算，见 `enclosure.yaml` 注释）：
- 退出码 1 且 `ok = false`（0.2）；
- 报出 module_a × module_b，体积 400 mm³（±2%）（0.3）；
- 报出 bottom × module_d，体积 100 mm³（±2%）（0.3）；
- 只接触的 module_a × module_c 不算干涉；不多报其他对；总量 500 mm³（0.2）。
