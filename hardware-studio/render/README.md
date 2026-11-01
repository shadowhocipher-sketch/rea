# render/ — 产品渲染图

从 STEP / STL（也支持 OBJ / PLY / 3MF）渲染产品图：多角度、爆炸图、摄影棚背景或桌面场景。
输出 PNG，文件名一律 `render_` 开头，右下角标"渲染图 / Render"，PNG 元数据里也写了
`Label` 和"渲染图，非实拍"。**渲染图不能当实拍用。**

## 渲染器和许可证

渲染器是本目录自己写的 numpy 光栅器（`prender/raster.py`）+ 延迟着色（`prender/engine.py`），
不用 Blender/bpy，不用 OpenGL/EGL/OSMesa，无界面直接跑。

| 依赖 | 版本 | 许可证 | 用途 |
|---|---|---|---|
| numpy | 2.5.4 | BSD-3-Clause | 光栅化、着色 |
| Pillow | 13.0.0 | MIT-CMU (HPND) | 写 PNG、画标注、缩放 |
| trimesh | 5.2.0 | MIT | 读 STL/OBJ/PLY/3MF，折边平滑法线 |
| scipy | 1.18.1 | BSD-3-Clause | trimesh 平滑法线需要 |
| PyYAML | 6.0.3 | MIT | 读 YAML 场景文件 |
| build123d | 0.13.0 | Apache-2.0 | 读 STEP 并三角化（只在输入是 STEP 时用）；它依赖 OCP/OpenCASCADE（LGPL-2.1 + OCCT 例外条款），按库调用，不复制代码，和 cad/ 线用法相同 |
| matplotlib | 3.11.2 | PSF 风格 (matplotlib License) | 只借用它自带的 DejaVu Sans 字体作英文后备 |
| Noto Sans CJK（系统字体） | fonts-noto-cjk 20230817 | SIL OFL 1.1 | 中文标注；不随库分发 |

## 安装

```bash
cd hardware-studio && . .venv/bin/activate
pip install -r requirements.txt          # 顶层会 -r render/requirements.txt
# 中文字体（标注"渲染图"需要）：
sudo apt-get install fonts-noto-cjk      # Debian/Ubuntu；macOS/Windows 自带苹方/微软雅黑也能用
# 或指定字体：export HS_CJK_FONT=/path/NotoSansCJK-Regular.ttc#2
```

找不到中文字体时，标注退化为英文 "Render"，命令行会打印提示，不会崩溃。

## 用法

命令行：

```bash
python render/render.py \
  --part cad/examples/out/bottom.stl:#C9A27C:matte \
  --part cad/examples/out/top.step:#EFE9DF:satin:0,0,28 \
  --views front,side,back,iso --exploded --exploded-views iso \
  --scene desk --props book,pencil --out products/<产品名>/render --name <产品名>
python render/render.py --config render/examples/generic_box.yaml          # YAML 场景文件
python render/render.py --config render/examples/generic_box.yaml --quality draft --views iso   # 快速预览
```

- `--part PATH[:COLOR[:MATERIAL[:DX,DY,DZ]]]`，可重复。颜色 `#RRGGBB`；材质 `matte`、`satin`、`gloss`、
  `rubber`、`metal`、`glass`（深色屏幕玻璃）、`paper`；`DX,DY,DZ` 是爆炸图位移（mm）。
- `--views`：`front`(从 -Y 看)、`back`、`side`/`right`(从 +X)、`left`、`top`、`iso`(右前上方 45°/30°)、
  `iso-left`、`iso-back`、`hero`，或自定义 `az30el20`（方位角/仰角，度）。
- `--scene`：`studio`（浅灰无缝背景 + 阴影，默认）、`desk`（木纹桌面 + 墙 + 景深）、`plain`（纯色背景无地面）。
- `--props book,pencil`：桌面道具，用来体现尺寸。书是 A5 平装书 148×210×16 mm，铅笔 Ø7.2×175 mm。
  道具跟着相机摆在产品左后方和右前方。
- `--exploded` / `--exploded-views iso`：按各零件位移再出爆炸图（`render_<名>_<场景>_<视角>-exploded.png`）。
- `--size 1600x1200`、`--quality draft|final`、`--ss N`（超采样）、`--label`、`--no-sheet`、`--json`。
- 多张图时额外输出一张拼图 `render_<名>_<场景>_sheet.png`。

坐标约定：单位 mm，Z 向上（与 build123d / cad/ 一致），正面朝 -Y。零件按在装配体中的位置给出，
不要各自归零；地面放在所有零件最低点。

YAML 场景文件（路径相对 YAML 文件所在目录，命令行参数会覆盖它）：

```yaml
name: generic-box
out: out/generic-box
scene: studio              # studio | desk | plain
props: [book]              # 只在 desk 场景有效
views: [front, side, back, iso]
exploded_views: [iso]
size: 1600x1200
quality: final
parts:
  - path: ../../cad/examples/out/bottom.stl
    color: "#C9A27C"
    material: matte
  - path: ../../cad/examples/out/top.step
    color: "#EFE9DF"
    explode: [0, 0, 28]
  - "../../cad/examples/out/cap_btn_a.stl:#3A3F47:rubber:0,0,48"   # 也可写成一行
```

Python 调用：

```python
import sys; sys.path.insert(0, "hardware-studio/render")
from prender import PartSpec, RenderJob, render_product, load_job
results = render_product(RenderJob(parts=[PartSpec("shell.stl", "#EFE9DF", "satin")],
                                   views=["iso", "front"], scene="desk", props=["book"], out="out"))
for r in results:
    print(r.path, r.size, r.label.text, r.label.box)   # 标注文字和位置
```

## 速度（实测，4 核，无 GPU）

1600×1200、`final`（2× 超采样，24 方向天光阴影）：测试模型每张约 26–35 s，B 线示例外壳每张约 22–60 s。
`draft`（不超采样、10 方向）800×600 每张约 1–1.5 s，适合调参数。

## 检查结果

- 文件名以 `render_` 开头；尺寸等于 `--size`；
- 右下角有深色标签"渲染图 / Render"（`RenderedImage.label.box` 给出位置，PNG 元数据 `Label` 字段同文）；
- 用图片查看器看一眼：零件没有缺面、颜色对、阴影落在地面上、爆炸图位移方向对；
- `pytest render/tests`。

## 文件

- `render.py` 命令行入口；`prender/` 库（`api.py` 任务和视角，`engine.py` 相机/光照/阴影，
  `raster.py` 光栅器，`mesh.py` 读模型和道具几何，`label.py` 标注，`fonts.py` 字体查找）
- `examples/make_test_model.py` 用 build123d 生成自测模型（圆角盒 + 屏幕 + 旋钮，STL + STEP）
- `examples/testbox.yaml`、`examples/generic_box.yaml` 示例任务；`examples/out/` 示例输出
- `tests/` pytest

## 已知限制

- 没有透明、折射、贴图、文字丝印；屏幕用深色 `glass` 材质代替显示内容。
- 阴影是 PCF 软阴影 + 多方向阴影图近似的天光遮蔽，不是路径追踪；大平面上的投影边缘偶有轻微折线感。
- 外壳开口里能看到内部（例如 B 线示例外壳的屏幕窗没有放屏幕零件），需要的话把屏幕模块作为零件加进来。
