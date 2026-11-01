---
name: product-render
description: 出产品图：从 STEP/STL 渲染多角度、爆炸图和桌面场景的产品渲染图（render_*.png，标"渲染图 / Render"），以及从 pins.csv 自动画接线图（wiring_*.svg/png）并核对每根线不多不少。Use when a product needs rendered images of its enclosure/parts (studio or desk scene, exploded views, size reference props), or a wiring diagram drawn and verified from products/<name>/pins.csv.
---

# 出图（product-render）

## 什么时候用

- 外壳模型（`cad/` 导出的 STL/STEP）已经有了，要给人看产品长什么样：多角度图、爆炸图、桌面场景图；
- 接线表 `products/<产品名>/pins.csv` 写好或改过，要一张接线图，并确认图和表一致。

不适用：外壳建模本身（用 enclosure-design）、PCB 原理图/布板（KiCad）、屏幕内容预览（用 firmware-sim 的模拟器）。

## 红线

- **渲染图不冒充实拍。** 文件名必须 `render_` 开头，图上必须有"渲染图 / Render"标注（工具自动加，
  不能去掉；`--label` 只能改文字不能为空）。对外使用时不能裁掉标注，不能写"实拍""实物图"。
- 不用 Blender/bpy 写可复用渲染工具（GPL 派生）；本工具是自己写的 numpy 光栅器，见 `render/README.md`。
- 替身数据画出的接线图要在副标题写明"替身数据"。
- 字体文件不提交进仓库，用系统安装的字体。

## 准备（一次）

```bash
cd hardware-studio && . .venv/bin/activate && pip install -r requirements.txt
fc-list :lang=zh | head -1 || sudo apt-get install -y fonts-noto-cjk   # 中文标注要用；OFL 1.1
```

没有中文字体也能跑：渲染图只标 "Render"，命令行会提示，记进报告。

## 出渲染图

1. 拿到装配位置下的零件文件（不要各自归零），例如 `cad/examples/out/{bottom,top,cap_btn_a}.stl`。
   坐标：mm，Z 向上，正面朝 -Y。
2. 先用 `--quality draft --size 800x600` 快速看效果，再出正式图：

   ```bash
   python render/render.py \
     --part <下壳>.stl:#C9A27C:matte --part <上壳>.step:#EFE9DF:satin:0,0,28 \
     --part <按键>.stl:#3A3F47:rubber:0,0,48 \
     --views front,side,back,iso --exploded --exploded-views iso \
     --out products/<产品名>/render --name <产品名>
   python render/render.py ...同上... --scene desk --props book,pencil --views iso,front
   ```

   或写 YAML 场景文件（格式见 `render/README.md`，例子 `render/examples/generic_box.yaml`）后
   `python render/render.py --config <文件>`；命令行参数会覆盖 YAML。
   自检（渲染库里示例外壳，草稿 2 张约 15 s，输出到临时目录，不覆盖示例输出）：
   `python render/render.py --config render/examples/generic_box.yaml --quality draft --size 400x300 --views iso --exploded-views iso --out /tmp/render_selftest`
3. 场景：`studio`（浅灰背景，看造型）、`desk`（木桌 + 书/铅笔，体现尺寸，书是 A5 148×210 mm）、`plain`。
   视角：`front/side(=right)/left/back/top/iso/iso-left/iso-back/hero` 或 `azXXelYY`。
   材质：`matte satin gloss rubber metal glass paper`。爆炸位移是每个零件第 4 段 `DX,DY,DZ`（mm）。
4. 1600×1200 final 每张约 20–60 s（4 核 CPU）；多张时会多出一张拼图 `render_<名>_<场景>_sheet.png`。

## 出接线图

```bash
python diagrams/wiring.py products/<产品名>/pins.csv --out products/<产品名>/out \
  [--subtitle "替身数据 / stand-in data"]
```

输出 `wiring_<产品名>.svg` + `.png`；命令行打印核对结果。pins.csv 格式见 `CONVENTIONS.md`，
以 `#` 开头的行是注释。

## 怎么检查结果

渲染图：
- [ ] 文件名 `render_` 开头，尺寸等于 `--size`；
- [ ] 用 Read 工具打开 PNG 看：右下角有"渲染图 / Render"标签；零件颜色、位置、爆炸方向对；没有缺面/黑块；
- [ ] 需要机器检查时：`RenderedImage.label`（文字、位置、是否中文）或 PNG 元数据 `Label` 字段：
      `python -c "from PIL import Image; im=Image.open('render_x.png'); print(im.size, im.info['Label'])"`；
- [ ] `pytest render/tests` 通过。

接线图：
- [ ] `wiring.py` 输出 `OK: every wire drawn exactly once` 且没有 `LAYOUT` 行，退出码 0；
- [ ] 单独核对：`python diagrams/check_wiring.py pins.csv wiring_x.svg`（MISSING/EXTRA/GEOMETRY 任一出现即失败）；
- [ ] 打开 PNG 看：电源线红、地线黑、信号线按 net 区分颜色，引脚旁有 net 名，下方表格有备注；
- [ ] `pytest diagrams/tests` 通过。

## 出问题时

- `unknown view/material/colour`：按提示改参数；`part file not found`：检查路径（YAML 里相对 YAML 文件）。
- 图里有零件但位置错：零件文件不是装配坐标，回 cad/ 导出装配位置的 STL/STEP。
- 接线图退出码 1：看 MISSING/EXTRA（图和表不一致，属工具缺陷，记录并报告）或 LAYOUT（排版重叠，同样报告）。
- pins.csv 被拒绝：按报错改表（同一引脚两个 net、kind 拼错、重复行等）。
