# b01 · B 外壳 · 带 USB-C 和电池仓的外壳：干涉为 0、插头能插到底

**需求**：随身小设备，软包电芯 40×30×6 mm 在底部，PCB 架在支柱上，USB-C 从左侧（-x 面）出线，顶面一个屏幕窗和一个按键。

**任务**：用 enclosure-design skill，把 `enclosure.yaml`（本目录，已按"由内而外"排好层叠）生成外壳：
`python cad/build_enclosure.py evals/tasks/b01_usbc_battery_enclosure/enclosure.yaml --out <目录> --no-slice --no-preview`，
确认干涉为 0、USB 插头能插到底、外形尺寸正确。

**判分**（工具报告 + 独立几何探针，探针用 trimesh 直接读导出的 STL，不用 cad 工具的检查代码）：
- 退出码 0 且报告 `ok`、`interference_zero`、`usb_plug_fully_inserts` 为真（0.3）；
- 下壳 + 上壳合并包围盒 = 70 × 45 × 22 mm（±0.1）（0.2）——由参数直接得出；
- USB-C 开孔：在侧壁厚度范围内、插头金属壳截面（8.3 × 2.5 mm，USB Type-C 规范插头外形，评分人取值）内的
  采样点全部不在壳体实体里（0.2）；对照点（同一侧壁、离开孔 15 mm 处）在实体里，证明探针有效（0.1）；
- 电池仓：膨胀后电芯（40×30×6.6 mm，位置按参数手算）范围内的采样点全部不在壳体实体里（0.2）。
