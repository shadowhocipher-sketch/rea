# e02 · E 合规 · 带 BLE 和纽扣电池的儿童玩具的合规清单

**需求**：一个 CR2032 纽扣电池供电、用 BLE 连手机（不上网）的儿童玩具，卖美国、欧盟、澳洲。

**任务**：`python compliance/checklist.py --product evals/tasks/e02_coin_cell_toy_checklist/product.yaml --out <dir>/checklist.md`

**判分**：标准答案由评分人按法规知识独立列出。

必须包含：Reese's Law 16 CFR part 1263；CPSIA / ASTM F963；欧盟玩具安全 2009/48/EC（或新法规 2025/2509）；
欧盟电池法规 (EU) 2023/1542；RED 2014/53/EU；RED 网络安全授权法规 (EU) 2022/30（对无线玩具适用，不论是否联网）；
FCC Part 15 Subpart C；澳洲纽扣/硬币电池强制安全标准。

不得包含：通用充电器 (EU) 2022/2380（不可充电）；LVD 2014/35/EU（无适配器）；美国 DOE 外部电源能效 10 CFR 430.32(w)；
单独的 EMC 指令 2014/30/EU；FCC Cyber Trust Mark（不联网）。

得分 = （命中的必须项 + 没误含的禁止项）/ 总项数。
