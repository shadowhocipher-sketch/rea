# sim/ — MicroPython 固件桌面模拟器（mpsim）

在电脑上**不改代码**运行 MicroPython 风格的显示固件：在 `sys.modules` 里注入模拟的
`machine`、`time`、`framebuf`、`ssd1306` 等模块，用虚拟时钟跑完 `while True`，
把屏幕每一帧存下来，输出 PNG / GIF（文件名 `sim_` 开头，图角标"模拟 / Simulated"）。

> 模拟图不是实拍，也不能证明固件在真机上能跑：时序、ADC、触摸数值、电流、
> 刷新时间都是模型或估算。真机验证另做。

## 快速开始

```bash
cd hardware-studio && . .venv/bin/activate
python sim/run_firmware.py products/desk-creature-standin/eyes.py \
    --display ssd1306 --seconds 12 --seed 1 \
    --out products/desk-creature-standin/sim_eyes.gif
```

| 参数 | 含义 |
|---|---|
| `--display ssd1306\|st7789\|epaper` | 输出哪类屏幕的帧（不写则取第一个出帧的屏） |
| `--width --height` | 期望的面板尺寸；与固件实际尺寸不一致时给警告 |
| `--frames N` / `--seconds S` | 停止条件：帧数 / **虚拟**时间上限（都不写默认 10 s） |
| `--out 路径.gif\|.png` | 可重复；文件名不以 `sim_` 开头会自动加前缀 |
| `--seed` | 随机种子（同种子结果逐像素可复现） |
| `--inputs 文件.json\|.yaml` | 外部输入：按键（含抖动）、引脚电平、触摸、ADC 电压、I2C 设备 |
| `--png-mode sheet\|last\|first` | PNG 输出拼图或单帧 |
| `--speed` | GIF 播放倍速（帧间隔按虚拟时间等比缩放） |
| `--scale --oled-color --no-glow --no-flash` | 外观：放大倍数、OLED 颜色（white/blue/yellow/yellow-blue）、发光、墨水屏全刷闪烁 |
| `--log 文件.json` | 写入运行摘要和调用记录 |
| `--wall-timeout` | 真实时间安全上限（默认 60 s） |

退出码：正常结束且有帧 → 0；固件抛异常或没有帧 → 1。

Python 里使用：

```python
import sys; sys.path.insert(0, "sim")
from run_firmware import run_firmware          # 命令行同款
res = run_firmware("eyes.py", display="ssd1306", seconds=5, out=["sim_eyes.gif"])
from mpsim import run, session                 # 底层接口
res = run("eyes.py", display="ssd1306", max_frames=50, inputs={...})
res.summary(); res.frames[0].rgb; res.console; res.log; res.pin_history(4)
with session(inputs={...}, paths=["firmware/templates"]) as s:   # 单元测试用
    import buttons; ...
```

## 运行模型

- 固件在独立线程里以 `__name__ == "__main__"` 执行；固件所在目录被复制到一个临时
  "设备文件系统"（当前目录 + `sys.path`，含 `lib/`），固件写的文件（日志等）不会污染仓库，
  写了哪些文件见 `files_written`。`main.py` 旁有 `boot.py` 时先跑 `boot.py`。
- **模拟模块优先于固件目录里的同名文件**（如固件自带的 `ssd1306.py`），因为只有模拟驱动能出帧。
- **虚拟时钟**：`sleep*` 立即推进时间；每次 `ticks_*()` 调用推进 50 µs，保证忙等循环会结束。
- **停止**：帧数或虚拟时间到上限时抛 `SimStop`（继承 `BaseException`，`except Exception` 吞不掉）。
  固件用裸 `except:` 反复吞掉时，线程被挂起并给警告；纯 Python 死循环由真实时间上限打断。
- **复位**：`deepsleep()`、`reset()`、`soft_reset()`、看门狗超时都会从头重跑固件，
  `reset_cause()`/`wake_reason()` 按 ESP32 端口的数值返回；RTC 内存、NVS（已 commit 的）跨复位保留。
