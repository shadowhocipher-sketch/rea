"""导出 STL / STEP。

可以 import::

    from tools.export import export_parts
    export_parts({"top": part_a, "bottom": part_b}, "out/", formats=("step", "stl"))

也可以命令行转换格式（STEP -> STL）::

    python cad/tools/export.py in.step --out out/ --stl-tolerance 0.02
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from build123d import Compound, export_step, export_stl, import_step


def export_part(shape, path: str | Path, stl_tolerance: float = 0.02, stl_angular_tolerance: float = 0.1) -> Path:
    """按扩展名导出一个实体（.step/.stp/.stl），返回文件路径。

    Args:
        shape: build123d 实体。
        path: 输出文件路径。
        stl_tolerance: STL 线性弦高误差，mm（默认 0.02，打印足够）。
        stl_angular_tolerance: STL 角度误差，弧度。
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ext = p.suffix.lower()
    if ext in (".step", ".stp"):
        ok = export_step(shape, str(p))
    elif ext == ".stl":
        ok = export_stl(shape, str(p), tolerance=stl_tolerance, angular_tolerance=stl_angular_tolerance)
    else:
        raise ValueError(f"不支持的格式：{ext}")
    if ok is False or not p.exists() or p.stat().st_size == 0:
        raise RuntimeError(f"导出失败：{p}")
    return p


def export_parts(parts: dict, out_dir: str | Path, formats=("step", "stl"), prefix: str = "",
                 assembly_name: str | None = "assembly") -> dict[str, list[str]]:
    """导出多个零件；``assembly_name`` 不为 None 时另外导出一个装配体 STEP。

    Returns:
        零件名 -> 已写出的文件路径列表。
    """
    out = Path(out_dir)
    written: dict[str, list[str]] = {}
    for name, shp in parts.items():
        written[name] = [str(export_part(shp, out / f"{prefix}{name}.{fmt}")) for fmt in formats]
    if assembly_name and "step" in formats and len(parts) > 1:
        comp = Compound(children=[s for s in parts.values()])
        written[assembly_name] = [str(export_part(comp, out / f"{prefix}{assembly_name}.step"))]
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="STEP -> STL/STEP 导出")
    ap.add_argument("inputs", nargs="+", help="STEP 文件")
    ap.add_argument("--out", required=True)
    ap.add_argument("--formats", default="stl", help="逗号分隔：stl,step")
    ap.add_argument("--stl-tolerance", type=float, default=0.02)
    a = ap.parse_args(argv)
    fmts = [f.strip() for f in a.formats.split(",") if f.strip()]
    for f in a.inputs:
        shp = import_step(f)
        for fmt in fmts:
            p = export_part(shp, Path(a.out) / f"{Path(f).stem}.{fmt}", a.stl_tolerance)
            print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
