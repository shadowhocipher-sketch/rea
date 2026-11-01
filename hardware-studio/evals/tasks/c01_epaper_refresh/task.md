# c01 · C 模拟器 · 墨水屏固件的刷新次数和节奏

**需求**：墨水屏产品每分钟局刷一次、每 5 次全刷一次去残影。上真机前要在模拟器里确认刷新次数和总时长，
估算功耗和屏幕寿命都靠它。

**任务**：用 firmware-sim skill 运行本目录 `fw_epaper_counter.py`：
`python sim/run_firmware.py evals/tasks/c01_epaper_refresh/fw_epaper_counter.py --display epaper --seconds 700 --out <dir>/sim_counter.png --log <dir>/log.json`，
从摘要读刷新次数、虚拟时间、帧数。

**判分**（标准答案按固件逻辑手算）：开机全刷 1 次 + n=5、10 全刷 → 全刷 3 次、局刷 8 次；
刷新耗时 3×2500 + 8×400 = 10 700 ms；虚拟时间 10×60 s + 10.7 s = 610.7 s；每次刷新出 1 帧 → 11 帧；面板 200×200。
- 正常结束（`finished`）、退出码 0、控制台有 `done 10`（0.2）；全刷 = 3（0.2）；局刷 = 8（0.2）；
- 刷新总时长 10 700 ms（0.1）；虚拟时间 610.7 s ±0.1 s（0.1）；帧数 11 且 200×200（0.2）。
