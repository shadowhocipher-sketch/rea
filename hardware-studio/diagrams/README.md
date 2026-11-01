# diagrams/ — 接线图

从 `pins.csv`（格式见 `CONVENTIONS.md` 第 2 条）自动画接线图，输出 `wiring_<名>.svg` 和
`wiring_<名>.png`，并核对图里画的线和 `pins.csv` 一一对应。

## 用法

```bash
python diagrams/wiring.py products/<产品名>/pins.csv --out products/<产品名>/out
python diagrams/wiring.py pins.csv --out out --name demo --subtitle "替身数据 / stand-in data"
python diagrams/check_wiring.py pins.csv out/wiring_demo.svg      # 单独核对，0=通过 1=不一致
```

`wiring.py` 画完会自动核对，并检查排版是否重叠；退出码 0 = 全部通过，1 = 核对或排版有问题
（文件照样写出），2 = 输入有错。

Python 调用：

```python
import sys; sys.path.insert(0, "hardware-studio/diagrams")
from wirediag import draw_wiring, check_files
svg, png, layout, layout_problems = draw_wiring("pins.csv", "out", name="demo")
print(check_files("pins.csv", svg).report())
```

## 画法

- 每个部件一个方框，引脚列在框边；连线最多的部件（通常是 MCU）放中间，其他部件放左右两列，
  引脚朝向中间。彼此直接相连（不经过中间部件）的部件放同一列。
- 连线按 net 着色：电源红色系、地黑色系、信号每个 net 一种颜色；电源/地线更粗。
- 每个引脚旁边标 net 名；图下方是图例和接线表（序号、从、到、网络、类型、备注）。
- 正交走线：每根需要拐弯的线有自己的竖直走线道，不同 net 的线不会叠在一起；
  `check_layout` 会检查方框、标签、连线是否重叠。
- 同一个引脚连多根线（例如 GND、I2C 总线）时，线从同一个点分出。中间部件的引脚如果两边都有线，
  会在左右两边各画一次。

## pins.csv 读入规则

- 表头必须含 `from_part,from_pin,to_part,to_pin,net,kind,note`；`kind` 取 `power`/`ground`/`signal`；
- 以 `#` 开头的行是注释；表格里的序号是数据行号（不算表头和注释）；
- 会拒绝：空字段、未知 kind、一根线两端是同一个引脚、同一引脚出现在两个 net、同一 net 两种 kind、重复行。

## 核对（不多不少）

SVG 里每根线是一个 `<polyline class="wire">`，带 `data-from="MCU.GPIO8" data-to="OLED.SDA"`、
拆开的 `data-from-part/-pin`、`data-to-part/-pin`、`data-net`、`data-kind`、`data-row`；
每个引脚是 `<g class="pin" data-part data-pin>` 里的一个圆点。`check_wiring.py`：

1. 把 pins.csv 的每一行和 SVG 里的每根线按 (两端、net、kind) 做多重集比较，报告 MISSING / EXTRA；
2. 检查每根线的起点和终点确实落在它声称连接的两个引脚圆点上（GEOMETRY）。

PNG 和 SVG 由同一个布局对象画出，核对 SVG 即核对了这张图的内容。

## 示例

- `examples/out/wiring_desk-creature-standin.*`：来自 `products/desk-creature-standin/pins.csv`，**替身数据，不是真实引脚**；
- `examples/complex/pins.csv` → `examples/out/wiring_complex-example.*`：虚构的 8 个部件、24 根线，用来测排版。

## 测试

`pytest diagrams/tests`：两张示例图核对通过、排版无重叠；删掉一根线、多画一根线、线端点移走时核对失败；
40 个随机网表排版无重叠；坏 CSV 被拒绝。

## 依赖

只用 Pillow 和标准库；中文字体查找复用 `render/prender/fonts.py`（安装见 `render/README.md`）。
没有中文字体时 PNG 里的中文会缺字，命令行会提示；SVG 不受影响（浏览器用自己的字体）。