- 调用记录：`res.log`（前 5000 条明细）+ `res.log_counts`（全部计数）；I2C/SPI 只记字节统计。

## 外部输入（stimulus）

```json
{
  "buttons": [{"pin": 0, "at_ms": 1000, "hold_ms": 80, "active_level": 0, "bounce_ms": 4}],
  "pins":    {"4": [[0, 1], [1500, 0]]},
  "touch":   {"7": {"idle": 20000, "touched": 60000, "windows": [[2000, 2300]]}},
  "adc":     {"1": [[0, 4.10], [60000, 3.55]]},
  "i2c_devices": [60, 104],
  "i2c_registers": {"104": {"117": [104]}},
  "uart_rx": [[500, "hello\n"]],
  "wifi": {"connect": false},
  "rtc_start": "2026-11-01T09:00:00"
}
```

`i2c_devices` 不写时：`--display ssd1306`（或不指定）默认只有 0x3C 应答，其他屏默认没有 I2C 设备。
ADC 电压是**引脚上**的电压（分压后），线性插值。

## 支持的 API

行为以 MicroPython 官方文档为准：<https://docs.micropython.org/en/latest/library/index.html>；
文档没写清的绘图细节按 MicroPython 源码 `extmod/modframebuf.c`（MIT）的算法重写，像素级一致（字体除外）。

