"""测量工具：包围盒、体积、零件间干涉体积、最小壁厚抽样、打印平台检查。

可以 import，也可以命令行用::

    python cad/tools/measure.py part_a.step part_b.step --min-wall 1.2 [--json out.json]

命令行读 STEP（精确 B-rep，干涉用布尔求交）或 STL（只做包围盒 / 体积 / 壁厚抽样）。

最小壁厚抽样的做法：在三角网格表面按面积均匀撒点，从每个点沿**内法线**发射射线，
到下一次穿出表面的距离记为该点的局部厚度。这是抽样估计：

* 薄的地方可能刚好没抽到（增加 ``samples`` 可以降低漏检概率）；
* 卡钩尖、倒角边缘这类本来就趋近于 0 的几何也会被统计进去，所以报告给出分位数和
  低于阈值的比例，并列出最薄的几个点的坐标，由人判断。
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import trimesh

from build123d import import_step, import_stl


def bbox(shape) -> dict:
    """包围盒：min、max、size（mm）。"""
    bb = shape.bounding_box()
    mn = [bb.min.X, bb.min.Y, bb.min.Z]
    mx = [bb.max.X, bb.max.Y, bb.max.Z]
    return {"min": [round(v, 4) for v in mn], "max": [round(v, 4) for v in mx],
            "size": [round(b - a, 4) for a, b in zip(mn, mx)]}


def volume(shape) -> float:
    """体积 mm³。"""
    return float(shape.volume)


def interference_volume(a, b) -> float:
    """两个实体的干涉（重叠）体积 mm³；只接触不算干涉（体积为 0）。"""
    ba, bb_ = a.bounding_box(), b.bounding_box()
    if (ba.max.X < bb_.min.X or bb_.max.X < ba.min.X or ba.max.Y < bb_.min.Y or bb_.max.Y < ba.min.Y
            or ba.max.Z < bb_.min.Z or bb_.max.Z < ba.min.Z):
        return 0.0
    inter = a & b
    v = getattr(inter, "volume", 0.0) or 0.0
    return float(v)


def interference_matrix(shapes: dict, ignore: list[tuple[str, str]] | None = None, tol: float = 1e-3) -> dict:
    """所有两两组合的干涉体积。

    Args:
        shapes: 名称 -> 实体。
        ignore: 不参与判定的名称对（仍然计算并报告）。
        tol: 小于该体积（mm³）视为 0（布尔运算的数值噪声）。

    Returns:
        {"pairs": [{a, b, volume, ignored}], "total": 未忽略部分的总干涉体积, "ok": bool}
    """
    ignore_set = {frozenset(p) for p in (ignore or [])}
    pairs = []
    total = 0.0
    for (na, sa), (nb, sb) in itertools.combinations(shapes.items(), 2):
        v = interference_volume(sa, sb)
        v = 0.0 if v < tol else v
        ig = frozenset((na, nb)) in ignore_set
        if v > 0:
            pairs.append({"a": na, "b": nb, "volume": round(v, 4), "ignored": ig})
        if not ig:
            total += v
    return {"pairs": pairs, "total": round(total, 4), "ok": total == 0.0}


def to_trimesh(shape, tolerance: float = 0.05, angular_tolerance: float = 0.2) -> trimesh.Trimesh:
    """build123d 实体 -> trimesh 网格（用于壁厚抽样和预览）。"""
    verts, tris = shape.tessellate(tolerance, angular_tolerance)
    v = np.array([[p.X, p.Y, p.Z] for p in verts], dtype=float)
    f = np.array(tris, dtype=np.int64)
    return trimesh.Trimesh(vertices=v, faces=f, process=True)


def wall_thickness_samples(mesh: trimesh.Trimesh, samples: int = 2000, seed: int = 0) -> dict:
    """最小壁厚抽样（见模块说明）。

    Args:
        mesh: 封闭三角网格。
        samples: 撒点数。
        seed: 随机种子（结果可复现）。

    Returns:
        {"n": 有效样本数, "min", "p01", "p05", "median", "thickness": ndarray, "points": ndarray}
    """
    rng_state = np.random.get_state()
    np.random.seed(seed)
    try:
        pts, fidx = trimesh.sample.sample_surface(mesh, samples)
    finally:
        np.random.set_state(rng_state)
    normals = mesh.face_normals[fidx]
    eps = 1e-3
    origins = pts - normals * eps
    dirs = -normals
    inter = trimesh.ray.ray_triangle.RayMeshIntersector(mesh)
    locs, ray_idx, _ = inter.intersects_location(origins, dirs, multiple_hits=False)
    thick = np.full(len(pts), np.nan)
    if len(ray_idx):
        d = np.linalg.norm(locs - origins[ray_idx], axis=1) + eps
        thick[ray_idx] = d
    ok = ~np.isnan(thick)
    t = thick[ok]
    if len(t) == 0:
        return {"n": 0, "min": None, "p01": None, "p05": None, "median": None, "thickness": t, "points": pts[ok]}
    return {
        "n": int(len(t)),
        "min": float(t.min()),
        "p01": float(np.percentile(t, 1)),
        "p05": float(np.percentile(t, 5)),
        "median": float(np.median(t)),
        "thickness": t,
        "points": pts[ok],
    }


def min_wall_report(shape_or_mesh, min_wall: float, samples: int = 2000, seed: int = 0, worst: int = 5,
                    rel_tol: float = 0.01) -> dict:
    """壁厚抽样报告：分位数、低于阈值比例、最薄的几个点。

    ``rel_tol``：低于 ``min_wall × (1 - rel_tol)`` 才算"低于"，避免网格离散误差把恰好等于阈值的壁算进去。
    """
    mesh = shape_or_mesh if isinstance(shape_or_mesh, trimesh.Trimesh) else to_trimesh(shape_or_mesh)
    r = wall_thickness_samples(mesh, samples, seed)
    if r["n"] == 0:
        return {"n": 0, "error": "没有有效射线（网格可能不封闭）"}
    t, p = r["thickness"], r["points"]
    order = np.argsort(t)[:worst]
    below = float(np.mean(t < min_wall * (1 - rel_tol)))
    return {
        "n": r["n"],
        "min_wall_required": min_wall,
        "min": round(r["min"], 3),
        "p01": round(r["p01"], 3),
        "p05": round(r["p05"], 3),
        "median": round(r["median"], 3),
        "fraction_below": round(below, 4),
        "thinnest_points": [{"xyz": [round(float(c), 2) for c in p[i]], "t": round(float(t[i]), 3)} for i in order],
        "note": "抽样估计；卡钩尖、圆角边缘等趋近 0 的几何也会计入，请看最薄点位置判断",
    }


def fits_bed(shape, bed: tuple[float, float, float]) -> dict:
    """零件能否放上打印平台（允许绕轴转 90° 的整数倍，比较排序后的尺寸）。"""
    size = sorted(bbox(shape)["size"])
    b = sorted(bed)
    ok = all(s <= c for s, c in zip(size, b))
    return {"part_size_sorted": size, "bed_sorted": b, "ok": ok}


def load(path: str | Path):
    """读取 STEP / STL。"""
    p = Path(path)
    if p.suffix.lower() in (".step", ".stp"):
        return import_step(str(p))
    if p.suffix.lower() == ".stl":
        return import_stl(str(p))
    raise ValueError(f"不支持的格式：{p.suffix}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="测量 STEP/STL：包围盒、体积、干涉、壁厚抽样")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--min-wall", type=float, default=None, help="壁厚阈值 mm；给出时做壁厚抽样")
    ap.add_argument("--samples", type=int, default=2000)
    ap.add_argument("--bed", type=float, nargs=3, default=None, help="打印平台 X Y Z（mm）")
    ap.add_argument("--json", default=None, help="把结果写成 JSON")
    a = ap.parse_args(argv)
    shapes = {Path(f).stem: load(f) for f in a.files}
    paths = {Path(f).stem: Path(f) for f in a.files}
    out: dict = {"parts": {}}
    for n, s in shapes.items():
        is_stl = paths[n].suffix.lower() == ".stl"
        row: dict = {"bbox": bbox(s)}
        mesh = trimesh.load(str(paths[n])) if is_stl else None
        row["volume"] = round(float(mesh.volume), 3) if is_stl else round(volume(s), 3)
        if a.min_wall is not None:
            row["wall"] = min_wall_report(mesh if is_stl else s, a.min_wall, a.samples)
        if a.bed:
            row["bed"] = fits_bed(s, tuple(a.bed))
        out["parts"][n] = row
    if len(shapes) > 1 and all(Path(f).suffix.lower() in (".step", ".stp") for f in a.files):
        out["interference"] = interference_matrix(shapes)
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if a.json:
        Path(a.json).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
