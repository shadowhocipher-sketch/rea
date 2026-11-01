# firmware/ — MicroPython 固件模式库

通用模板，不写死引脚：每个模板开头有 `CONFIG` 字典，设备上放 `config.json` 可覆盖同名键
（`load_config()`，每个模板各带一份，方便单文件拷到板子上）。

**验证状态（2026-11-01）：四个模板都只在 `sim/` 模拟器里运行过，未在任何真机上验证。**
每个文件头写了已验证 / 未验证的具体项。

| 模板 | 作用 | 主要 API（官方文档） |
|---|---|---|
| `templates/state_machine.py` | 事件驱动状态机：事件队列、每个状态的超时、enter/exit/动作回调、表校验 | [time.ticks_diff](https://docs.micropython.org/en/latest/library/time.html) |
| `templates/buttons.py` | 按键与电容触摸消抖：单击、双击、长按（LONG + HOLD_END）；触摸基线跟踪，两种方向 | [Pin](https://docs.micropython.org/en/latest/library/machine.Pin.html)、[TouchPad](https://docs.micropython.org/en/latest/esp32/quickref.html#capacitive-touch) |
| `templates/power.py` | 低功耗：ext0/触摸/定时唤醒配置、light/deep sleep、空闲计时、RTC 内存启动计数、复位/唤醒原因名称 | [machine 电源函数](https://docs.micropython.org/en/latest/library/machine.html)、[esp32](https://docs.micropython.org/en/latest/library/esp32.html)、[ESP32 深睡](https://docs.micropython.org/en/latest/esp32/quickref.html#deep-sleep-mode) |
| `templates/selftest.py` | 开机自检：I2C 扫描对照期望地址、屏幕测试图案、电池电压（ADC 分压）、结果上屏、JSON 行日志（限大小） | [I2C](https://docs.micropython.org/en/latest/library/machine.I2C.html)、[ESP32 ADC](https://docs.micropython.org/en/latest/esp32/quickref.html#adc-analog-to-digital-conversion) |

每个模板都能直接当 `main.py` 跑演示（`if __name__ == "__main__"`），也能 `import` 用里面的类。

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

## 上真机前要做的

- 按板子改 `CONFIG`（或 `config.json`）：引脚、I2C 地址、分压比、触摸阈值。
- 电池阈值 `battery_low_v / battery_min_v` 是占位值，按电芯数据手册设置。
- 唤醒引脚必须是芯片支持的 RTC GPIO（ESP32 见 quickref；S2/S3/C3/C6 查 ESP-IDF "Sleep Modes"，待核实）。
- 实测：按键抖动、触摸原始值范围、深睡电流、ADC 读数与万用表对比。验证后把结果写回各文件头的"验证状态"。
