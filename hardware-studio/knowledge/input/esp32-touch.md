# ESP32 自带电容触摸（以 ESP32-S3 为主）

一句话：ESP32 / S2 / S3 片上集成的电容触摸外设，用 PCB 铜皮当按键，不需要额外触摸芯片；**ESP32-C3、ESP32-C6 没有这个外设**。

> 来源：乐鑫官方 GitHub 上《硬件设计指南》源文件（S）与 ESP-IDF 触摸驱动文档、soc_caps.h（A）。

## 关键参数

| 参数 | 值 | 来源 |
|---|---|---|
| 支持的芯片 | ESP32（V1）、ESP32-S2 / S3（V2）、ESP32-P4（V3）；C3、C6 不支持 | [ESP-IDF cap_touch_sens.rst 版本表](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/cap_touch_sens.rst) · A · 2026-11-01 |
| S3 通道数 | 14 路：TOUCH1–TOUCH14 = GPIO1–GPIO14；通道 0 是内部去噪通道 | [ESP-IDF soc_caps.h (esp32s3)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32s3/include/soc/soc_caps.h) · A · 2026-11-01 |
| 触摸时读数变化方向 | V1（ESP32）按下读数变小；V2（S2/S3）按下读数变大 | [ESP-IDF cap_touch_sens.rst 版本表](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/cap_touch_sens.rst) · A · 2026-11-01 |
| S3 附加能力 | 硬件滤波、基线（benchmark）、防水、接近感应、睡眠唤醒 | [ESP-IDF cap_touch_sens.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/cap_touch_sens.rst) · A · 2026-11-01 |
| 屏蔽电极驱动 | 只有 GPIO14（TOUCH14）能驱动屏蔽电极（防水设计用） | [HDG 原理图清单 Touch Sensor](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 抗扰度 | 乐鑫注明 S3 触摸尚未通过传导抗扰度（CS）测试，适用场景受限 | [HDG 原理图清单 Touch Sensor](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 触摸唤醒时的睡眠电流 | 未查到具体数值；文档只说明开启触摸唤醒后睡眠中继续采样会增加功耗，可减少充放电次数、加大采样间隔来降低 | [ESP-IDF cap_touch_sens.rst Sleep Wake-up](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/cap_touch_sens.rst) · A · 2026-11-01 · 未查到 |

## 引脚与电路要点

| 项目 | 要点 | 来源 |
|---|---|---|
| 串联电阻 | 芯片侧串 470 Ω–2 kΩ，优选 510 Ω（降耦合噪声、加强 ESD），按实测调整 | [HDG 原理图清单 Touch Sensor](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 电极尺寸 | 直径 8–15 mm；圆形/椭圆/类似指尖的形状；太大或不规则会误触相邻电极 | [HDG esp32-touch-sensor-pcb-layout.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32/esp32-touch-sensor-pcb-layout.inc) · S · 2026-11-01 |
| 走线 | 尽量短，≤ 300 mm；线宽 ≤ 0.18 mm（7 mil）；转角 ≥ 90°；到地间距 0.5–1 mm | [HDG esp32-touch-sensor-pcb-layout.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32/esp32-touch-sensor-pcb-layout.inc) · S · 2026-11-01 |
| 铺地 | 电极和走线周围铺网格地；走线远离天线 | [HDG esp32-touch-sensor-pcb-layout.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32/esp32-touch-sensor-pcb-layout.inc) · S · 2026-11-01 |
| 防水/接近感应（S3） | 屏蔽电极宽约 2 cm；顶层网格 7 mil 线宽 / 45 mil 网格（25% 填充），底层 7 mil / 70 mil（17%），网格接屏蔽驱动；保护电极宽 2 mm，与屏蔽电极间隙 1 mm；接近感应电极做闭环，宽 1.5 mm | [HDG esp32s3-touch-sensor-waterproof-design.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32s3/esp32s3-touch-sensor-waterproof-design.inc) · S · 2026-11-01 |

## 电压、电流

| 项目 | 值 | 来源 |
|---|---|---|
| 触摸外设自身工作电流 | 未查到（在芯片数据手册中，站点不可达） | https://documentation.espressif.com/esp32-s3_datasheet_en.pdf · 未查到 |
| 睡眠唤醒 | S3 可用触摸从浅睡和深睡唤醒；睡眠中采样由硬件完成，主核驱动在睡眠中不能读/配置 | [ESP-IDF cap_touch_sens.rst Sleep Wake-up](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/cap_touch_sens.rst) · A · 2026-11-01 |

## 接口时序要点

| 项目 | 要点 | 来源 |
|---|---|---|
| 判定方式 | 读数 > 基线 + active_threshold 判为按下（on_active 回调），低于则释放（on_inactive） | [ESP-IDF cap_touch_sens.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/cap_touch_sens.rst) · A · 2026-11-01 |
| 滤波 | 所有通道共用一个滤波器配置（touch_sensor_config_filter） | [ESP-IDF cap_touch_sens.rst](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/cap_touch_sens.rst) · A · 2026-11-01 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| 选了 C3/C6 才发现没触摸 | 触摸只在 ESP32/S2/S3/P4 上有；C3/C6 要外加触摸 IC 或改按键 | [ESP-IDF soc_caps.h (esp32c3)](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32c3/include/soc/soc_caps.h) · A · 2026-11-01 |
| 触摸脚和 ADC/strapping 冲突 | S3 的 GPIO1–10 同时是 ADC1，GPIO3 还是 strapping 脚；规划引脚时一起看 | [ESP-IDF gpio/esp32s3.inc](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/gpio/esp32s3.inc) · A · 2026-11-01 |
| 隔着外壳摸不灵 | 电极面积、外壳厚度和材料都影响灵敏度；乐鑫只给了电极尺寸范围，外壳厚度上限未查到，要做样机实测 | [HDG esp32-touch-sensor-electrode-pattern.inc](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/esp32/esp32-touch-sensor-electrode-pattern.inc) · S · 2026-11-01 |
| 接市电适配器后误触 | 未过 CS 测试，传导干扰可能导致误触；电池产品风险小，插电产品要实测 | [HDG 原理图清单 Touch Sensor](https://github.com/espressif/esp-hardware-design-guidelines/blob/a727293ef28136766f6fcc1ea8cc670e59c6ae1a/docs/en/schematic-checklist.rst) · S · 2026-11-01 |
| 把 V1 的"变小"逻辑搬到 S3 | S3 按下读数变大，阈值方向相反 | [ESP-IDF cap_touch_sens.rst 版本表](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/docs/en/api-reference/peripherals/cap_touch_sens.rst) · A · 2026-11-01 |

## 来源列表

- [HDG] ESP Hardware Design Guidelines 源文件，commit a727293：https://github.com/espressif/esp-hardware-design-guidelines
- [IDF] ESP-IDF 触摸驱动文档与 soc_caps.h，commit d445e94：https://github.com/espressif/esp-idf
- 查询日期：2026-11-01。
