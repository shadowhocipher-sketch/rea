# c04 · C 固件模板 · 【缺口探测】加速度计"摇一摇"有没有固件模板

**需求**：随身小物和桌面陪伴类产品常用"摇一摇 / 拍一拍"唤醒或切换（LIS3DH 类加速度计，I2C 地址 0x18/0x19，
WHO_AM_I 寄存器 0x0F 读出 0x33）。

**任务**：在 `firmware/templates/` 里找加速度计摇一摇模板；没有就按现有模板的写法补一个
（CONFIG 不写死引脚、文件头写验证状态、`__main__` 演示），并能在模拟器里用本目录 `stimulus.json` 跑起来：
`python sim/run_firmware.py firmware/templates/<模板>.py --inputs evals/tasks/c04_gap_shake_template/stimulus.json --seconds 5`

**判分**：
- `firmware/templates/` 下有文件名或内容含 shake / 摇 / accel / imu / lis3dh 的模板（0.4）；
- 文件头写了验证状态（"Verification status" 或"验证状态"）（0.3）；
- 用上面的激励在模拟器里跑 5 s 不抛异常（stop_reason 不是 exception）（0.3）。

这是缺口题：2026-11-01 基线时没有这个模板，得 0 分是预期的。
