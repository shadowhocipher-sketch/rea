# 外壳检查报告：answer-box

- 工艺：mjf；打印机：jlc3dp-mjf-assumed (380.0, 284.0, 380.0)
- 总结论：**通过**（生成用时 4.7 s）

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
| bottom | 58.0×42.0×13.5 | 9511 | 0.999 / 2.4 | 0.1% |
| top | 58.0×42.0×6.7 | 4223 | 1.099 / 2.4 | 0.3% |

壁厚是抽样估计（射线法），卡钩尖、圆角边缘等本身趋近 0 的几何会计入比例，最薄点坐标见 JSON。

## 输出文件

- bottom: bottom.step, bottom.stl
- top: top.step, top.stl
- assembly: assembly.step
- envelopes: envelopes.step
- preview: preview_assembly.png, preview_exploded.png
