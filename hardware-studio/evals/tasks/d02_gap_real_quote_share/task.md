# d02 · D 成本 · 【缺口探测】成本里有多少是真实查价

**需求**：给客户或自己做决策的成本数字，至少一半金额要来自真实查到的阶梯价（B 级来源，`status: quote`），
否则只能叫"估算"。

**任务**：用库里的价格缓存，对通用示例 BOM 算成本：
`python mfg/cost.py mfg/examples/generic-esp32s3-gadget.bom.csv --qty 100 1000 --out <dir>`，看 `summary.csv` 的 `quote_share`。
提高的办法：能打开分销商页面时按 `mfg/pricing.md` 把 `unverified`/`estimate` 条目复查成 `quote`；或在 jlcparts 镜像里找到同型号。

**判分**：目标是 100 台和 1000 台两档的实查占比都 ≥ 50%。每档得分 = min(1, 实查占比 / 0.5)，取两档平均。
例如实查 12.5% → 0.25。

这是缺口题：2026-11-01 基线时实查只占约 12%（大头是待核实的模组价和估算的 OLED 模块），不满分是预期的。
