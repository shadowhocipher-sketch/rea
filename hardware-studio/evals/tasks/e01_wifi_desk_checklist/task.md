# e01 · E 合规 · Wi-Fi 联网桌面摆件（无电池、不带适配器、成人用）的合规清单

**需求**：一个 USB 线供电、连家里 Wi-Fi 的桌面小摆件，卖欧盟、美国、英国，包装里不带充电器，不是玩具。

**任务**：`python compliance/checklist.py --product evals/tasks/e01_wifi_desk_checklist/product.yaml --out <dir>/checklist.md`

**判分**：标准答案由评分人按法规知识独立列出（按法规编号匹配清单条目的标题和"依据"行）。

必须包含：RED 2014/53/EU；RED 网络安全授权法规 (EU) 2022/30；RoHS 2011/65/EU；WEEE 2012/19/EU；GPSR (EU) 2023/988；
FCC Part 15 Subpart C（有意辐射体）；英国 Radio Equipment Regulations 2017；英国 PSTI。

不得包含：单独的 EMC 指令 2014/30/EU 和英国 EMC Regulations 2016（无线设备的 EMC 由 RED / RER 覆盖）；
LVD 2014/35/EU（不带市电适配器，RED 已含安全要求）；电池法规 (EU) 2023/1542；玩具安全（2009/48/EC、Toys (Safety) Regulations）；
Reese's Law 16 CFR 1263。

得分 = （命中的必须项 + 没误含的禁止项）/ 总项数。
