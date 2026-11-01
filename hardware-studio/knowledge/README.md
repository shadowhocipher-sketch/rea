# 元器件与模块知识库 `knowledge/`

给任何小型电子产品选型、画原理图、写驱动时查用。每个器件一页，每个类别一张选型表。
所有事实都按 [研究方法](../.claude/skills/research-method/SKILL.md) 标了来源链接、来源级别和查询日期；
`python knowledge/check_sources.py` 会逐行检查。

## 怎么读一行数据

`| 参数 | 值 | [文档 章节/表号](链接) · 级别 · 查询日期 · 标记 |`

- **S**：原厂一手资料。乐鑫《硬件设计指南》源文件取自乐鑫官方 GitHub 仓库 `espressif/esp-hardware-design-guidelines`（固定到 commit），算 S。
- **S（镜像）**：原厂数据手册 PDF，但本会话是从**第三方 GitHub 仓库**读到的（原厂站点被网络代理拦截）。内容是原厂文件，托管方不是原厂，所以这些行一律再加"待核实"——以后能访问原厂站点时，按页尾"来源列表"里的官方地址核对版本后即可去掉"待核实"。
- **A**：官方二手资料，如 ESP-IDF 文档/头文件/例程（`espressif/esp-idf`）、`espressif/esp-iot-solution`、ST 官方驱动 `STMicroelectronics/lis3dh-pid`。
- **B**：立创 / LCSC / JLCPCB 商品页。本次商品页无法直接打开，价格来自搜索引擎返回的页面摘要快照，所以全部"待核实"。
- **C**：社区线索（开源库、论坛、issue），只当线索，必带"待核实"。
- 标记：**未查到**（写了查过哪里、为什么查不到）、**估算**（写了公式和依据）、**待核实**（写了冲突点或原因）。
- "推论"：由已引用事实推出的结论，正文里会写"推论"二字。

## 本次查询的网络限制（2026-11-01）

本次会话只能访问 github.com / raw.githubusercontent.com 和搜索引擎。以下原厂站点无法访问（DNS 不可解析或代理返回 403）：
documentation.espressif.com、www.espressif.com、docs.espressif.com、st.com、analog.com、microchip.com、lcsc.com、jlcpcb.com、szlcsc.com、usb.org、solomon-systech.com、good-display.com 等。
因此**乐鑫芯片/模组数据手册里独有的数值（射频收发电流、模组尺寸、内部上拉阻值等）写的是"未查到"**；
改用乐鑫官方 GitHub 上的硬件设计指南和 ESP-IDF 文档补齐了大部分设计要点。

## 目录

### mcu/ 主控
- [esp32-s3.md](mcu/esp32-s3.md) — 双核、Wi-Fi + BLE、USB OTG、14 路触摸；strapping、ADC/触摸脚、深睡电流、模组 vs 芯片
- [esp32-c3.md](mcu/esp32-c3.md) — 低成本 RISC-V、Wi-Fi + BLE、无触摸无 OTG
- [esp32-c6.md](mcu/esp32-c6.md) — Wi-Fi 6 + BLE + 802.15.4（Thread/Zigbee）
- [selection.md](mcu/selection.md) — MCU 选型表

### display/ 显示
- [ssd1306.md](display/ssd1306.md) — 128×64 单色 OLED
- [st7789.md](display/st7789.md) — 240×320 彩色 TFT（SPI 小彩屏）
- [ssd1680-ssd1681.md](display/ssd1680-ssd1681.md) — 墨水屏控制器：BUSY、深睡、局刷、刷新时间
- [selection.md](display/selection.md) — 显示选型表

### input/ 输入
- [esp32-touch.md](input/esp32-touch.md) — ESP32 片上电容触摸：电极、走线、防水
- [tactile-switch.md](input/tactile-switch.md) — 轻触按键与消抖（Omron B3U、esp-iot-solution button）
- [lis3dh.md](input/lis3dh.md) — 三轴加速度计：摇一摇、敲击中断
- [selection.md](input/selection.md) — 输入选型表

### audio/ 声音
- [buzzer.md](audio/buzzer.md) — 无源 MLT-8530 / 有源 TMB12A05 的驱动方式
- [max98357a.md](audio/max98357a.md) — I2S D 类功放
- [selection.md](audio/selection.md) — 音频选型表

### power/ 电源
- [usb-c-sink.md](power/usb-c-sink.md) — USB-C 受电：CC 下拉 5.1 kΩ（Type-C 规范 R2.1）
- [tp4056.md](power/tp4056.md) — 单节锂电线性充电
- [dw01-protection.md](power/dw01-protection.md) — 锂电保护 DW01-P + FS8205A
- [me6211.md](power/me6211.md) — 500 mA LDO（静态 60 μA）
- [xc6206.md](power/xc6206.md) — 超低静态电流 LDO（1 μA，约 200 mA）
- [selection.md](power/selection.md) — 电源选型表

### wireless/ 无线
- [esp32-wifi-ble-power.md](wireless/esp32-wifi-ble-power.md) — Wi-Fi/BLE 各模式电流与供电
- [esp32-antenna-coexistence.md](wireless/esp32-antenna-coexistence.md) — 天线净空、射频布局、Wi-Fi/BLE/802.15.4 共存
- [selection.md](wireless/selection.md) — 无线选型表

## 检查

```bash
cd hardware-studio
. .venv/bin/activate
python knowledge/check_sources.py        # 扫描全部 Markdown 表格行，退出码非 0 表示有行缺来源
pytest knowledge/tests                   # 检查脚本的单元测试（含故意缺来源的反例）+ 全库检查
```

新增器件页、维护方法见 [component-knowledge skill](../.claude/skills/component-knowledge/SKILL.md)。
