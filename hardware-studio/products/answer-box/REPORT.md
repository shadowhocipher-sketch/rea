# answer-box 报告（迁移测试，2026-11-01）

产品：口袋大小墨水屏"答案之书"，摇一摇换一句答案；锂电 + USB-C，不联网，目标 ¥99 以内。
按 `.claude/skills/new-product/SKILL.md` 八步走完。下文区分**实际运行过的**（命令 + 结果）和**只是推理的**（标"推论/估算"）。
模拟图标"模拟 / Simulated"，渲染图标"渲染图 / Render"，都不是实拍；没有任何真机、打样或报价。

## 结论

- **做到哪一步**：1–8 步交付物都生成了；`product.py check` 除"最大数量档单台 ≤ 目标"外全部 OK（结果见文末）。
- **成本（CNY，`--fx USD=6.7829`：2026-09 人民币中间价，来自搜索摘要，待核实）**：
  100 台 **¥120.33/台**，1000 台 **¥115.43/台**，比 ¥99 高 **¥21.3 / ¥16.4（+22% / +17%）**。
  金额中实查 23.9% / 22.8%、待核实 58.3% / 59.8%、估算 17.8% / 17.4%——**实查不到 50%，结论是估算**。
  若 ¥99 指零售价而不是成本，差距更大（见 brief.yaml open_questions）。
- **模拟**：固件在模拟器里跑通（退出码 0）：摇一摇 → 换答案，闲置 → 深睡 → INT1 唤醒；墨水屏 全刷 3 / 局刷 6 / 7560 ms，与按固件逻辑手算一致。**未上真机**。
- **外壳**：58 × 42 × 16.6 mm（上限 70×50×18），MJF PA12，`cad_out/check_report.json` ok = true（几何有效、干涉 0、USB 插头插到底、参数警告 0）。
- **合规**：按特征（无无线、不联网、锂电、无适配器、非儿童、仅 CN）生成 **3 条**（CN-03/05/07），全部待核实；若"带射频但不开"也算无线，则 5 条（+CN-01/02）。
- **最大风险**：①成本超标，最贵两项（墨水屏模块 ¥38.05、MJF 外壳 ¥26.45）都是待核实价；②库里没有墨水屏真机驱动（模拟器 API 不是真驱动）；③"射频在但不开"的合规归类；④中文答案需要设备端中文字库。

## 交付清单

| # | 交付物 | 实际文件 | 状态 |
|---|---|---|---|
| 1 | 简报 | `brief.yaml` | OK |
| 2 | 选型 + 包络 | `selection.md`（+ 回写 `knowledge/input/lis3dh.md`、`knowledge/display/ssd1680-ssd1681.md`） | OK |
| 3 | 接线表、固件、接线图 | `pins.csv`（42 根线）、`firmware/main.py`、`firmware/shake.py`（库模板原样复制）、`out/wiring_answer-box.svg/png` | OK：`wiring.py` 输出 `OK: every wire drawn exactly once` |
| 4 | 模拟图 | `sim/sim_main.gif`、`sim/sim_main.png`（9 帧拼图）、`sim/log.json`；激励 `firmware/stimulus.json` | OK（模拟） |
| 5 | 外壳 | `enclosure.yaml`、`cad_out/{bottom,top}.{step,stl}`、`assembly.step`、`envelopes.step`、`check_report.{md,json}`、`preview_*.png` | OK |
| 6 | BOM + 两档成本 | `bom.csv`、`cost/{cost.md,summary.csv,cost_100.csv,cost_1000.csv}` | 缺价格 0；**单台超目标** |
| 7 | 合规清单 | `compliance.yaml`、`compliance_checklist.md` | OK（3 条，全部待核实） |
| 8 | 渲染图 | `render/render_answer-box_studio_{front,iso,iso-exploded,sheet}.png`、`render/render_answer-box_desk_iso.png`；屏幕替身 `render/epd_standin.stl`（由 `render/make_panel_stl.py` 生成） | OK；没画 PCB，所以没有 `kicad/`、未运行 `kicad_check.py` |
| 9 | 报告 | 本文件 | — |

实际运行的命令（`hardware-studio/` 下、`.venv` 激活）：

