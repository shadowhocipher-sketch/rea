# c02 · C 固件模板 · 按键/触摸消抖：单击、双击、长按、毛刺

**需求**：桌面陪伴类产品一个按键 + 一个触摸区，要区分单击、双击、长按，并且不被抖动和毛刺误触发。

**任务**：用 firmware-sim skill，以 `firmware/templates/buttons.py`（默认 CONFIG：debounce 25 ms、long 700 ms、double 300 ms）
和本目录 `stimulus.json` 运行：
`python sim/run_firmware.py firmware/templates/buttons.py --inputs evals/tasks/c02_button_events/stimulus.json --seconds 9`
（模板没有屏幕，退出码 1、"no frames" 是正常的），读控制台 `EVENT` 行。

**判分**（标准答案按模板文档里的时序模型和激励时间手算）：
| 事件 | 手算时间 |
|---|---|
| button click | 1000+80 松开 +25 消抖 +300 双击等待 ≈ 1405 ms |
| button double | 第二次 3200+80 松开 +25 ≈ 3305 ms |
| button long | 5000 +25 +700 ≈ 5725 ms |
| button hold_end | 6200 +25 ≈ 6225 ms |
| touch click | 8150 +25 +300 ≈ 8475 ms |
7000 ms 的 10 ms 毛刺不应产生事件。顺序完全一致得 0.5；每个时间在 ±50 ms 内各得 0.1。
