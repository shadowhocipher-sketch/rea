# c03 · C 模拟器 · 【缺口探测】模拟器能不能跑 uasyncio 固件

**需求**：稍复杂的产品固件（动画 + 按键 + 联网）通常用 `uasyncio` 写多任务。模拟器跑不了就无法预览这类固件。

**任务**：`python sim/run_firmware.py evals/tasks/c03_gap_uasyncio/fw_async.py --display ssd1306 --seconds 8 --out <dir>/sim_async.png`

**判分**（手算）：计数任务在 t = 0、1、2、3、4 s 各重画一次 → 5 帧；t = 5 s 结束并打印 `count 5 blinks N`，
闪灯任务每 250 ms 一次，t = 0…5000 ms 共 20 或 21 次（t = 5000 ms 两个任务同时到点，顺序不定）。
- 退出码 0 且 `stop_reason = finished`（0.4）；控制台有 `count 5`（0.3）；blinks 在 20–21（0.1）；帧数 5（0.2）。

这是缺口题：2026-11-01 基线时模拟器把 `uasyncio` 列为"可 import、一用就报 SimUnsupported"，得 0 分是预期的。
