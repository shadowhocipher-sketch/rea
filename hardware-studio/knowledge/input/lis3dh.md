# LIS3DH 三轴加速度计（"摇一摇"、敲击、翻转检测）

一句话：ST 的超低功耗三轴 MEMS 加速度计，±2/4/8/16 g，I2C/SPI，两个可编程中断（运动/自由落体/6D 方向）加硬件单击/双击识别；适合"摇一摇唤醒""敲一敲""翻转换页"。

> 数据手册来源说明：st.com 本会话不可达。本页读自 GitHub 第三方仓库 sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH 托管的 **LIS3DH 数据手册 DocID17530 Rev 2（Dec 2016）**，非官方托管，标"待核实"。寄存器地址/器件 ID 另用 ST 官方 GitHub 驱动 STMicroelectronics/lis3dh-pid 交叉核对（A）。

## 关键参数

| 参数 | 值 | 来源 |
|---|---|---|
| 量程 | ±2 / ±4 / ±8 / ±16 g 可选 | [LIS3DH DocID17530 Rev2 p1](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 输出数据率 ODR | 1 / 10 / 25 / 50 / 100 / 200 / 400 Hz；低功耗 1.6 kHz、5.376 kHz；正常/高分辨率 1.344 kHz | [LIS3DH DocID17530 Rev2 表 31](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 供电 Vdd | 1.71–3.6 V（典型 2.5 V，出厂在 2.5 V 校准） | [LIS3DH DocID17530 Rev2 表 6](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| IO 供电 Vdd_IO | 1.71 V – (Vdd + 0.1 V) | [LIS3DH DocID17530 Rev2 表 6](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| FIFO | 32 级 × 16 位 | [LIS3DH DocID17530 Rev2 p1](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 工作温度 | –40 ~ +85 °C | [LIS3DH DocID17530 Rev2 表 6](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| WHO_AM_I (0Fh) | 0x33 | [ST lis3dh-pid lis3dh_reg.h（LIS3DH_ID）](https://github.com/STMicroelectronics/lis3dh-pid/blob/8c0588bb9ff7e94730425a7887e5c620903eae41/lis3dh_reg.h) · A · 2026-11-01 |

## 引脚要点

| 引脚 | 要点 | 来源 |
|---|---|---|
| SDO/SA0 | I2C 地址最低位：接地 → 0011000b（0x18），接 Vdd → 0011001b（0x19）；内部有上拉（Vdd_IO=3.6 V 时典型 20.4 kΩ），写 CTRL_REG0(1Eh)=90h 可关闭 | [LIS3DH DocID17530 Rev2 §6.1.1、表 3](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| INT1 / INT2 | 两个中断输出；CTRL_REG3 选择送到 INT1 的源（I1_CLICK、I1_IA1 等），CTRL_REG6 选择 INT2 的源并有 INT_POLARITY 位 | [LIS3DH DocID17530 Rev2 §8.10、§8.13](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| CS | SPI/I2C 选择（CS 高 = I2C） | [LIS3DH DocID17530 Rev2 表 2 引脚说明](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 电压、电流

| 模式 / ODR | 低功耗（8 位） | 正常（10 位） | 高分辨率（12 位） | 来源 |
|---|---|---|---|---|
| 1 Hz | 2 μA | 2 μA | 2 μA | [LIS3DH DocID17530 Rev2 表 12](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 10 Hz | 3 μA | 4 μA | 4 μA | [LIS3DH DocID17530 Rev2 表 12](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 50 Hz | 6 μA | 11 μA | 11 μA | [LIS3DH DocID17530 Rev2 表 12](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 400 Hz | 36 μA | 73 μA | 73 μA | [LIS3DH DocID17530 Rev2 表 12](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 掉电模式 | 0.5 μA | — | — | [LIS3DH DocID17530 Rev2 表 6](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 接口时序要点

| 项目 | 要点 | 来源 |
|---|---|---|
| I2C | 标准 100 kHz / 快速 400 kHz | [LIS3DH DocID17530 Rev2 表 8](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| SPI | 时钟 ≤ 10 MHz（周期 ≥ 100 ns） | [LIS3DH DocID17530 Rev2 表 7](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| "摇一摇"（运动中断） | INT1_CFG(30h) 打开 XHIE/YHIE/ZHIE（OR 组合，超过阈值触发）；INT1_THS(32h) 阈值 1 LSb = 16 mg@±2 g、32 mg@±4 g、62 mg@±8 g；INT1_DURATION(33h) 设持续时间；CTRL_REG3 置 I1_IA1 送到 INT1 脚 | [LIS3DH DocID17530 Rev2 §8.21–8.24](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 敲击 | CLICK_CFG(38h) 选单击/双击和轴；CLICK_SRC(39h) 读结果；CLICK_THS(3Ah) 阈值；CTRL_REG3 的 I1_CLICK 送到 INT1 | [LIS3DH DocID17530 Rev2 §8.29–8.31](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 自动睡眠/唤醒 | ACT_THS(3Eh)/ACT_DUR(3Fh)：加速度低于阈值自动切到低功耗 10 Hz，超过阈值恢复原 ODR | [LIS3DH DocID17530 Rev2 §3.2.4](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 中断锁存 | CTRL_REG5 的 LIR_INT1 置 1 时中断锁存，读 INT1_SRC(31h) 才清除 | [LIS3DH DocID17530 Rev2 §8.12](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| 地址写成 0x31/0x33 | ST 官方驱动用的是含读写位的 8 位地址（LIS3DH_I2C_ADD_L=0x31、_H=0x33）；ESP-IDF/MicroPython 用 7 位地址 0x18/0x19 | [ST lis3dh-pid lis3dh_reg.h](https://github.com/STMicroelectronics/lis3dh-pid/blob/8c0588bb9ff7e94730425a7887e5c620903eae41/lis3dh_reg.h) · A · 2026-11-01 |
| SA0 悬空 | 内部上拉让地址默认 0x19；想用 0x18 要明确接地 | [LIS3DH DocID17530 Rev2 表 3](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 中断只来一次 | 开了 LIR_INT1 锁存却不读 INT1_SRC，中断脚一直保持；MCU 用电平唤醒时尤其要清 | [LIS3DH DocID17530 Rev2 §8.12](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 阈值换量程后失效 | 阈值 LSb 随量程变化（16/32/62 mg…），改量程要重算 | [LIS3DH DocID17530 Rev2 §8.23](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| Vdd_IO 高于 Vdd | Vdd_IO 上限是 Vdd + 0.1 V；MCU 3.3 V、传感器 1.8 V 供电时要电平转换 | [LIS3DH DocID17530 Rev2 表 6](https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf) · S（镜像）· 2026-11-01 · 待核实 |
| 单击/双击参数 | 时间窗（TIME_LIMIT/LATENCY/WINDOW）的调法在 ST 应用笔记 AN3308 中，本次未读取 | https://www.st.com/ · 未查到 |

## 来源列表

- [DS] LIS3DH Datasheet DocID17530 Rev 2（STMicroelectronics，Dec 2016）。第三方镜像：https://github.com/sparkfun/SparkFun_Triple_Axis_Acclerometer-LIS3DH/blob/7d6bde80688871b4ce9355815a1cfc40219b901d/Documentation/lis3dh.pdf （sha256 前缀 852bfcf1a993f04c）。官方 https://www.st.com/resource/en/datasheet/lis3dh.pdf 本会话不可达。
- [ST-PID] ST 官方平台无关驱动（BSD-3-Clause），commit 8c0588b：https://github.com/STMicroelectronics/lis3dh-pid
- 查询日期：2026-11-01。
