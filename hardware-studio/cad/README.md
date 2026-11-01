# cad/ —— 参数化外壳模块与工具（B 线）

通用、不写死任何产品尺寸。具体产品的外壳参数放在 `products/<产品名>/enclosure.yaml`，
用 `cad/build_enclosure.py` 生成零件、预览和检查报告。

```bash
. .venv/bin/activate
python cad/build_enclosure.py cad/examples/generic_box.yaml --out cad/examples/out
python -m pytest cad/tests -q
```

## 目录

| 路径 | 内容 |
|---|---|
| `hwcad/process.py` | 按工艺（fdm / sla / mjf / im）分组的壁厚、间隙、公差常量；打印平台；螺丝比例 |
| `hwcad/frames.py` | 坐标约定、面上的局部坐标系、`Feature`（加料 + 去料 + 检查包络） |
| `hwcad/shell.py` | 圆角盒、抽壳、按 Z 分模、止口 |
| `hwcad/bosses.py` | 自攻螺丝柱、热熔螺母柱、过孔柱、沉头孔 |
| `hwcad/windows.py` | 屏幕窗（矩形 / 圆形 + 内侧台阶） |
| `hwcad/buttons.py` | 按键孔 + 导向筒 + 按键帽；一体式悬臂按键；悬臂应变公式 |
| `hwcad/usbc.py` | USB-C 开孔（按插座缩进量选开孔尺寸）+ 插座 / 插头包络 |
| `hwcad/snaps.py` | 悬臂卡扣 + 卡槽，应变估算 |
| `hwcad/battery.py` | 电池仓围框 + 膨胀余量 + 走线口 |
| `hwcad/enclosure.py` | 从参数 dict 拼装整个外壳 |
| `tools/measure.py` | 包围盒、体积、干涉体积、最小壁厚抽样、打印平台检查 |
| `tools/export.py` | 导出 STEP / STL / 装配体 |
| `tools/preview.py` | matplotlib 快速预览 PNG（不是渲染图） |
| `tools/slice_check.py` | 调 PrusaSlicer 命令行切片：能否切片、耗材、时间 |
| `build_enclosure.py` | 入口：YAML → STEP/STL/PNG/检查报告 |
| `DFM.md` | 四种工艺的设计规则和批量切换点（带来源） |
| `examples/generic_box.yaml` | 通用示例（不是任何产品）；`examples/out/` 是它的实际输出 |

## 坐标约定

* 单位 **mm**，角度 **°**。
* 外壳外形：X 方向 `length`，Y 方向 `width`，Z 方向 `height`；X、Y 以外形中心为 0；
  **Z = 0 是底面外表面**，Z = height 是顶面外表面。
* 分模面垂直于 Z（`split_z`）。`style: top_bottom` 时两半叫 `bottom` / `top`；
  `style: front_back` 时叫 `back` / `front`（手持设备把 +Z 当"前"即屏幕面）。
* 导出的 STEP/STL 都在**装配位置**（全局坐标）。切片时上壳会自动翻转 180° 打印。
* 面上特征的位置 `u`、`v` 用全局坐标：

  | face | u | v |
  |---|---|---|
  | `top` / `bottom` | 全局 x | 全局 y |
  | `+x` / `-x` | 全局 y | 全局 z |
  | `+y` / `-y` | 全局 x | 全局 z |

  侧面特征的局部 +X：`+x`→+Y，`-x`→-Y，`+y`→-X，`-y`→+X；局部 +Y 一律朝上（+Z）。
  悬臂按键的根部在局部 -X 一端。

## 参数文件格式 `enclosure.yaml`

除注明"必填"外都有默认值；默认值随 `process` 变化的写作"工艺默认"（见 `hwcad/process.py`）。

