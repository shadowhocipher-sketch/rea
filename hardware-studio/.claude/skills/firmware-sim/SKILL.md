---
name: firmware-sim
description: 在电脑上不改代码运行 MicroPython 显示固件（SSD1306 OLED、ST7789 彩屏、SSD1680/SSD1681 墨水屏），用虚拟时钟出 PNG/GIF 模拟图，并使用 firmware/templates 里的状态机、按键/触摸消抖、低功耗休眠、开机自检模板。Use when previewing what MicroPython firmware shows on a small display, checking firmware logic (timing, buttons, sleep/wake, self-test) without hardware, producing sim_*.png/gif screen mockups for a product, or starting new MicroPython firmware from a template.
---

# 固件模拟与模板

## 什么时候用

- 有一份 MicroPython 固件（`inputs/` 里用户给的，或新写的），想看屏幕上会显示什么、动画节奏对不对；
- 新产品流程里"屏幕和交互模拟"这一步：出 `sim_*.gif` / `sim_*.png`；
- 写新固件时从 `firmware/templates/` 起步（状态机、按键/触摸、休眠、自检）；
- 不用于：证明真机能跑、测功耗、测真实刷新时间。这些要上真机。

## 怎么跑

```bash
cd hardware-studio && . .venv/bin/activate
python sim/run_firmware.py <固件.py> --display ssd1306|st7789|epaper \
    [--width W --height H] [--frames N] [--seconds S] [--seed K] \
    [--inputs stimulus.json] --out products/<产品>/sim_<名字>.gif [--out ...png]
```

- 停止条件：`--frames` 或 `--seconds`（虚拟时间）；都不给默认 10 s。
- 有按键/触摸/ADC/I2C 传感器的固件要给 `--inputs`（格式见 `sim/README.md`"外部输入"）。
  只有 SSD1306 时默认 0x3C 应答；其他 I2C 设备要写进 `i2c_devices`。
- 墨水屏时间长：`--seconds` 给够（全刷 2–3 s/次），GIF 用 `--speed 10` 之类加速。
- 输出放 `products/<产品名>/`，文件名必须 `sim_` 开头（工具会自动补）。
- Python 里：`from run_firmware import run_firmware` 或 `from mpsim import run, session`。

可直接复制运行的例子（2026-11-01 实测，每条几秒）：

```bash
python sim/run_firmware.py products/desk-creature-standin/eyes.py --display ssd1306 --seconds 12 --seed 1 --out /tmp/sim_eyes.gif
python sim/run_firmware.py sim/examples/epaper_card.py --display epaper --seconds 400 --speed 10 --out /tmp/sim_card.gif --log /tmp/card.json
python sim/run_firmware.py sim/examples/lcd_dashboard.py --display st7789 --seconds 5 --out /tmp/sim_lcd.png
```

模板：`firmware/templates/*.py`，改开头的 `CONFIG` 或在设备上放 `config.json`。

| 模板 | 演示命令 | 预期 |
|---|---|---|
| `state_machine.py` | `python sim/run_firmware.py firmware/templates/state_machine.py --seconds 20 --out /tmp/sim_fsm.png` | 退出码 0，SSD1306 出帧 |
| `power.py` | `python sim/run_firmware.py firmware/templates/power.py --seconds 20 --out /tmp/sim_power.png` | 退出码 0 |
| `selftest.py` | `python sim/run_firmware.py firmware/templates/selftest.py --seconds 10 --out /tmp/sim_selftest.png` | 退出码 0；没给 ADC 输入时警告"ADC pin 1 has no stimulus"，电池项显示 0 V |
| `buttons.py` | `python sim/run_firmware.py firmware/templates/buttons.py --inputs btn.json --seconds 6` | **没有屏幕**，只在控制台打印 `EVENT button click/double/long/hold_end`；因为没帧，退出码是 1，这是正常的。**不要加 `--out`**，否则会抛 `ValueError: no frames captured` 的回溯 |

`btn.json` 例子（单击、长按各一次）：`{"buttons": [{"pin": 0, "at_ms": 1000, "hold_ms": 80, "active_level": 0, "bounce_ms": 4}, {"pin": 0, "at_ms": 3000, "hold_ms": 1500, "active_level": 0, "bounce_ms": 4}]}`

## 支持哪些 API

`time/utime`（虚拟时钟）、`random`（可设种子）、`framebuf`（7 种格式、全部绘图方法，像素与
MicroPython 源码算法一致，字形除外）、`machine`（Pin/IRQ、I2C/SoftI2C、SPI、PWM、ADC、TouchPad、
Timer、WDT、RTC、UART、light/deepsleep、reset、reset_cause、wake_reason…）、`esp32`（唤醒源、NVS）、
`micropython`、`gc`、`network`（存根）、`ssd1306`（micropython-lib API）、`st7789`/`st7789py`
（st7789py_mpy API + `ST7789_FB` framebuf 写法）、`epaper`/`ssd1680`/`ssd1681`（模拟器自定义 API）。
完整清单和每项的偏差说明见 `sim/README.md`"支持的 API"。

## 不支持的会怎样

访问未实现的属性 → `SimUnsupported`（AttributeError），摘要里列出 `unsupported`；
`asyncio`/`uasyncio`、`bluetooth`、`urequests`、`neopixel`、`dht` 等能 import、一用就报同样的错（所以用 uasyncio 写的固件目前不能模拟，`evals/` 的 c04 题在跟踪这个缺口）。
遇到时：先看是否能在固件外层用配置绕开；需要的话在 `sim/mpsim/` 里补模拟并加测试，不要改用户固件。

## 怎么检查结果

1. 摘要里 `stop_reason` 应为 `frame_limit`/`time_limit`/`finished`/`sleep_forever`；
   `exception` 时看 `firmware raised`；`frames` > 0，`frame_size` 与面板一致。
2. 用 Read 工具打开 PNG 拼图（`--png-mode sheet`）逐帧看内容；GIF 抽帧看。
   墨水屏看摘要里的 `epaper` 行（如 `{'ssd1680#0': {'full': 2, 'partial': 5, 'refresh_ms': 7500}}`），
   或 `--log x.json` 后读 `summary.stats.epaper`：刷新次数和自己按固件逻辑手算的一致，才算节奏对。
3. 看 `warnings`（浮空引脚、未配置的 ADC/触摸、三色屏局刷、裸 except 吞掉停止信号等）。
4. 报告里写清：模拟图标"模拟"、哪些是模型/估算（ADC 线性、刷新时间、字体、随机数）、未在真机验证。
5. 改了 `sim/` 或模板就跑 `python -m pytest sim/tests firmware/tests -q`。

## 已知坑

- 固件目录里自带 `ssd1306.py` 也会被模拟驱动替代（只有模拟驱动能出帧）。
- `blit_buffer` 按面板大端解释：framebuf RGB565（小端）直接推会颜色错乱——真机一样。
- `ssd1306.rotate(False)` 是旋转 180°（与 micropython-lib 驱动一致）。
- 墨水屏 API 不是标准：用户真实驱动不同名时，写一个薄适配层，或只看逻辑不出帧。
