# 蜂鸣器：无源（外驱）与有源（自激）

一句话：**无源**蜂鸣器内部没有振荡电路，要 MCU 用 PWM 方波按谐振频率驱动，能放不同音调；**有源**蜂鸣器内部自带振荡，加直流电就响，只有一个固定音调。蜂鸣器没有统一的数据手册，本页以江苏华能（Jiangsu Huaneng）两款立创常见型号为例：无源电磁式 **MLT-8530**、有源 **TMB12A05**。

> 来源说明：两款器件的原厂规格书在 datasheet.lcsc.com 上，本会话代理拒绝连接，未能读取。下面器件参数来自 LCSC 商品页的搜索摘要（B 级，按研究方法 B 级参数须回到原厂核对），全部标"待核实"。驱动方式的 MCU 侧参数来自乐鑫官方资料（A）。

## 关键参数（器件）

| 参数 | MLT-8530（无源电磁式） | TMB12A05（有源） | 来源 |
|---|---|---|---|
| 类型 | 外驱（externally driven）电磁式，贴片 8.5 × 8.5 mm | 自激（内置驱动），插件 Φ12 mm | [LCSC C94599](https://www.lcsc.com/product-detail/C94599.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 工作电压 | 2.5–4.5 V | 4–8 V | [LCSC C96093](https://www.lcsc.com/product-detail/C96093.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 谐振 / 发声频率 | 2.7 kHz | 2.4 kHz | [LCSC C94599](https://www.lcsc.com/product-detail/C94599.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 声压 | 80 dB | 85 dB | [LCSC C96093](https://www.lcsc.com/product-detail/C96093.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 电流 | 未查到（规格书 datasheet.lcsc.com/lcsc/1811151451_Jiangsu-Huaneng-Elec-MLT-8530_C94599.pdf 不可达） | 30 mA | [LCSC C96093](https://www.lcsc.com/product-detail/C96093.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 线圈电阻、测试距离、占空比条件 | 未查到 | 未查到 | https://datasheet.lcsc.com/lcsc/1811151451_Jiangsu-Huaneng-Elec-MLT-8530_C94599.pdf · 未查到 |
| 工作温度 | –20 ~ +70 °C | 未查到 | [LCSC C94599](https://www.lcsc.com/product-detail/C94599.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |

## 引脚要点

| 项目 | 要点 | 来源 |
|---|---|---|
| 极性 | 两种都有 +/– 极性；有社区 PR 提到 EasyEDA 符号只标了 MLT-8530 的 1 脚 "+"，2 脚为 "–"，画板前对照规格书封装图 | [nakomis/katooni PR #9](https://github.com/nakomis/katooni/pull/9) · C · 2026-11-01 · 待核实 |
| 驱动脚 | 无源：接一个 LEDC（PWM）通道；有源：接普通 GPIO 开关即可 | [ESP-IDF soc_caps.h (esp32s3) LEDC](https://github.com/espressif/esp-idf/blob/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc/esp32s3/include/soc/soc_caps.h) · A · 2026-11-01 |

## 电压、电流

| 项目 | 要点 | 来源 |
|---|---|---|
| TMB12A05 用 3.3 V 系统 | 额定 4–8 V，3.3 V GPIO 直驱低于额定下限；接 5 V（USB/升压）并用三极管或 MOS 低边开关 | [LCSC C96093](https://www.lcsc.com/product-detail/C96093.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 电流是否超出 GPIO 能力 | 有源 30 mA；ESP32 GPIO 驱动能力在数据手册中（未查到），稳妥做法是用晶体管/MOS 驱动 | https://documentation.espressif.com/esp32-s3_datasheet_en.pdf · 未查到 |

## 接口时序要点（驱动方式）

| 项目 | 要点 | 来源 |
|---|---|---|
| 无源蜂鸣器 PWM | 用 LEDC 输出约 50% 占空比方波，频率设在谐振频率（MLT-8530 为 2.7 kHz）附近最响；改频率出不同音调 | [LCSC C94599](https://www.lcsc.com/product-detail/C94599.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| LEDC 资源 | S3 有 8 个 LEDC 通道、C3/C6 各 6 个；S3/C3 定时器位宽 14 位，C6 20 位 | [ESP-IDF soc_caps.h](https://github.com/espressif/esp-idf/tree/d445e947156f276dfe0db5804e4edf6ae90fe6fb/components/soc) · A · 2026-11-01 |
| 电磁式是感性负载 | 社区做法是 MOSFET 低边驱动 + 续流二极管；原厂推荐驱动电路未查到 | [MAGNIS-v1-GroundStation](https://github.com/Emilio-Guadarrama/MAGNIS-v1-GroundStation) · C · 2026-11-01 · 待核实 |
| 有源蜂鸣器不要 PWM | 社区 issue 指出对有源蜂鸣器做 PWM 斩波会把平均电压拉到最低工作电压以下，应直接给直流开/关 | [BenSeverson/bisque issue #342](https://github.com/BenSeverson/bisque/issues/342) · C · 2026-11-01 · 待核实 |

## 易踩的坑

| 坑 | 说明 / 对策 | 来源 |
|---|---|---|
| 买错类型 | 无源加直流不响（只"咔"一声）；有源给 PWM 音调怪或不响。下单前看商品页"外驱/自激" | [LCSC C94599](https://www.lcsc.com/product-detail/C94599.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 频率偏离谐振点 | 偏离 2.7 kHz 太远声音明显变小；具体频响曲线在规格书（未查到） | https://datasheet.lcsc.com/lcsc/1811151451_Jiangsu-Huaneng-Elec-MLT-8530_C94599.pdf · 未查到 |
| 3.3 V 系统选了 5 V 有源款 | TMB12A05 额定 4–8 V；3.3 V 产品要选 3 V 款（如 HNB09A03，摘要写 3 V、3 kHz）或改用无源 | [LCSC C96102](https://www.lcsc.com/product-detail/C96102.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 想要"可爱"的提示音 | 有源只有一个固定音调；要旋律只能用无源 + PWM 改频率，但离谐振点越远越小声，需样机试听 | [LCSC C94599](https://www.lcsc.com/product-detail/C94599.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |

## 来源列表

- [B] LCSC 商品页（WebSearch 摘要，未能直接打开）：MLT-8530 https://www.lcsc.com/product-detail/C94599.html ；TMB12A05 https://www.lcsc.com/product-detail/C96093.html ；HNB09A03 https://www.lcsc.com/product-detail/C96102.html
- [原厂规格书，未读取] https://datasheet.lcsc.com/lcsc/1811151451_Jiangsu-Huaneng-Elec-MLT-8530_C94599.pdf （代理拒绝连接）
- [IDF] ESP-IDF soc_caps.h，commit d445e94：https://github.com/espressif/esp-idf
- [C] 社区线索：https://github.com/nakomis/katooni/pull/9 、https://github.com/BenSeverson/bisque/issues/342 、https://github.com/Emilio-Guadarrama/MAGNIS-v1-GroundStation
- 查询日期：2026-11-01。
