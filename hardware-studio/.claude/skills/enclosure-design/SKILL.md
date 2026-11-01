---
name: enclosure-design
description: 为小型电子产品设计 3D 打印 / 注塑外壳：由内而外先放元器件包络，再用 cad/ 的参数化模块（圆角壳、止口、螺丝柱、屏幕窗、按键、USB-C 开孔、卡扣、电池仓）生成外壳，导出 STEP/STL、出预览图，并检查干涉、壁厚、打印平台、USB 插头能否插到底、能否切片。Use when a product needs an enclosure model, when editing products/<name>/enclosure.yaml, or when checking an enclosure's manufacturability (DFM) for FDM, SLA, MJF or injection molding.
---

# 外壳设计（enclosure-design）

## 什么时候用

- 新产品要外壳模型（给打样、渲染、算成本）；
- 改 `products/<产品名>/enclosure.yaml` 之后重新生成和检查；
- 判断某个外壳能不能用某种工艺做、该换什么工艺（看 `cad/DFM.md`）。

不适用：PCB 布局（KiCad）、正式渲染图（用 `render/` 的 product-render skill，输入就是这里导出的 STL/STEP）。

## 准备

```bash
cd hardware-studio && . .venv/bin/activate
pip install -r requirements.txt            # 含 cad/requirements.txt（rtree）
# 可选：切片检查
sudo apt-get install -y --no-install-recommends prusa-slicer
```

参数格式、坐标约定、输出文件都在 `cad/README.md`。工艺规则和来源在 `cad/DFM.md`。

## 步骤（由内而外）

1. **列元器件包络**。从 `knowledge/` 的器件页和所用模块的数据手册 / 卖家页取外形（PCB、屏幕模组、电池、
   轻触开关、USB-C 插座、扬声器……）。尺寸要有来源；量的写"实测"，没有的写"估算"。
2. **摆放元器件**。在 `enclosure.yaml` 的 `components:` 里写成盒子（`size`、`center`、`z`），先排好
   层叠高度：底板内表面（= wall）→ 电池（膨胀后）→ PCB 支柱 → PCB → 器件 → 屏幕 → 顶板内表面。
   电池用 `battery:`（自动加膨胀余量和走线口），USB-C 用 `usb_c:`（自动生成插座和插头包络）。
3. **定外壳**。`shell.size` = 元器件总包络 + 2 × 壁厚 + 间隙；按工艺选 `process`（壁厚、间隙默认值随工艺）。
   - 分模面 `split_z` 尽量取 USB-C 插座中心高度，避免开孔在分模面处留下薄片；
   - FDM 止口：`lip.thickness`、`lip.clearance` 和上壳剩余壁三者都要 ≥ 最小壁厚（FDM 1.2 mm → 壁厚 ≥ 2.7 mm），否则报告会警告；
   - 两半壳的螺丝用 `fasteners:`（上壳倒挂螺丝柱 + 下壳过孔柱 + 沉头孔），柱子离止口环至少留 0.3 mm；
   - 屏幕窗 `screen_windows:` 的台阶按玻璃 / 模组外形，压边厚度 = 壁厚 - 台阶深度；
   - 按键选 `type: hole`（会生成按键帽零件，用 `plunger_length` 让压杆离开关顶面约 0.5 mm）或 `type: cantilever`；
   - 卡扣 `snaps:` 放在侧壁上、避开 USB 和螺丝柱；卡钩要高于止口让位槽。
4. **生成**：

   ```bash
   python cad/build_enclosure.py products/<产品名>/enclosure.yaml --out products/<产品名>/cad_out
   ```

5. **读报告** `cad_out/check_report.md`，不通过就回到第 2–3 步改参数，重新生成。

## 在 Python 里直接用模块

```python
import sys; sys.path.insert(0, "cad")
from hwcad.shell import ShellSpec, make_shell
from hwcad.frames import face_plane
from hwcad.usbc import usbc_cutout
from build123d import Location
spec = ShellSpec(length=80, width=50, height=25, wall=2.7, split_z=10, lip_thickness=1.2, lip_clearance=0.3)
halves = make_shell(spec)
usb = usbc_cutout(spec.wall, recess=1.0)
loc = Location(face_plane(spec.size, "-x", u=0, v=10))
halves["lower"] = halves["lower"] - usb.cut.moved(loc)
```

工具都能单独用：

```bash
python cad/tools/measure.py a.step b.step --min-wall 1.2 --bed 250 210 220
python cad/tools/export.py a.step --out out/ --formats stl
python cad/tools/preview.py a.stl b.stl --out p.png --explode 20
python cad/tools/slice_check.py out/bottom.stl --json r.json          # 上壳加 --rotate-x 180
```

## 怎么检查结果（报告里的每一项）

| 检查 | 通过标准 | 不通过怎么改 |
|---|---|---|
| 几何有效 | 所有零件 `valid = true` | 通常是特征重叠在圆角边上，挪开或减小圆角 |
| 干涉 | 零件 + 包络两两干涉体积 = 0（报告列出每一对） | 按列出的对挪位置或改尺寸；确实允许接触 / 重叠的写进 `ignore_pairs` 并说明理由 |
| USB 插头插到底 | `usb_plug_fully_inserts = true` | 插座缩进（recess > 0）时开孔要让开插头外壳；或把插座往外挪；用实测的插头外壳尺寸 |
| 壁厚 | 参数警告为 0；抽样"低于最小壁厚比例"接近 0，最薄点只出现在卡钩尖、斜切边缘这类本该薄的地方 | 加壁厚、减台阶深度、减卡槽深度、加大过孔柱 |
| 打印平台 | `fits_printer_bed = true` | 换平台或把零件拆分 |
| 切片 | 每个零件 `ok = true`，记下耗材 g 和时间 | 切不了通常是网格问题或零件超出平台 |
| 应变 | 卡扣 / 悬臂按键的 `root_strain_est` < 材料许用应变（自己查材料数据填 `allowable_strain`） | 加长梁、减薄梁、减小卡钩 |

注意：

- 默认值里标"估算 / 待核实"的（USB-C 插座和插头外壳尺寸、电池膨胀 10%、FDM 配合间隙 0.3 mm 等）在具体项目里
  要换成数据手册或实测值；首件打样后按实测修正间隙。
- 切片时间是 PrusaSlicer 默认配置的估算，不代表具体打印机。
- 预览 PNG 只用于检查，图上标"预览"，不是渲染图；正式出图交给 `render/`。
- 批量多大换工艺看 `cad/DFM.md` 第 10 节（估算区间，要拿报价复核）。
