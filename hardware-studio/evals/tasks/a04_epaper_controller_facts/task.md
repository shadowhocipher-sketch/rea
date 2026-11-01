# a04 · A 知识库 · 墨水屏控制器（SSD1680 类）驱动要点

**需求**：墨水屏小设备要自己写或改驱动、决定 RES#/BUSY 接不接 MCU、深睡后怎么唤醒屏。

**任务**：用 component-knowledge skill 从 `knowledge/display/` 查出：
1. BUSY 引脚什么电平表示忙；
2. 控制器进入深睡后怎么退出（决定 RES# 是否必须接 GPIO）；
3. 进入深睡的命令字；
4. 触发刷新（Master Activation）的命令字；
每条带链接 + 级别 + 日期。

**判分**（标准答案取自 Solomon Systech SSD1680 数据手册的引脚说明和命令表，评分人独立整理）：
- BUSY 高电平 = 忙，带来源（0.3）；
- 退出深睡只能硬件复位（RES#），带来源（0.3）；
- 深睡命令 0x10，带来源（0.2）；
- Master Activation 命令 0x20，带来源（0.2）。
