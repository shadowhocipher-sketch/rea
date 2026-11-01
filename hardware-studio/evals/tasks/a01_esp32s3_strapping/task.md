# a01 · A 知识库 · ESP32-S3 strapping 引脚（带来源）

**需求**：新产品用 ESP32-S3 模组画板子，按键、LED、屏幕要避开启动相关引脚。

**任务**：只用能力库（`knowledge/`，按 component-knowledge skill），回答：
1. ESP32-S3 的 strapping 引脚是哪几个 GPIO；
2. 每个 strapping 引脚管什么（启动模式 / VDD_SPI 电压 / JTAG 信号源）；
3. 每条回答都带来源链接、来源级别、查询日期。

**判分**（`grade.py`）：从 `knowledge/` 里找 ESP32-S3 器件页的 strapping 行和各引脚说明行，与独立答案比对：
- 引脚集合 = {GPIO0, GPIO3, GPIO45, GPIO46}（0.5）；
- strapping 行带链接 + 级别 + 日期（0.2）；
- GPIO45 的作用写成 VDD_SPI 电压选择，且带来源（0.15）；
- GPIO3 的作用写成 JTAG 信号源选择，且带来源、不是"未查到"（0.15）。

答案来源：乐鑫 ESP32-S3 技术规格书 "Strapping Pins / Boot Configurations" 章节（GPIO0、GPIO46 启动模式；GPIO45 VDD_SPI 电压；GPIO3 JTAG 信号源）。评分人独立整理，不取自被测知识库。
