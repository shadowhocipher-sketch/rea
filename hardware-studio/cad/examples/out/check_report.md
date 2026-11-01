# 外壳检查报告：generic-box-example

- 工艺：fdm；打印机：prusa_mk4s (250.0, 210.0, 220.0)
- 总结论：**通过**（生成用时 7.6 s）

## 检查项

| 项目 | 结果 |
|---|---|
| 几何有效 | True |
| 干涉体积为 0（零件 + 包络体两两） | True（总 0.0 mm³） |
| USB 插头能插到底 | True |
| 能放上打印平台 | True |
| 参数警告数 | 0 |

## 零件

| 零件 | 尺寸 X×Y×Z (mm) | 体积 (mm³) | 壁厚抽样 p01 / 中位 (mm) | 低于最小壁厚比例 |
|---|---|---|---|---|
| bottom | 96.0×60.0×24.9 | 28395 | 1.199 / 2.7 | 0.1% |
| top | 96.0×60.0×15.1 | 23355 | 1.2 / 2.7 | 0.0% |
| cap_btn_a | 8.0×8.0×12.2 | 317 | 1.2 / 5.993 | 0.0% |

壁厚是抽样估计（射线法），卡钩尖、圆角边缘等本身趋近 0 的几何会计入比例，最薄点坐标见 JSON。

## 切片（PrusaSlicer 命令行，时间为默认配置估算）

| 零件 | 能否切片 | 耗材 (g, 估算) | 时间 |
|---|---|---|---|
| bottom | True | 27.8 | 2h 47m 28s |
| top | True | 22.84 | 2h 5m 50s |
| cap_btn_a | True | 0.41 | 5m 6s |

## 输出文件

- bottom: bottom.step, bottom.stl
- top: top.step, top.stl
- cap_btn_a: cap_btn_a.step, cap_btn_a.stl
- assembly: assembly.step
- envelopes: envelopes.step
- preview: preview_assembly.png, preview_exploded.png
