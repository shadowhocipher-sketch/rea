# 第三方代码、数据、文档与许可证

由统筹汇总各工作线的记录。详细表格见 `cad/LICENSES-THIRD-PARTY.md`、`mfg/LICENSES-THIRD-PARTY.md`、`render/README.md`。
版本是 2026-11-01 在 `hardware-studio/.venv` 中的版本。

## 红线执行情况

- 可复用的固件和工具里**没有复制任何 GPL/LGPL/AGPL 代码**。
- GPL/AGPL 软件只作为**外部命令行程序**调用，不复制、不链接、不随库分发：KiCad（GPL-3.0+）、PrusaSlicer（AGPL-3.0）、git（GPL-2.0）。
- **没有使用 Blender bpy**：Blender 官方认为调用 bpy API 的脚本属于 GPL 派生作品。渲染器是本库自己用 numpy 写的。
- **需要注意的一处**：build123d（Apache-2.0）依赖 OCP，OCP 内含 OpenCASCADE 几何内核，许可证是 LGPL-2.1 附 OCCT 例外（**待核实**：需按 OCCT 官方许可说明核对）。本库只通过 Python 动态调用它，没有复制或修改它的代码。B-rep 建模和 STEP 导出都依赖这个内核；如果你的红线也排除 LGPL 的动态依赖，需要另行决定。

## Python 依赖

| 名称 | 版本 | 许可证 | 使用方 |
|---|---|---|---|
| build123d | 0.13.0 | Apache-2.0 | cad、render（读 STEP） |
| cadquery-ocp-novtk（OCP / OpenCASCADE） | 8.0.1.1.0 | 绑定 Apache-2.0；内核 LGPL-2.1 附例外（待核实） | build123d 的传递依赖 |
| numpy | 2.5.4 | BSD-3-Clause | 全部 |
| scipy | 1.18.1 | BSD-3-Clause | trimesh 的传递依赖 |
| matplotlib | 3.11.2 | Matplotlib License（PSF 风格） | cad 预览、render 英文后备字体 |
| pillow | 13.0.0 | MIT-CMU（HPND） | sim、render、diagrams |
| trimesh | 5.2.0 | MIT | cad、render |
| rtree | 1.4.1 | MIT | cad（射线求交） |
| PyYAML | 6.0.3 | MIT | 全部 |
| imageio | 2.38.1 | BSD-2-Clause | 公共依赖 |
| pytest | 9.2.0 | MIT | 测试 |

## 外部程序（不分发）

| 名称 | 版本 | 许可证 | 用途 |
|---|---|---|---|
| PrusaSlicer | 2.7.2（Ubuntu apt） | AGPL-3.0 | `cad/tools/slice_check.py` 调用 |
| KiCad kicad-cli | 9.0.9（官方 Docker 镜像 `kicad/kicad:9.0`） | GPL-3.0+ | `mfg/kicad_check.py` 调用 |
| git | 系统自带 | GPL-2.0 | 拉取 jlcparts 数据和乐鑫文档源码 |

## 数据、字体和文档

| 名称 | 许可证 | 怎么用 |
|---|---|---|
| font8x8（Daniel Hepper，源自公有领域 VGA 字体），https://github.com/dhepper/font8x8 | 公有领域 | 转写进 `sim/mpsim/font8x8.py`，用于 framebuf.text |
| Noto Sans CJK（系统字体包 fonts-noto-cjk） | SIL OFL 1.1 | 运行时读取，用来写图上的中文标注；**没有提交字体文件** |
| jlcparts（yaqwsx/jlcparts）的数据导出 | 代码 MIT；数据来自 JLCPCB，数据使用条款**待核实** | 只读，`mfg/prices/` 里只存 25 条价格 |
| 乐鑫硬件设计指南（espressif/esp-hardware-design-guidelines） | 文档 CC BY-SA 4.0 | `mfg/esp32s3-min-system.md` 是摘要和翻译，页内已署名，并声明该页按 CC BY-SA 4.0 发布 |
| MicroPython 文档和源码、micropython-lib ssd1306、st7789py_mpy | MIT | 只作为 API 行为参考，模拟器是重新实现的，没有复制代码 |

## 知识库 `knowledge/` 引用的资料

知识库里**没有复制第三方代码**；数据手册 PDF 只在临时目录里读取，没有放进仓库。

| 名称（固定到的提交） | 许可证 | 怎么用 |
|---|---|---|
| espressif/esp-hardware-design-guidelines @a727293 | 文档 CC BY-SA 4.0，代码 Apache-2.0 | 中文转述设计要点，附链接署名；转述段落如被视为改编作品，适用相同方式共享 |
| espressif/esp-idf @d445e94 | Apache-2.0 | 引用文档、`soc_caps.h`、`io_mux_reg.h` 里的数值 |
| espressif/esp-iot-solution @d2d935d | Apache-2.0 | 引用 button 组件的默认消抖参数 |
| STMicroelectronics/lis3dh-pid @8c0588b | BSD-3-Clause | 核对器件 ID、I2C 地址常量 |
| ZinggJM/GxEPD2 @de82887 | **GPL-3.0** | 只把两个墨水屏刷新时间常量的**数值**当作 C 级线索引用（标"待核实"），没有复制任何代码 |
| 原厂数据手册、USB Type-C 规范 | 版权归原厂 / USB 3.0 Promoter Group | 只引用参数并附链接，没有再分发；经第三方 GitHub 镜像读取的已在各页注明 |
