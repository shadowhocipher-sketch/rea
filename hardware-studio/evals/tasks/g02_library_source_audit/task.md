# g02 · G 研究方法 · 全库事实记录的来源合规率

**需求**：research-method 要求写进库的每条参数、价格、法规都有链接、级别、日期（或标明 未查到 / 估算 / 待核实）。
这道题用一个**独立实现**的审计脚本（不调用库里的检查器）统计全库事实记录的合规率，防止回退。

**范围和规则**（按 research-method skill 第 3、4 节）：
- 事实页表格行：`knowledge/**/*.md`（README 除外）、`cad/DFM.md`、`mfg/esp32s3-min-system.md`。
  一行合规 = 同时有 http 链接、合法日期、`· S/A/B/C` 级别；或含"未查到 / 估算 / 待核实"。写"同上"而没有链接的行不合规。
- 价格缓存 `mfg/prices/*.yaml` 每条：status ∈ {quote, unverified, estimate}；有 date；quote/unverified 有 http 的 source_url；
  unverified/estimate 有 basis。
- 合规数据 `compliance/data/requirements.yaml` 每条：至少一个 http 来源且来源都写了 level；status ∈ {已核实, 待核实}；待核实写了 doubts。

**判分**：得分 = 合规记录数 / 记录总数。理由里列出不合规最多的文件。