```yaml
name: my-product              # 外壳名，出现在报告里
process: fdm                  # fdm | sla | mjf | im（别名 dlp→sla，injection→im）
printer: prusa_mk4s           # 可选：prusa_mk4s | bambu_a1_mini | bambu_p1s | {name: x, bed: [X, Y, Z]}

shell:                        # 必填
  size: [L, W, H]             # 必填，外形 mm
  wall: 2.0                   # 壁厚，工艺默认 default_wall
  corner_radius: 4            # 竖直棱外圆角
  edge_radius: 1              # 顶 / 底面棱外圆角（≤ corner_radius）
  split_z: H/2                # 分模面高度（底面外表面量起）
  style: top_bottom           # top_bottom | front_back
  lip:                        # 止口；height: 0 表示平口对接
    height: 2.0
    thickness: 0.4*wall       # 占壁厚内侧
    clearance: 工艺默认 fit_clearance

fasteners:                    # 两半壳之间的螺丝：上壳倒挂螺丝柱 + 下壳过孔柱 + 底面沉头孔
  - x: 0                      # 必填
    y: 0                      # 必填
    kind: self_tap            # self_tap | heat_insert
    thread: M3
    meet_z: split_z           # 两柱相接高度
    gap: 0.2                  # 两柱之间留缝，保证壳口先贴合
    counterbore_depth: 2.0    # 0 = 不做沉头
    # 可选：hole_factor, outer_factor（自攻）；insert_hole_d, insert_length, min_wall（热熔）；
    #       clearance_d, head_d, post_outer_d

standoffs:                    # 单独的柱子（例如 PCB 支柱）
  - {x: 0, y: 0, part: lower, kind: self_tap, thread: M2, height: 4}
    # part: lower（从底板往上）| upper（从顶板往下）
    # kind: self_tap | heat_insert | plain（plain 需 outer_d，可选 hole_d）

screen_windows:
  - face: top                 # 必填
    u: 0
    v: 0
    shape: rect               # rect | circle（circle 时 width 为直径）
    width: 30                 # 必填，可视区
    height: 15
    corner_radius: 1
    margin: 0                 # 开口比可视区每边大多少
    step:                     # 可选：内侧台阶（压玻璃 / 模组边框）
      width: 36               # 玻璃 / 模组外形
      height: 22
      depth: 0.8              # 从内表面往外挖的深度；压边剩余 = wall - depth
      clearance: 工艺默认 fit_clearance
      corner_radius: 0.5      # 尖角模组要求 r ≤ 约 3.4 × clearance

buttons:
  - name: btn_a
    face: top
    u: 0
    v: 0
    type: hole                # hole：圆孔 + 可选导向筒 + 按键帽零件
    diameter: 6               # 帽身直径
    clearance: 工艺默认 fit_clearance
    sleeve_length: 0          # 导向筒长度
    sleeve_wall: 工艺默认 min_wall
    cap: true                 # 是否生成按键帽零件 cap_<name>
    protrusion: 1.0           # 帽露出外表面高度
    flange_t: 工艺默认 min_wall
    cap_gap: 0.3
    plunger_length: 1.0       # 压杆长度（去按轻触开关）
  - name: btn_b
    face: top
    type: cantilever          # 一体式悬臂按键
    length: 12
    width: 7
    slot: 0.8                 # U 形槽宽
    tongue_thickness: null    # 舌片减薄后的厚度；null = 壁厚
    nub_d: 3
    nub_height: 1.5
    travel: 0.5               # 按压行程，用于应变估算
    allowable_strain: null    # 材料许用应变（0.02 = 2%），给出时超出会警告

usb_c:
  - name: usb
    face: -x                  # 必填（侧面）
    u: 0                      # 插座中心
    v: 5
    recess: 0.5               # 插座前端面到外表面距离（正 = 缩进）；决定开孔按插头外壳还是插座外形
    receptacle: [8.94, 3.26, 7.35]   # 插座 宽 高 长（估算默认值，换成数据手册值）
    overmold: [12.4, 6.5, 20]        # 插头外壳 宽 高 长（估算默认值，量自己的线）
    clearance: 工艺默认 fit_clearance
    mate_gap: 0.0

snaps:                        # 下壳立梁、上壳内壁挖卡槽
  - name: snap_a
    face: +y                  # 必填：+x | -x | +y | -y
    u: 0                      # 沿墙位置（全局坐标）
    length: 10
    thickness: 1.2
    width: 5
    undercut: 0.8             # 卡钩凸出量
    gap: 0.2                  # 梁与上壳内壁的间隙；挠度 = undercut - gap
    flat: 0.6
    lead_angle: 30
    clearance: 0.2
    root_height: 3.0
    q: 1.0                    # BASF 挠度放大系数
    allowable_strain: null

battery:                      # 可选，一个
  x: 0
  y: 0
  cell: [L, W, T]             # 必填，电芯标称尺寸
  swell: 0.10                 # 厚度膨胀余量（估算）
  xy_clearance: 0.5
  rib_thickness: 工艺默认 min_wall
  rib_height: 3.0
  wire_side: +x               # +x | -x | +y | -y
  wire_slot_width: 4.0
  top_gap: 0.3

components:                   # 元器件包络（盒子），参与干涉检查
  - {name: pcb, size: [X, Y, Z], center: [x, y], z: 底面高度（默认 = wall）}

ignore_pairs:                 # 可选：明确允许重叠的名称对，例如 [[pcb, usb_receptacle]]
  - [a, b]
```

## 输出与检查

`build_enclosure.py <yaml> --out <dir> [--no-slice] [--no-preview] [--wall-samples N]` 写出：

| 文件 | 内容 |
|---|---|
| `<零件>.step` / `.stl` | 每个零件（装配位置） |
| `assembly.step` | 装配体 |
| `envelopes.step` | 检查用包络（元器件、膨胀后电池、USB 插座与插头外壳） |
| `preview_assembly.png` / `preview_exploded.png` | 快速预览，标"预览 / Preview (not a render)" |
| `check_report.json` / `.md` | 检查报告 |

总结论 `ok = true` 需要同时满足：几何有效；零件与包络两两干涉体积为 0（`ignore_pairs` 除外）；
USB 插头外壳包络与外壳不干涉（插头能插到底）；零件能放上打印平台；参数校验没有警告
（壁厚、止口、压边、卡槽剩余壁厚 ≥ 工艺最小壁厚，应变不超许用值等）。
最小壁厚抽样只报告分位数和"低于最小壁厚的样本比例"，并列出最薄点坐标，由人判断
（卡钩尖、斜切边缘本来就趋近 0）。

退出码：0 通过，1 有检查未通过，2 参数错误。

## 依赖

公共依赖见顶层 `requirements.txt`；本目录额外依赖见 `cad/requirements.txt`；许可证见 `cad/LICENSES-THIRD-PARTY.md`。
切片检查需要外部命令行 `prusa-slicer`（AGPL-3.0，仅作为外部程序调用）：
`sudo apt-get install -y --no-install-recommends prusa-slicer`。没装时切片检查返回清楚的提示，其余功能不受影响。