| 模块 | 支持 | 说明 |
|---|---|---|
| `time` / `utime` | sleep、sleep_ms、sleep_us、ticks_ms/us/cpu、ticks_add、ticks_diff、time、time_ns、gmtime、localtime、mktime | [time 文档](https://docs.micropython.org/en/latest/library/time.html)；TICKS_PERIOD = 2³⁰；纪元 2000-01-01（ESP32 端口）；ticks_cpu 返回微秒 |
| `random` / `urandom` | getrandbits、randint、randrange、random、uniform、seed、choice | 可复现，但数值与真机（Yasmarang）不同 |
| `framebuf` | FrameBuffer（MONO_VLSB/MVLSB、MONO_HLSB、MONO_HMSB、RGB565、GS2_HMSB、GS4_HMSB、GS8，stride）；fill、pixel、hline、vline、line、rect、fill_rect、ellipse（含象限掩码）、poly、text、scroll、blit（key、palette、元组源）；FrameBuffer1 | [framebuf 文档](https://docs.micropython.org/en/latest/library/framebuf.html)；RGB565 按小端存（同 ESP32）；`text` 用 font8x8 字形（与真机字形不同，格子和裁剪相同） |
| `machine.Pin` | IN/OUT/OPEN_DRAIN、PULL_UP/PULL_DOWN、value/on/off/high/low/toggle/__call__、irq（IRQ_RISING/FALLING、WAKE_LOW/HIGH、wake=）、mode/pull/drive；`Signal` | 常量取 ESP32 端口值；浮空输入读 0 并警告 |
| `machine.I2C` / `SoftI2C` | scan、writeto、writevto、readfrom(_into)、readfrom_mem(_into)、writeto_mem、start/stop/readinto/write | 未应答地址抛 `OSError(19)`；寄存器内容来自 stimulus |
| `machine.SPI` / `SoftSPI` | init、write、read、readinto、write_readinto | 只统计字节，读回 0 |
| `machine.PWM` | freq、duty_u16、duty_ns、duty（ESP32 旧接口 0–1023）、deinit | 背光 PWM 会影响 LCD 亮度 |
| `machine.ADC` | read_u16、read_uv、read、atten、width、ATTN_*、WIDTH_* | 0 V 到量程上限**线性**（量程取 ESP32 quickref 的近似线性区上限 0.95/1.25/1.75/2.45 V），真机非线性 |
| `machine.TouchPad` | read、config | 数值来自 stimulus（ESP32 触摸变小，S2/S3 变大） |
| `machine.Timer` | init（PERIODIC/ONE_SHOT、period、freq、callback）、deinit | 回调在虚拟时间到点时调用；回调异常打印后继续 |
| `machine.WDT` | feed | 超时 → WDT_RESET 重启 |
| `machine.RTC` | datetime、init、memory（≤2048 B，跨深睡保留） | |
| `machine.UART` | write、read、readline、any、readinto | 接收数据来自 stimulus |
| `machine` 函数 | lightsleep、deepsleep、sleep、reset、soft_reset、reset_cause、wake_reason、wake_pins、freq、unique_id、idle、disable_irq/enable_irq、time_pulse_us、bitstream（只记录） | 唤醒：定时、ext0、ext1、gpio、Pin.irq(wake=)、触摸 |
| `esp32` | wake_on_touch/ext0/ext1/gpio/ulp、gpio_deep_sleep_hold、WAKEUP_ALL_LOW/ANY_HIGH、NVS（set/get_i32、set/get_blob、erase_key、commit）、raw_temperature、mcu_temperature、idf_heap_info | [esp32 文档](https://docs.micropython.org/en/latest/library/esp32.html)；温度、堆信息是固定假值；ULP 不模拟 |
| `micropython` | const、schedule、native/viper（原样返回）、opt_level、alloc_emergency_exception_buf、mem_info、heap_lock/unlock 等 | |
| `gc` | collect、mem_free/mem_alloc（固定假值）、enable/disable/threshold | |
| `network` | WLAN 存根：active、connect（不记录密码）、isconnected（由 stimulus 决定）、ifconfig、status、scan | 不联网 |
| `ssd1306` | SSD1306_I2C、SSD1306_SPI：show、poweroff、poweron、contrast、invert、rotate，及 buffer/width/height/pages | 与 [micropython-lib ssd1306](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py) 同 API；注意 `rotate(True)` 是正常方向、`rotate(False)` 旋转 180° |
| `st7789` / `st7789py` | ST7789（[st7789py_mpy](https://github.com/russhughes/st7789py_mpy) API）：fill、pixel、hline、vline、line、rect、fill_rect、blit_buffer、text(font,…)、polygon、rotation、sleep_mode、inversion_mode、init、color565、颜色常量；ST7789_FB（framebuf RGB565 + show()） | 直接绘图的屏在固件 sleep 时出帧；blit_buffer 按大端解释（与面板一致，所以 framebuf 小端数据要先换字节序） |
| 字体模块 `vga1_8x8`、`vga1_8x16`、`vga1_bold_16x32` 等 | 固件目录没有时提供替代 | 由 font8x8 放大，字形与原字体不同 |
| `epaper` / `ssd1680` / `ssd1681` | SSD1680、SSD1681（FrameBuffer MONO_HLSB，1=白 0=黑；`red=True` 时 `.red` 层 1=红）：show/display/refresh（全刷）、show_partial/display_partial/partial（局刷）、clear、sleep、init；计数 full_refreshes/partial_refreshes/refresh_ms_total | MicroPython 没有标准墨水屏驱动，这是模拟器自定义 API；刷新阻塞虚拟时间；局刷后显示残影（示意） |
| `ustruct ujson ubinascii ucollections uerrno uio uos uhashlib uarray ure uzlib uselect usys` | 映射到 CPython 同名模块 | 细节差异未逐一核对 |

墨水屏默认刷新时间（不是控制器数据手册值，取决于面板波形）：

| 面板 | 全刷 | 局刷 | 来源 |
|---|---|---|---|
| SSD1680 2.13" 250×122 黑白（Good Display GDEY0213B74） | 3 s | 0.3 s | [厂商产品页](https://www.good-display.com/product/391.html)（25 °C；经搜索结果读取，未打开数据手册 PDF）· 待核实 · 2026-11-01 |
| SSD1681 1.54" 200×200 黑白（GDEY0154D67） | 2 s | 0.26 s | [经销商页面](https://eckstein-shop.de/Arduino_1__154_1__Arduino_1__ESP32_1__Neu_2) · B · 待核实 · 2026-11-01 |
| 三色（红黑白） | 15 s | 不支持（改全刷并警告） | **估算**：未查到可信数值；依据只有论坛线索（C 级，三色波形更长、闪烁明显）。用 `full_refresh_ms=` 覆盖 |

## 不支持的 API 会怎样

- 访问模拟模块里没有的属性（如 `machine.mem32`、`machine.I2S`、`st7789.ST7789.bitmap`）
  → 抛 `SimUnsupported`（是 `AttributeError` 子类），消息写明"not implemented by the simulator"，
  并列入结果的 `unsupported_apis`。固件若不捕获，运行以 `stop_reason = exception` 结束，已出的帧照常输出。
- 已知但未模拟的模块：`asyncio`/`uasyncio`、`bluetooth`、`aioble`、`usocket`、`urequests`、`umqtt`、
  `espnow`、`webrepl`、`ntptime`、`dht`、`onewire`、`ds18x20`、`neopixel`、`btree`、`deflate`、`cryptolib`、
  `uctypes`：可以 import，用到任何属性就报 `SimUnsupported`。
- `sys` 没有替换（`sys.platform` 是电脑的值）；`os` 用电脑的（在临时文件系统目录里）。

## 怎么检查结果

1. 看命令行摘要：`stop_reason`（`frame_limit`/`time_limit`/`finished`/`sleep_forever` 为正常）、
   `frames`、`frame_size`、`warnings`、`unsupported`、`firmware raised`。
2. 用 PNG 拼图（`--png-mode sheet`）看关键帧；GIF 看动画节奏（帧间隔 = 虚拟时间 / `--speed`）。
3. 需要断言时用 Python 接口：`res.frames[i].rgb`（numpy 像素）、`res.console`（print 输出）、
   `res.log`、`res.pin_history(pin)`、`res.rt.stats`（睡眠时长、墨水屏刷新次数）。

## 已知限制

- 时序只到"调用级"：不模拟 CPU 执行时间、I2C/SPI 传输时间、GC 停顿。
- 不模拟功耗和电流；睡眠只统计时长（`stats.lightsleep_ms/deepsleep_ms`）。
- I2C 设备只是"应答 + 寄存器表"，没有传感器行为模型；SSD1306 不从 I2C 字节流解析（直接读 framebuf）。
- `framebuf.text` 字形与真机不同；随机数序列与真机不同。
- ST7789 的旋转按 numpy 视图实现，`inversion_mode` 按"初始化后 INVON 为正常色"处理，面板差异未建模。
- 硬件滚动（vscrdef/vscsad）不渲染。

## 文件

- `run_firmware.py` 命令行入口；`mpsim/` 模拟包（`runtime.py` 时钟与调度、`stimulus.py` 输入、
  `mp_*.py` 各模块、`render.py` 出图、`sim.py` 运行器）；`examples/` 示例固件，`examples/out/` 示例输出；
  `tests/` pytest。

## 第三方资源与许可证

| 名称 | 用途 | 许可证 | 来源 |
|---|---|---|---|
| font8x8（font8x8_basic.h，Daniel Hepper；源自 Marcel Sondaar / IBM 公有领域 VGA 字体） | `framebuf.text` 字形、st7789 替代字体 | 公有领域（Public Domain） | <https://github.com/dhepper/font8x8>，2026-11-01 获取 |
| MicroPython 文档与 `extmod/modframebuf.c` | 行为参考（未复制代码，按算法重写） | MIT | <https://github.com/micropython/micropython> |
| micropython-lib ssd1306 驱动 | API 参考 | MIT | <https://github.com/micropython/micropython-lib> |
| st7789py_mpy | API 参考 | MIT | <https://github.com/russhughes/st7789py_mpy> |
| 系统 CJK 字体（如 Noto Sans CJK） | 图上"模拟"字样，运行时从系统读取，不随库分发 | SIL OFL 1.1（Noto） | 系统自带；找不到时只写 "SIMULATED" |
