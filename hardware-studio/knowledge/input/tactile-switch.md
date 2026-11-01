# 轻触按键（以 Omron B3U 为例）与消抖

一句话：机械轻触开关按下/松开时触点会弹跳几毫秒，MCU 直接读会读到多次按下；硬件上留好上拉和唤醒脚，软件上按"采样周期 × 连续次数"做消抖。

> 器件参数以 Omron B3U 超小型贴片轻触开关为例（Cat. No. A162-E1-05），读自 GitHub 第三方仓库 femtoduino/femto-usb 托管的原厂 PDF，非官方托管，标"待核实"。消抖参数参考乐鑫官方 esp-iot-solution 的 button 组件（A）。

## 关键参数（器件：Omron B3U）

| 参数 | 值 | 来源 |
|---|---|---|
| 额定 | 1–50 mA，5–12 VDC（阻性负载） | [Omron B3U Ratings/Characteristics](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 弹跳时间（Bounce time） | ≤ 5 ms | [Omron B3U Ratings/Characteristics](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 接触电阻 | ≤ 100 mΩ（初始，1 mA 5 VDC） | [Omron B3U Ratings/Characteristics](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 寿命 | 顶按型 ≥ 200,000 次；侧按型 ≥ 100,000 次 | [Omron B3U Ratings/Characteristics](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 操作力 | 顶按 1.50 ± 0.49 N；侧按 1.59 ± 0.49 N | [Omron B3U Operating Characteristics](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 尺寸 | 1.2 × 3 × 2.5 mm（高 × 宽 × 深） | [Omron B3U 封面](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 工作温度 | –25 ~ +70 °C（60%RH 以下，无结冰凝露） | [Omron B3U Ratings/Characteristics](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 引脚与接法要点

| 项目 | 要点 | 来源 |
|---|---|---|
| 接法 | 一端接 GPIO（开内部或外部上拉），一端接地，按下读低电平；额定最小 1 mA / 5 V 是开关厂的测试条件，3.3 V 小电流读取的可靠性未在手册中给出 | [Omron B3U Ratings/Characteristics](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| ESP32 内部上拉阻值 | 未查到（在芯片数据手册中，站点不可达） | https://documentation.espressif.com/esp32-s3_datasheet_en.pdf · 未查到 |
| 深睡唤醒按键 | C3：只有 GPIO0–5 能唤醒深睡（IDF GPIO 文档）；S3：22 个 RTC IO（GPIO0–21）可用 ext0/ext1 唤醒；C6：8 个 RTC/LP IO（GPIO0–7）可用 ext1 唤醒 | [ESP-IDF sleep_modes.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/system/sleep_modes.rst) · A · 2026-11-01；[soc_caps.h SOC_RTCIO_PIN_COUNT](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc) · A · 2026-11-01 |
| 兼作 BOOT 键 | S3 用 GPIO0、C3/C6 用 GPIO9 做下载键；这些脚不要并大电容 | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |

## 电压、电流

| 项目 | 值 | 来源 |
|---|---|---|
| 按下时上拉电流 | 估算：I = 3.3 V ÷ R_上拉；例如外接 10 kΩ 时 0.33 mA，长按期间持续消耗（电池产品要算进去） | [Omron B3U Ratings](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · 估算 |

## 接口时序要点（消抖）

| 项目 | 要点 | 来源 |
|---|---|---|
| 弹跳上限 | B3U 弹跳 ≤ 5 ms，消抖窗口应大于它 | [Omron B3U Ratings/Characteristics](https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 乐鑫 button 组件默认值 | 扫描周期 5 ms；消抖 2 个周期（即 10 ms）；短按判定 180 ms；长按判定 1500 ms | [esp-iot-solution button Kconfig](https://github.com/espressif/esp-iot-solution/blob/d2d935d0ee3e78deffa3981cc8c39ac8f534932b/components/button/Kconfig) · A · 2026-11-01 |
| 可调范围 | 扫描周期 2–500 ms；消抖 1–7 个周期；短按 50–800 ms；长按 500–5000 ms | [esp-iot-solution button Kconfig](https://github.com/espressif/esp-iot-solution/blob/d2d935d0ee3e78deffa3981cc8c39ac8f534932b/components/button/Kconfig) · A · 2026-11-01 |
| GPIO 硬件毛刺滤波 | ESP-IDF 的 pin glitch filter 只滤掉短于 2 个 IO_MUX 采样时钟的脉冲（时长不可配）；推论：这是纳秒级滤波，不能代替毫秒级机械消抖 | [ESP-IDF gpio.rst Glitch Filter](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio.rst) · A · 2026-11-01 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| 用边沿中断直接计数 | 一次按下触发多次中断；中断里只记时间戳/启动定时器，按 10 ms 级窗口确认电平 | [esp-iot-solution button Kconfig](https://github.com/espressif/esp-iot-solution/blob/d2d935d0ee3e78deffa3981cc8c39ac8f534932b/components/button/Kconfig) · A · 2026-11-01 |
| 唤醒键接错脚 | 深睡只能由特定 GPIO 唤醒（见上表）；画原理图前先定唤醒脚 | [ESP-IDF gpio/esp32c3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32c3.inc) · A · 2026-11-01 |
| 按键接在 strapping 脚又加了消抖电容 | GPIO0（S3）/GPIO9（C3、C6）加大电容可能让芯片上电进下载模式 | [HDG 原理图清单 Strapping Pins](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 按键经过长线引到外壳 | 长线引入 ESD；乐鑫对触摸脚建议串 470 Ω–2 kΩ 加强 ESD，对普通按键的串阻建议未查到 | [HDG 原理图清单 Touch Sensor](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 · 未查到 |

## 来源列表

- [Omron] Ultra-small Tactile Switch (SMT) B3U，Cat. No. A162-E1-05。第三方镜像：https://github.com/femtoduino/femto-usb/blob/3b0757e438f7e71c113634b8b79e3e4c98cc137e/omron_ultra-small_tactile_switch_%28SMT%29_en-b3u.pdf （sha256 前缀 9ad5a04e31524d1e）。官方 www.omron.com/ecb 本会话未尝试访问（同类官方站点均被拦截）。
- [iot-button] espressif/esp-iot-solution，components/button/Kconfig，commit d2d935d：https://github.com/espressif/esp-iot-solution
- [IDF] ESP-IDF，commit d445e94：https://github.com/espressif/esp-idf
- 查询日期：2026-11-01。
