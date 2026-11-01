# firmware/ — MicroPython 固件模式库

通用模板，不写死引脚：每个模板开头有 `CONFIG` 字典，设备上放 `config.json` 可覆盖同名键
（`load_config()`，每个模板各带一份，方便单文件拷到板子上）。

**验证状态（2026-11-01）：五个模板、`drivers/ssd168x.py` 和 `examples/` 都只在 `sim/` 模拟器 / 假 SPI 上运行过，未在任何真机上验证。**
每个文件头写了已验证 / 未验证的具体项。

| 模板 | 作用 | 主要 API（官方文档） |
|---|---|---|
| `templates/state_machine.py` | 事件驱动状态机：事件队列、每个状态的超时、enter/exit/动作回调、表校验 | [time.ticks_diff](https://docs.micropython.org/en/latest/library/time.html) |
| `templates/buttons.py` | 按键与电容触摸消抖：单击、双击、长按（LONG + HOLD_END）；触摸基线跟踪，两种方向 | [Pin](https://docs.micropython.org/en/latest/library/machine.Pin.html)、[TouchPad](https://docs.micropython.org/en/latest/esp32/quickref.html#capacitive-touch) |
| `templates/power.py` | 低功耗：ext0/触摸/定时唤醒配置、light/deep sleep、空闲计时、RTC 内存启动计数、复位/唤醒原因名称 | [machine 电源函数](https://docs.micropython.org/en/latest/library/machine.html)、[esp32](https://docs.micropython.org/en/latest/library/esp32.html)、[ESP32 深睡](https://docs.micropython.org/en/latest/esp32/quickref.html#deep-sleep-mode) |
| `templates/selftest.py` | 开机自检：I2C 扫描对照期望地址、屏幕测试图案、电池电压（ADC 分压）、结果上屏、JSON 行日志（限大小） | [I2C](https://docs.micropython.org/en/latest/library/machine.I2C.html)、[ESP32 ADC](https://docs.micropython.org/en/latest/esp32/quickref.html#adc-analog-to-digital-conversion) |
| `templates/shake.py` | 摇一摇：LIS3DH 类加速度计（自动探测 0x18/0x19、核对 WHO_AM_I）配置运动中断到 INT1，INT1 上升沿 → SHAKE 事件（带冷却）；深睡 INT1 唤醒；无中断线时用 `ShakeDetector` 软件检测采样。寄存器位来源见 `knowledge/input/lis3dh.md`"寄存器位" | [I2C](https://docs.micropython.org/en/latest/library/machine.I2C.html)、[esp32 唤醒](https://docs.micropython.org/en/latest/library/esp32.html) |

每个模板都能直接当 `main.py` 跑演示（`if __name__ == "__main__"`），也能 `import` 用里面的类。

## 驱动 `drivers/`

| 驱动 | 作用 | 验证状态（2026-11-01） |
|---|---|---|
| `drivers/ssd168x.py` | SSD1680 / SSD1681 墨水屏 MicroPython 驱动（SPI + CS/DC/RST/BUSY）：全刷、局刷、深睡、BUSY 等待超时（`BusyTimeout`）、黑白红三色、rotation 0–3 | **未在真机运行**。只用假 SPI/Pin 录命令序列对照数据手册流程、并在模拟器里跑过。待真机核实：RAM 位序/扫描方向、rotation 方向、面板 OTP 的 Display Mode 2 是否是局刷波形、边框值、刷新时间 |

**API 与模拟器 `epaper` 模块完全一致**（类名、构造参数、方法、属性、常量都同名；`firmware/tests/test_fw_ssd168x.py` 逐项比对），所以同一份固件在模拟器和真机上不用改：

```python
from machine import Pin, SPI
import ssd168x                      # 模拟器里 ssd168x / epaper / ssd1680 / ssd1681 都映射到模拟模型
spi = SPI(1, baudrate=4_000_000, sck=Pin(12), mosi=Pin(11))
epd = ssd168x.SSD1681(spi, Pin(10, Pin.OUT), Pin(9, Pin.OUT), Pin(8, Pin.OUT), Pin(7, Pin.IN),
                      rotation=0, busy_timeout_ms=None)   # 2.13" 用 SSD1680（默认 122×250）
epd.fill(ssd168x.WHITE); epd.text("hi", 0, 0, ssd168x.BLACK)
epd.show()            # 全刷（display()/refresh() 同义；show(full=False) = 局刷）
epd.show_partial()    # 局刷（display_partial()/partial() 同义）；三色屏自动改全刷
epd.sleep()           # 深睡 mode 1；下次刷新自动硬件复位 + init；没接 RST 时抛 ValueError
```

- 上板：把 `drivers/ssd168x.py` 拷到板子上（固件写 `import epaper` 的，拷成 `epaper.py`）。
- 命令序列（数据手册 SSD1680 Rev0.14 §9.1 / SSD1681 Rev0.13 §8.1，来源和每个参数的依据写在文件头和
  `knowledge/display/ssd1680-ssd1681.md`）：init = RST 低 10 ms → `12h` → 等 10 ms + BUSY → `01h` `11h`(03) `44h` `45h` `3Ch`(05) →
  `18h`(80) → `22h`(B1) `20h` → 等 BUSY；全刷 = `3Ch`(05) `4Eh` `4Fh` `24h`(新图) `4Eh` `4Fh` `26h`(同图) `22h`(F7) `20h` → 等 BUSY；
  局刷 = `3Ch`(80) … `24h`(新图) … `26h`(上一帧) `22h`(FF) `20h` → 等 BUSY；深睡 = `10h`(01)。`0Ch` 软启动保持上电默认值。
- BUSY 超时：默认 max(5 s, 3 × 预期刷新时间)，`busy_timeout_ms=` 覆盖；超时抛 `ssd168x.BusyTimeout`（`OSError` 子类，errno 110）。
- `refresh_ms_total` 在真机上是实测 BUSY 时间，在模拟器里是模型时间。
- 已知限制：rotation 1/3 在 MCU 上逐像素转置（2.13" 约 3 万像素，较慢）；局刷前假定面板显示的是上一次本对象刷出的图
  （开机/深睡重启后先全刷一次，模拟器会对"第一次就局刷"给警告）；部分 2.13" 面板需要 `21h` 源极范围设置，驱动未发送，图像偏移时检查。

## 示例 `examples/`

| 示例 | 演示命令 | 预期 |
|---|---|---|
| `examples/epaper_hello.py` | `python sim/run_firmware.py firmware/examples/epaper_hello.py --display epaper --seconds 120 --out /tmp/sim_hello.png` | 退出码 0，1 次全刷 + 5 次局刷，打印 `done full=1 partial=5`；真机上配合 `drivers/ssd168x.py` 运行（未在真机运行） |

## asyncio 固件

模拟器支持 `asyncio`/`uasyncio`（虚拟时钟，见 `sim/README.md`"支持的 API"），用 `asyncio.run`、`create_task`、`sleep_ms`、
`gather`、`Event`、`Lock`、`wait_for`、`ThreadSafeFlag`（IRQ 里 `set()`）写的多任务固件可以直接模拟。TCP 流不支持。

## 在模拟器里跑

```bash
. .venv/bin/activate
python sim/run_firmware.py firmware/templates/state_machine.py --seconds 20 --out /tmp/sim_fsm.png
python sim/run_firmware.py firmware/templates/selftest.py --inputs my_inputs.json --seconds 10 --out /tmp/sim_selftest.png
python -m pytest firmware/tests -q
```

`firmware/tests/test_fw_templates.py` 覆盖：状态转换与超时、事件队列溢出、表校验；
按键抖动、毛刺过滤、单击/双击/长按时序、两种触摸方向；深睡循环（按键 ext0 唤醒、定时唤醒）、
浅睡触摸唤醒、启动计数；自检 PASS/WARN/FAIL、日志写入与大小上限。
`firmware/tests/test_fw_ssd168x.py` 覆盖：init/全刷/局刷/深睡的命令序列和参数对照数据手册流程、BUSY 高时不发 SPI、RES# 脉宽、
BUSY 超时、rotation 映射、三色 RAM、与模拟器同样绘图代码逐像素一致、API 与模拟器一致、示例固件在模拟器里跑（含"真驱动 + 模拟 machine"）。
`firmware/tests/test_fw_shake.py` 覆盖：寄存器值对照数据手册表格、WHO_AM_I 错误/无应答、INT1 边沿与冷却、深睡 INT1 唤醒、软件检测器。
模拟器里的 I2C 设备只是寄存器表，**不模拟传感器**，所以阈值和"多用力算摇"必须上真机调。

## 上真机前要做的

- 按板子改 `CONFIG`（或 `config.json`）：引脚、I2C 地址、分压比、触摸阈值。
- 电池阈值 `battery_low_v / battery_min_v` 是占位值，按电芯数据手册设置。
- 唤醒引脚必须是芯片支持的 RTC GPIO（ESP32 见 quickref；S2/S3/C3/C6 查 ESP-IDF "Sleep Modes"，待核实）。
- 实测：按键抖动、触摸原始值范围、深睡电流、ADC 读数与万用表对比。验证后把结果写回各文件头的"验证状态"。
