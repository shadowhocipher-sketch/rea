"""快速预览 PNG（matplotlib，平面着色），用于检查，不是正式渲染（正式渲染由 render/ 负责）。

图上标"预览 / Preview (not a render)"，不冒充渲染图或实拍。

可以 import::

    from tools.preview import preview_png
    preview_png({"top": a, "bottom": b}, "out/preview.png", explode=15)

命令行::

    python cad/tools/preview.py a.stl b.step --out preview.png --explode 15
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

_PALETTE = ["#7aa6c2", "#d9a066", "#9cc28a", "#c99bd1", "#e0c35f", "#8fb3b0", "#d48a8a", "#a0a0a0"]
_LIGHT = np.array([0.4, -0.5, 0.75])
_LIGHT = _LIGHT / np.linalg.norm(_LIGHT)

VIEWS = {
    "iso": (25, -55),
    "front": (0, -90),
    "top": (90, -90),
    "iso_back": (25, 125),
}


def _as_mesh(obj) -> trimesh.Trimesh:
    if isinstance(obj, trimesh.Trimesh):
        return obj
    if isinstance(obj, (str, Path)):
        p = Path(obj)
        if p.suffix.lower() == ".stl":
            return trimesh.load(str(p))
        from build123d import import_step

        obj = import_step(str(p))
    verts, tris = obj.tessellate(0.1, 0.3)
    v = np.array([[q.X, q.Y, q.Z] for q in verts], dtype=float)
    return trimesh.Trimesh(vertices=v, faces=np.array(tris), process=True)


def _shade(mesh: trimesh.Trimesh, color: str) -> np.ndarray:
    base = np.array(matplotlib.colors.to_rgb(color))
    lam = np.clip(mesh.face_normals @ _LIGHT, 0, 1)
    k = 0.35 + 0.65 * lam
    return np.clip(base[None, :] * k[:, None], 0, 1)


def preview_png(
    shapes: dict,
    out: str | Path,
    views: tuple[str, ...] = ("iso", "front", "top", "iso_back"),
    explode: float = 0.0,
    explode_names: tuple[str, ...] = ("top", "front"),
    envelopes: dict | None = None,
    title: str | None = None,
    dpi: int = 110,
) -> Path:
    """把若干实体画成多视角预览图。

    Args:
        shapes: 名称 -> build123d 实体 / trimesh / 文件路径。
        out: 输出 PNG 路径。
        views: 视角名，取自 :data:`VIEWS`。
        explode: 爆炸距离（mm）；名称在 ``explode_names`` 里的零件沿 +Z 抬起这么多。
        explode_names: 需要抬起的零件名（默认上壳 / 前壳）。
        envelopes: 检查用包络体（半透明灰色线框显示），可为 None。
        title: 图标题。
        dpi: 分辨率。
    """
    _set_cjk_font()
    meshes = {}
    for n, s in shapes.items():
        m = _as_mesh(s).copy()
        if explode and n in explode_names:
            m.apply_translation([0, 0, explode])
        meshes[n] = m
    env_meshes = {n: _as_mesh(s) for n, s in (envelopes or {}).items()}
    allv = np.vstack([m.vertices for m in meshes.values()])
    lo, hi = allv.min(0), allv.max(0)
    ctr, span = (lo + hi) / 2, (hi - lo).max() / 2 * 1.05
    # matplotlib 按三角形中心做画家算法排序，细长大三角形会前后错乱；先细分到较小边长再画
    max_edge = span / 12
    for n_, m in list(meshes.items()):
        v, f = trimesh.remesh.subdivide_to_size(m.vertices, m.faces, max_edge=max_edge, max_iter=8)
        meshes[n_] = trimesh.Trimesh(v, f, process=False)
    n = len(views)
    cols = 2 if n > 1 else 1
    rows = (n + cols - 1) // cols
    fig = plt.figure(figsize=(6 * cols, 5 * rows))
    for i, vname in enumerate(views):
        ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
        for j, (name, m) in enumerate(meshes.items()):
            pc = Poly3DCollection(m.triangles, facecolors=_shade(m, _PALETTE[j % len(_PALETTE)]), edgecolors="none")
            ax.add_collection3d(pc)
        for name, m in env_meshes.items():
            pc = Poly3DCollection(m.triangles, facecolors=(0.5, 0.5, 0.5, 0.08), edgecolors=(0.3, 0.3, 0.3, 0.05))
            ax.add_collection3d(pc)
        ax.set_xlim(ctr[0] - span, ctr[0] + span)
        ax.set_ylim(ctr[1] - span, ctr[1] + span)
        ax.set_zlim(ctr[2] - span, ctr[2] + span)
        ax.set_box_aspect((1, 1, 1))
        el, az = VIEWS[vname]
        ax.view_init(elev=el, azim=az)
        ax.set_title(vname, fontsize=9)
        ax.set_xlabel("X mm", fontsize=7)
        ax.set_ylabel("Y mm", fontsize=7)
        ax.set_zlabel("Z mm", fontsize=7)
        ax.tick_params(labelsize=6)
    handles = [plt.Line2D([0], [0], marker="s", ls="", color=_PALETTE[j % len(_PALETTE)], label=n)
               for j, n in enumerate(meshes)]
    fig.legend(handles=handles, loc="lower center", ncol=min(len(handles), 6), fontsize=8)
    fig.suptitle((title + "  " if title else "") + "预览 / Preview (not a render)", fontsize=11)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi)
    plt.close(fig)
    return out


def _set_cjk_font() -> None:
    """有中文字体就用，没有就退回默认字体（中文可能显示为方块，但不影响英文标注）。"""
    import logging

    from matplotlib import font_manager

    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

    for name in ("Noto Sans CJK SC", "Noto Sans CJK JP", "Noto Serif CJK SC", "WenQuanYi Zen Hei", "Source Han Sans SC", "SimHei"):
        if any(f.name == name for f in font_manager.fontManager.ttflist):
            plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
            return


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="STL/STEP 快速预览 PNG")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--explode", type=float, default=0.0)
    ap.add_argument("--views", default="iso,front,top,iso_back")
    a = ap.parse_args(argv)
    shapes = {Path(f).stem: f for f in a.files}
    p = preview_png(shapes, a.out, tuple(a.views.split(",")), a.explode, explode_names=tuple(shapes)[:1])
    print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