```bash
python .claude/skills/new-product/product.py new answer-box
python diagrams/wiring.py products/answer-box/pins.csv --out products/answer-box/out --subtitle "原型接线（未上真机）/ prototype wiring, not built"
python sim/run_firmware.py products/answer-box/firmware/main.py --display epaper --seconds 70 --seed 1 \
  --inputs products/answer-box/firmware/stimulus.json --speed 10 \
  --out products/answer-box/sim/sim_main.gif --out products/answer-box/sim/sim_main.png --log products/answer-box/sim/log.json
python cad/build_enclosure.py products/answer-box/enclosure.yaml --out products/answer-box/cad_out
python mfg/cost.py products/answer-box/bom.csv --qty 100 1000 --currency CNY --fx USD=6.7829 --out products/answer-box/cost
python .claude/skills/new-product/product.py compliance-yaml products/answer-box
python compliance/checklist.py --product products/answer-box/compliance.yaml --out products/answer-box/compliance_checklist.md
python products/answer-box/render/make_panel_stl.py
python render/render.py --part products/answer-box/cad_out/bottom.stl:#E9E4DA:matte \
  --part products/answer-box/cad_out/top.stl:#F4F1EA:matte:0,0,16 --part products/answer-box/render/epd_standin.stl:#CFCBC2:paper:0,0,8 \
  --views front,iso --exploded --exploded-views iso --out products/answer-box/render --name answer-box
python render/render.py （同上三个零件，不加位移）--scene desk --props book,pencil --views iso --out products/answer-box/render --name answer-box
```

模拟手算核对：激励里 INT1 脉冲在 3.0 / 3.3 / 6 / 9 / 12 / 15 / 18 s（清醒期）和 45 / 50 s（深睡后）。
3.3 s 落在 800 ms 冷却内被忽略；开机欢迎页算第 1 次更新（全刷），之后每第 5 次更新全刷 → 12 s 全刷，其余局刷；
18 s 后闲置 15 s 进深睡；45 s INT1 唤醒，深睡后控制器 RAM 丢失 → 首次全刷；50 s 局刷。
手算：全刷 3、局刷 6、刷新 3×2000 + 6×260 = 7560 ms；模拟摘要 `{'ssd1681#0': {'full': 3, 'partial': 6, 'refresh_ms': 7560}}`，boots 2，帧 9——一致。
刷新时间是模拟器默认值（GDEY0154D67 经销商页 2 s / 0.26 s，待核实）；局刷残影是示意，不是物理模型。

成本分项（1000 台，每台 ¥）：墨水屏模块 38.05（待核实）、外壳 MJF 13.9 g 26.45（待核实）、C3 模组 15.05（实查）、
电芯 13.21（估算）、LIS3DH 8.48（实查）、组装 10 分钟 4.75（估算）、PCB 2.77（待核实，按打样价折算偏高）、包装 2.08（估算）、其余合计约 4.5。

## 复用 / 临时补 / 回写

