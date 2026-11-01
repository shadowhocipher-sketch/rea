---
name: firmware-sim
description: 在电脑上不改代码运行 MicroPython 显示固件（SSD1306 OLED、ST7789 彩屏、SSD1680/SSD1681 墨水屏，含 asyncio/uasyncio 多任务固件），用虚拟时钟出 PNG/GIF 模拟图；使用 firmware/templates 里的状态机、按键/触摸消抖、摇一摇（加速度计）、低功耗休眠、开机自检模板，以及与模拟器同 API 的 SSD1680/SSD1681 真机墨水屏驱动 firmware/drivers/ssd168x.py。Use when previewing what MicroPython firmware shows on a small display, checking firmware logic (timing, buttons, shake/accelerometer, sleep/wake, self-test, asyncio tasks) without hardware, producing sim_*.png/gif screen mockups for a product, starting new MicroPython firmware from a template, or moving e-paper firmware from the simulator to a real board.
---

# 固件模拟与模板

## 什么时候用

- 有一份 MicroPython 固件（`inputs/` 里用户给的，或新写的），想看屏幕上会显示什么、动画节奏对不对；
- 新产品流程里"屏幕和交互模拟"这一步：出 `sim_*.gif` / `sim_*.png`；
- 写新固件时从 `firmware/templates/` 起步（状态机、按键/触摸、摇一摇、休眠、自检）；
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
python sim/run_firmware.py evals/tasks/c03_gap_uasyncio/fw_async.py --display ssd1306 --seconds 8 --out /tmp/sim_async.png
python sim/run_firmware.py firmware/examples/epaper_hello.py --display epaper --seconds 120 --out /tmp/sim_hello.png
```

- 给了 `--out` 但固件没出帧时：不写图片，打印 `error: 未生成图片：<原因>`（没调 show/刷新、只刷了别的屏、出帧前就异常），退出码 1，没有回溯。

模板：`firmware/templates/*.py`，改开头的 `CONFIG` 或在设备上放 `config.json`。

| 模板 | 演示命令 | 预期 |
|---|---|---|
| `state_machine.py` | `python sim/run_firmware.py firmware/templates/state_machine.py --seconds 20 --out /tmp/sim_fsm.png` | 退出码 0，SSD1306 出帧 |
| `power.py` | `python sim/run_firmware.py firmware/templates/power.py --seconds 20 --out /tmp/sim_power.png` | 退出码 0 |
| `selftest.py` | `python sim/run_firmware.py firmware/templates/selftest.py --seconds 10 --out /tmp/sim_selftest.png` | 退出码 0；没给 ADC 输入时警告"ADC pin 1 has no stimulus"，电池项显示 0 V |
| `shake.py` | `python sim/run_firmware.py firmware/templates/shake.py --inputs evals/tasks/c04_gap_shake_template/stimulus.json --seconds 5 --out /tmp/sim_shake.png` | 退出码 0，打印 `SELFTEST accel OK addr=0x18`；在 stimulus 的 `pins` 里给 INT1 脚（默认 3）脉冲，每个上升沿打印 `EVENT shake n`（800 ms 冷却内的脉冲被忽略） |
| `buttons.py` | `python sim/run_firmware.py firmware/templates/buttons.py --inputs btn.json --seconds 6` | **没有屏幕**，只在控制台打印 `EVENT button click/double/long/hold_end`；因为没帧，退出码是 1，这是正常的。加了 `--out` 会提示"未生成图片"，同样退出码 1 |

`btn.json` 例子（单击、长按各一次）：`{"buttons": [{"pin": 0, "at_ms": 1000, "hold_ms": 80, "active_level": 0, "bounce_ms": 4}, {"pin": 0, "at_ms": 3000, "hold_ms": 1500, "active_level": 0, "bounce_ms": 4}]}`

## 支持哪些 API

`time/utime`（虚拟时钟）、`random`（可设种子）、`framebuf`（7 种格式、全部绘图方法，像素与
MicroPython 源码算法一致，字形除外）、`machine`（Pin/IRQ、I2C/SoftI2C、SPI、PWM、ADC、TouchPad、
Timer、WDT、RTC、UART、light/deepsleep、reset、reset_cause、wake_reason…）、`esp32`（唤醒源、NVS）、
`micropython`、`gc`、`network`（存根）、`asyncio`/`uasyncio`（虚拟时钟：run、create_task、current_task、sleep、
sleep_ms、wait_for/wait_for_ms、gather、Task.cancel/done、Event、ThreadSafeFlag、Lock、get_event_loop/new_event_loop、
Loop.run_forever/stop/异常处理器）、`ssd1306`（micropython-lib API）、`st7789`/`st7789py`
（st7789py_mpy API + `ST7789_FB` framebuf 写法）、`epaper`/`ssd1680`/`ssd1681`/`ssd168x`（与真机驱动
`firmware/drivers/ssd168x.py` 同一套 API）。
完整清单和每项的偏差说明见 `sim/README.md`"支持的 API"。

## 不支持的会怎样

访问未实现的属性 → `SimUnsupported`（AttributeError），摘要里列出 `unsupported`；
`bluetooth`、`urequests`、`neopixel`、`dht` 等能 import、一用就报同样的错；asyncio 的 TCP 流（`open_connection`、`start_server`）也一样。
遇到时：先看是否能在固件外层用配置绕开；需要的话在 `sim/mpsim/` 里补模拟并加测试，不要改用户固件。

## asyncio 固件要注意

- 调度在虚拟时钟上：`await asyncio.sleep_ms(250)` 立刻推进 250 ms；`--seconds`/`--frames` 照常停止。
- 行为按 MicroPython：`sleep` 毫秒精度；`run()` 主任务结束就返回；没人 await 的任务异常打印 "Task exception wasn't retrieved"；
  `wait_for` 超时先取消内层任务再抛 `TimeoutError`；IRQ/Timer 回调里只用 `ThreadSafeFlag.set()`（`Event.set()` 会被警告）。
- 所有任务都在等、又没有 IRQ/Timer 能唤醒时：警告 "would wait forever" 并跑完时钟（真机会卡死）。
- 调度本身不耗虚拟时间：只靠 `await sleep(0)` 空转、不读 ticks 的任务只会被真实时间上限打断。

## 墨水屏：从模拟器到真机

- `firmware/drivers/ssd168x.py` 是 SSD1680/SSD1681 的 MicroPython 驱动（全刷、局刷、深睡、BUSY 超时），**API 与模拟器一致**：
  固件写 `import ssd168x`（或 `import epaper`），模拟器里得到模拟模型，板子上拷驱动文件（拷成 `ssd168x.py` 或 `epaper.py`）。
- 文件头写明**未在真机运行**：命令序列只和数据手册流程比对过（`firmware/tests/test_fw_ssd168x.py`）；RAM 方向、rotation 方向、
  局刷波形（Display Mode 2）、刷新时间要上板核实。报告里照这个写。
- 两边一致的规则：没接 RST 时 `sleep()` 抛 ValueError；深睡后再刷新自动重新 init；开机/重启后第一次刷新用全刷（模拟器对"第一次就局刷"给警告）。
- 用法和命令字说明见 `firmware/README.md`"驱动"。

## 怎么检查结果

1. 摘要里 `stop_reason` 应为 `frame_limit`/`time_limit`/`finished`/`sleep_forever`；
   `exception` 时看 `firmware raised`；`frames` > 0，`frame_size` 与面板一致。
2. 用 Read 工具打开 PNG 拼图（`--png-mode sheet`）逐帧看内容；GIF 抽帧看。
   墨水屏看摘要里的 `epaper` 行（如 `{'ssd1680#0': {'full': 2, 'partial': 5, 'refresh_ms': 7500}}`），
   或 `--log x.json` 后读 `summary.stats.epaper`：刷新次数和自己按固件逻辑手算的一致，才算节奏对。
3. 看 `warnings`（浮空引脚、未配置的 ADC/触摸、三色屏局刷、裸 except 吞掉停止信号等）。
4. 报告里写清：模拟图标"模拟"、哪些是模型/估算（ADC 线性、刷新时间、字体、随机数）、未在真机验证。
5. 改了 `sim/`、模板或驱动就跑 `python -m pytest sim/tests firmware/tests -q`。

## 已知坑

- 固件目录里自带 `ssd1306.py` 也会被模拟驱动替代（只有模拟驱动能出帧）。
- `blit_buffer` 按面板大端解释：framebuf RGB565（小端）直接推会颜色错乱——真机一样。
- `ssd1306.rotate(False)` 是旋转 180°（与 micropython-lib 驱动一致）。
- 墨水屏 API 不是 MicroPython 标准：库里的真机驱动 `firmware/drivers/ssd168x.py` 与它同 API；用户用别的驱动且方法名不同时，写一个薄适配层，或只看逻辑不出帧。
- `ssd1306` 构造时会 `show()` 一次空白屏（与 micropython-lib 一致），所以帧数 = 固件里的 show 次数 + 1。
