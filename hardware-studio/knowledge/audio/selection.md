# 音频选型表

价格说明：立创/LCSC/JLCPCB 商品页本会话无法直接打开，价格来自 WebSearch 返回的商品页摘要快照（时间不明、快照间有出入），全部标"待核实"。喇叭本身的价格本次未查。

| 场景 | 推荐器件 | 价格区间（美元/个） | 取舍 | 来源 |
|---|---|---|---|---|
| 只要"嘀"一声提示、最省事 | 有源蜂鸣器，例：华能 TMB12A05（LCSC C96093，4–8 V） | 约 0.097（LCSC）；JLCPCB 摘要 0.096–0.19 | GPIO 开关即可；只有一个音调；该型号要 5 V，3.3 V 产品要选 3 V 款（如 HNB09A03 C96102，价格未查到） | [LCSC C96093](https://www.lcsc.com/product-detail/C96093.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 要简单旋律、几个音调、体积小 | 无源电磁蜂鸣器，例：华能 MLT-8530（LCSC C94599，贴片 8.5 mm） | 约 0.10 起（LCSC）；JLCPCB 摘要 0.10–0.20 | 能放旋律，2.5–4.5 V 适合 3.3 V；要 PWM + 晶体管驱动；离谐振点（2.7 kHz）远就小声 | [LCSC C94599](https://www.lcsc.com/product-detail/C94599.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |
| 说话、播放音效/音乐 | MAX98357A（TQFN，LCSC C910544）+ 4 Ω/8 Ω 小喇叭 | 1.33（1 个）/ 0.89（100+）/ 0.82（1000+） | 音质好、无需 MCLK/I2C；占 3 个 I2S 脚 + 1 个 SD_MODE 脚；要存音频（flash 空间）；待机须拉低 SD_MODE 才到 0.6 μA | [LCSC C910544](https://www.lcsc.com/product-detail/Audio-Power-OpAmps_Analog-Devices-Inc-Maxim-Integrated-MAX98357AETE-T_C910544.html) · B · 2026-11-01 · 待核实（仅搜索摘要） |

## 依据

| 对比项 | 有源蜂鸣器 TMB12A05 | 无源蜂鸣器 MLT-8530 | MAX98357A | 来源 |
|---|---|---|---|---|
| 工作电压 | 4–8 V | 2.5–4.5 V | 2.5–5.5 V | [LCSC C94599 / C96093 摘要](https://www.lcsc.com/product-detail/C94599.html) · B · 2026-11-01 · 待核实 |
| 工作电流 | 30 mA | 未查到 | 静态 2.4 mA（3.7 V）+ 输出功率相应电流 | [MAX98357 Rev13](https://github.com/Xinyuan-LilyGO/LilyGo-HAL/blob/5045bdde1bdadc713935a06182e2f87f2c19f77c/MAX98357A/MAX98357A-MAX98357B.pdf) · S（镜像）· 2026-11-01 · 待核实 |

器件页：[buzzer.md](buzzer.md)、[max98357a.md](max98357a.md)。