| 步骤 | 直接复用了什么 | 临时补了什么 | 是否回写进库（写到哪 / 为什么没回写） |
|---|---|---|---|
| 1 场景与简报 | `products/_template/brief.yaml`、`product.py new / check --step 1`、compliance 特征词表 | 无（¥99 的口径不明，写进 open_questions） | 不需要 |
| 2 选型 | `knowledge/` 的 mcu / display / input / power 选型表和器件页（ESP32-C3、SSD1681、LIS3DH、TP4056、XC6206、USB-C、DW01）；`mfg/prices/jlcpcb-parts.yaml` 实查价 | LIS3DH 寄存器位（从数据手册镜像 PDF 逐表读取，表 29–61）；1.54 寸模块/裸屏外形；402030 电芯尺寸（C 级）；引脚分配 | **已回写**：`knowledge/input/lis3dh.md` 新增"寄存器位"一节（12 行）；`knowledge/display/ssd1680-ssd1681.md` 新增 2 行模块/面板外形。电芯**未回写**：只有 C 级卖家页，按规则不能单独作为事实，留在本产品 `selection.md` |
| 3 开发板原型 | `diagrams/wiring.py`（一次通过）、模板的 CONFIG/验证状态写法 | 摇一摇固件模板（库里没有，evals c04 早已标为缺口） | **已回写**：`firmware/templates/shake.py`（自动探测 0x18/0x19 + WHO_AM_I、运动中断寄存器、INT1 边沿 → SHAKE + 冷却、深睡 INT1 唤醒、软件检测器）+ `firmware/tests/test_fw_shake.py`（7 项）；入口写进 `firmware/README.md`、`.claude/skills/firmware-sim/SKILL.md`、`.claude/skills/new-product/SKILL.md`。产品 `pins.csv`、`firmware/main.py` 只对本产品有效，留在产品目录 |
| 4 模拟 | `sim/run_firmware.py`、`epaper.SSD1681` 模拟驱动、stimulus `pins` 脉冲、深睡唤醒模型 | 发现模拟摘要的墨水屏刷新计数在深睡重启后被清零（只显示最后一次启动），与 SKILL"摘要和手算一致"的验收冲突 | **已回写**：`sim/mpsim/mp_epaper.py` 改为按面板 id 跨重启累加；`sim/tests/test_sim_displays.py` 加回归测试。放大字（8×8 字形 ×2/×3）只在产品 `main.py`，未抽成库函数（只有一个产品用） |
| 5 外壳 | `cad/build_enclosure.py` 全部模块（圆角壳、止口、卡扣、屏幕窗台阶、USB-C 开孔、电池仓、plain 支柱）、`cad/DFM.md` 第 10 节选 MJF | 产品 `enclosure.yaml`；调参 2 次（edge_radius 2.5→2.0 满足 split_z 允许范围；卡扣长 5.5→3.6 mm 避免顶到顶板）；MJF 不切片，克数用体积 13735 mm³ × 1.01 g/cm³ 手算 | 库代码够用，未改。PA12 密度只有搜索摘要（HP/Materialise 数据表未打开），**未回写** `cad/DFM.md`；建议 B 线让 `build_enclosure.py` 对 MJF/SLA 按体积 × 密度输出克数 |
| 6 BOM 与成本 | `mfg/cost.py`（`--currency CNY --fx`）、BOM 模板的加工费/包装行、11 条实查价、加工费与人工/包装估算条目 | 墨水屏模块价（搜索摘要）、电芯价（C 级零售价 → 估算）、汇率 | **已回写**：`mfg/prices/unverified.yaml` 加 `lcsc:C5374685`；`mfg/prices/estimates.yaml` 加 `est:lipo-402030-200mah`；`mfg/README.md`、`mfg/pricing.md` 条目表更新。汇率只写在本报告（2 个月前的中间价，待核实） |
| 7 合规 | `product.py compliance-yaml`、`compliance/checklist.py`、`requirements.yaml` 52 条 | 用 `--wireless wifi,ble --not-connected` 对比"射频算不算无线"（多出 CN-01、CN-02） | 未回写：库里 UN 38.3 运输条目只挂在 US（其 notes 自己写"实际上所有市场都适用"），CN 清单不出现；补 CN 条目需要 S 级法规原文，本会话打不开，列入待核实交 E 线 |
| 8 小批量与出图 | `render/render.py`（studio / desk、爆炸图、自动加标注）、`mfg/production-routes.md`（选"模组 + 自画底板"） | 屏幕替身 STL（`render/make_panel_stl.py`，48×33×3 盒子），让窗口里有屏 | 未回写：只对本产品有意义。没画 KiCad 板（超出本次范围），`kicad_check.py` 未运行 |

## 待核实和风险

**价格（全部 2026-11-01 记录，下单前复核）**
- 墨水屏模块 C5374685 $5.50@100+：只有搜索摘要，摘要还显示缺货；同类 C359939 摘要 $10.65 起——实际可能更贵。
- MJF 外壳 $0.275/g（JLC3DP 调价公告摘要）；13.9 g 是估算；不含后处理和起步价。
- 电芯 $1.91 只是 C 级零售价；组装 10 分钟 × $0.07/分钟、包装 $0.30 是假设值（`est:assembly-labor` 内部用假设汇率 7.2，与本报告 6.7829 不一致）。
- PCB 按 5 片打样价 $0.40/片折算，批量价未查到。

**离 ¥99 的差距怎么补（推论/估算，未验证）**
1. 墨水屏模块 → 裸屏 + 板上升压驱动：最大杠杆（模块 ¥38），但裸屏价和升压外围元件值都未查到；
2. 外壳 ¥26：1000 台按 `cad/DFM.md` 第 10 节应和快速模注塑比价；MJF 想减薄受止口限制（壁厚 ≥ 2.3）；
3. 主控 ¥15：产品不用无线，射频是浪费；换无射频 MCU 要先补知识库页和模拟支持（库里只有 ESP32 系列，本次没做）；
4. 加速度计 ¥8.5：更便宜的加速度计或振动开关（库里没有页面）。
在拿到真实报价前**不能承诺 ¥99**。

