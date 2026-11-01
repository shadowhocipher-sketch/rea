# inputs/（用户提供的案例材料）

2026-11-01 开始本次冲刺时，这个会话能访问的仓库里都**没有找到** `inputs/`。
查过的位置：`rea` 仓库的本地和远端分支、`main` 分支，以及账号下的 stack-chan、taster 等仓库。

案例应包含：桌面小生命（ESP32-S3 + SSD1306 0.96 寸 OLED）的 MicroPython 眼睛固件、引脚表、产品定位、采购清单。

本次用 `products/desk-creature-standin/` 里一份**替身**代替。替身是统筹为了验证模拟器和流程而从零写的，
不是用户的案例。真实材料放进这个目录以后，运行：

```bash
python sim/run_firmware.py inputs/<眼睛固件>.py --display ssd1306 --out products/desk-creature/sim_eyes.gif
```

就能用真实固件复验模拟器。
