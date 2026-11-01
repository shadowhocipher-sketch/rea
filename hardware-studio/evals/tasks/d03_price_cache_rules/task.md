# d03 · D 价格缓存 · 不合研究方法的价格条目必须被拒

**需求**：以后的会话会往 `mfg/prices/` 加价格。没有链接的"实查"、没有依据的"估算"、没有日期的条目、
自造的状态值都不能混进成本里，否则成本表的"实查占比"就失真。

**任务**：`python mfg/cost.py --check-prices --prices evals/tasks/d03_price_cache_rules/bad_prices.yaml`
应该失败并点名每个坏条目；对库里的 `mfg/prices/` 跑同一命令应该通过。

**判分**（标准答案按 research-method 和 mfg/README.md 第 3 节手工判定，见 `bad_prices.yaml` 注释）：
- 坏缓存：退出码 2（0.2）；四个坏 key 各被点名（各 0.15）；合格的 `e:ok` 没被点名（0.1）；
- 库里的 `mfg/prices/` 检查通过（0.1）。