**硬件/固件（未运行）**
- 墨水屏真机驱动：`main.py` 用模拟器自定义 API `epaper.SSD1681`，真机要同名方法的 SSD1681 MicroPython 驱动——库里没有，需真机验证，本次不做。
- `esp32.wake_on_gpio` 在 MicroPython ESP32-C3 端口是否可用：待核实；阈值 1.6 g、冷却 800 ms、ODR 50 Hz 未在真机调。
- 中文答案需要中文点阵字库（`framebuf.text` 只有 8×8 ASCII），模拟图暂用英文。
- 包络估算：模块厚 3.0（不装排针）、C3 模组高 3.0、PCB 46×30×1.0、可视区居中——首件对位；USB-C 插座/插头尺寸是库默认估算值。
- 卡扣根部应变估算 2.3%，PA12 许用应变库里未查到，可能偏紧。
- XC6206 压差：电池低于约 3.55 V 后 3V3 下降（C3 下限 3.0 V）；没有电量检测脚，低电量行为未设计。
- 深睡电流估算（器件页典型值相加，未实测）：C3 4.8 + LIS3DH 50 Hz 低功耗 6 + XC6206 1 + 墨水屏深睡 1 + TP4056 BAT 漏电 < 2 ≈ 15 μA → 200 mAh 约 1.5 年（只算睡眠）；C3 不开射频时的清醒电流库里未查到，"≥ 1 个月"续航目标没估算完。

**问检测机构 / 供应商**
1. 主控模组带 Wi-Fi/BLE 射频但固件永不开启：国内是否仍需 SRRC 型号核准或无线评估（CN-01/CN-02）？
2. 本产品是否在 CCC 目录内（CN-03）；内置 200 mAh 电芯是否要求电池 CCC（GB 31241，CN-05）；RoHS 标识（CN-07）。
3. 快递/空运含锂电整机：UN 38.3 报告和包装要求（库里 CN 清单没有此条）。
4. 电芯供应商：规格书（尺寸、寿命末期厚度、PCM 阈值）、UN 38.3 报告、批量价。

**网络限制（本会话）**：lcsc.com、jlcpcb.com、waveshare.com、eemb.com、evelta.com、botland.com.pl 打不开（DNS 不可解析/代理拦截），只能用 GitHub、jlcparts 镜像和搜索摘要；墨水屏模块和电芯不在 jlcparts 镜像里。

## 下一步

1. 先核实两项大头价格（墨水屏模块/裸屏、外壳 MJF 与快速模报价），重跑 `cost.py` 判断能否进 ¥99；
2. 写真机 SSD1681 驱动（与模拟器同名方法），用开发板 + 模块验证摇一摇阈值、刷新时间、深睡电流；
3. 画 KiCad 底板（C3 模组 + TP4056 + XC6206 + LIS3DH + USB-C），跑 `mfg/kicad_check.py`；
4. 首件 MJF 打样，量包络、调配合间隙和卡扣；
5. 生成中文答案字库，重出模拟图。

## 库检查结果（2026-11-01 实际运行）

- `python evals/run.py --label answer-box-2026-11-01 --compare evals/results/baseline-2026-11-01.json`：总分 **15.51 → 16.51**（c04【缺口】摇一摇模板 0 → 1.00，其余不变；g02 来源合规 684/710，新增行全部合格）。
- `python knowledge/check_sources.py`：25 个文件、529 行，0 行不合格。抽查新补的行：LIS3DH 寄存器位是用 pdftotext 从镜像 PDF（sha256 前缀 852bfcf1a993f04c）提取后逐表核对的；Waveshare 外形两行只有搜索摘要，页面打不开，未核对。
- `python mfg/cost.py --check-prices`：38 条（实查 25、待核实 9、估算 4）通过。
- `python -m pytest -q`（全库）：**423 passed, 1 skipped**。
- `python .claude/skills/new-product/product.py check products/answer-box`：**27/28 通过**，唯一 FAIL 是"6. 最大数量档单台 ≤ brief 目标 99（1000 台 ¥115.43，实查 23%）"，原因见上"离 ¥99 的差距"。（`product.py check answer-box` 不带 `products/` 前缀会报"没有目录"，要写完整路径。）
