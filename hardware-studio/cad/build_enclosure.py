#!/usr/bin/env python3
"""从外壳参数文件（YAML）生成外壳：各零件 STEP/STL、预览 PNG、检查报告。

用法::

    python cad/build_enclosure.py products/<产品名>/enclosure.yaml --out products/<产品名>/cad_out
    python cad/build_enclosure.py cad/examples/generic_box.yaml --out cad/examples/out --no-slice

参数文件格式见 ``cad/README.md``。退出码：0 = 全部检查通过；1 = 有检查未通过；2 = 参数错误。

输出（``--out`` 目录）：

* ``<零件>.step`` / ``<零件>.stl``：每个零件，**装配位置**（全局坐标，单位 mm）；
* ``assembly.step``：所有零件的装配体；
* ``envelopes.step``：检查用包络体（元器件、电池膨胀外形、USB 插座和插头外壳）；
* ``preview_assembly.png``、``preview_exploded.png``：快速预览（不是渲染图）；
* ``check_report.json``、``check_report.md``：检查报告。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from build123d import Compound  # noqa: E402

from hwcad.enclosure import BuildResult, build_enclosure  # noqa: E402
from tools.export import export_part, export_parts  # noqa: E402
from tools.measure import bbox, fits_bed, interference_matrix, min_wall_report, volume  # noqa: E402
from tools.preview import preview_png  # noqa: E402
from tools.slice_check import find_slicer, slice_check  # noqa: E402


def run_checks(res: BuildResult, wall_samples: int = 1500) -> dict:
    """对拼装结果做全部检查，返回报告 dict（``ok`` 为总结论）。"""
    rep: dict = {"name": res.name, "process": res.process.key, "parts": {}, "warnings": list(res.warnings)}
    for n, p in res.parts.items():
        row = {"bbox": bbox(p), "volume_mm3": round(volume(p), 2), "valid": bool(p.is_valid)}
        row["wall"] = min_wall_report(p, res.process.min_wall, samples=wall_samples)
        if res.printer_bed:
            row["bed"] = fits_bed(p, res.printer_bed)
        rep["parts"][n] = row
    everything = {**res.parts, **res.envelopes}
    rep["interference"] = interference_matrix(everything, res.ignore_pairs)
    usb = {k: v for k, v in res.envelopes.items() if k.endswith("_plug_overmold")}
    rep["usb_plug_insertion"] = {}
    for k, env in usb.items():
        hits = [p for p in rep["interference"]["pairs"] if k in (p["a"], p["b"])]
        rep["usb_plug_insertion"][k] = {"ok": not hits, "interferes_with": hits}
    rep["features"] = {f.name: f.info for f in res.features}
    rep["fasteners"] = res.fastener_info
    rep["printer"] = {"name": res.printer_name, "bed": res.printer_bed}
    wall_flags = {n: r["wall"].get("fraction_below", 0) for n, r in rep["parts"].items()}
    rep["checks"] = {
        "geometry_valid": all(r["valid"] for r in rep["parts"].values()),
        "interference_zero": rep["interference"]["ok"],
        "usb_plug_fully_inserts": all(v["ok"] for v in rep["usb_plug_insertion"].values()),
        "fits_printer_bed": (all(r["bed"]["ok"] for r in rep["parts"].values()) if res.printer_bed else None),
        "spec_warnings": len(res.warnings),
        "wall_fraction_below_min": wall_flags,
    }
    c = rep["checks"]
    rep["ok"] = bool(c["geometry_valid"] and c["interference_zero"] and c["usb_plug_fully_inserts"]
                     and c["fits_printer_bed"] is not False and c["spec_warnings"] == 0)
    return rep


def _md(rep: dict, files: dict, elapsed: float) -> str:
    L = [f"# 外壳检查报告：{rep['name']}", "",
         f"- 工艺：{rep['process']}；打印机：{rep['printer']['name']} {rep['printer']['bed']}",
         f"- 总结论：**{'通过' if rep['ok'] else '未通过'}**（生成用时 {elapsed:.1f} s）", "",
         "## 检查项", "", "| 项目 | 结果 |", "|---|---|"]
    c = rep["checks"]
    L += [f"| 几何有效 | {c['geometry_valid']} |",
          f"| 干涉体积为 0（零件 + 包络体两两） | {c['interference_zero']}（总 {rep['interference']['total']} mm³） |",
          f"| USB 插头能插到底 | {c['usb_plug_fully_inserts']} |",
          f"| 能放上打印平台 | {c['fits_printer_bed']} |",
          f"| 参数警告数 | {c['spec_warnings']} |", ""]
    L += ["## 零件", "", "| 零件 | 尺寸 X×Y×Z (mm) | 体积 (mm³) | 壁厚抽样 p01 / 中位 (mm) | 低于最小壁厚比例 |", "|---|---|---|---|---|"]
    for n, r in rep["parts"].items():
        s = r["bbox"]["size"]
        w = r["wall"]
        L.append(f"| {n} | {s[0]:.1f}×{s[1]:.1f}×{s[2]:.1f} | {r['volume_mm3']:.0f} | "
                 f"{w.get('p01')} / {w.get('median')} | {w.get('fraction_below', 0):.1%} |")
    L += ["", "壁厚是抽样估计（射线法），卡钩尖、圆角边缘等本身趋近 0 的几何会计入比例，最薄点坐标见 JSON。", ""]
    if rep["interference"]["pairs"]:
        L += ["## 干涉", "", "| A | B | 体积 mm³ | 已忽略 |", "|---|---|---|---|"]
        L += [f"| {p['a']} | {p['b']} | {p['volume']} | {p['ignored']} |" for p in rep["interference"]["pairs"]]
        L.append("")
    if rep.get("slice"):
        L += ["## 切片（PrusaSlicer 命令行，时间为默认配置估算）", "", "| 零件 | 能否切片 | 耗材 (g, 估算) | 时间 |", "|---|---|---|---|"]
        for n, s in rep["slice"].items():
            L.append(f"| {n} | {s.get('ok')} | {s.get('filament_g_est', '-')} | {s.get('time_text', s.get('error', '-'))} |")
        L.append("")
    if rep["warnings"]:
        L += ["## 警告", ""] + [f"- {w}" for w in rep["warnings"]] + [""]
    L += ["## 输出文件", ""] + [f"- {k}: {', '.join(Path(x).name for x in v)}" for k, v in files.items()]
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="从 enclosure.yaml 生成外壳")
    ap.add_argument("spec")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-slice", action="store_true", help="跳过切片检查")
    ap.add_argument("--no-preview", action="store_true")
    ap.add_argument("--wall-samples", type=int, default=1500)
    a = ap.parse_args(argv)
    t0 = time.time()
    try:
        spec = yaml.safe_load(Path(a.spec).read_text(encoding="utf-8"))
        res = build_enclosure(spec)
    except (ValueError, KeyError, TypeError) as e:
        print(f"参数错误：{e}", file=sys.stderr)
        return 2
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    files = export_parts(res.parts, out, ("step", "stl"))
    if res.envelopes:
        files["envelopes"] = [str(export_part(Compound(children=list(res.envelopes.values())), out / "envelopes.step"))]
    rep = run_checks(res, a.wall_samples)
    if not a.no_preview:
        p1 = preview_png(res.parts, out / "preview_assembly.png", title=res.name, envelopes=None)
        upper = res.shell.part_names()["upper"]
        ex = max(res.shell.height * 0.8, 10.0)
        p2 = preview_png(res.parts, out / "preview_exploded.png", title=f"{res.name} exploded",
                         explode=ex, explode_names=(upper,) + tuple(n for n in res.parts if n.startswith("cap_")),
                         envelopes=res.envelopes)
        files["preview"] = [str(p1), str(p2)]
    if not a.no_slice and res.process.key == "fdm":
        if find_slicer() is None:
            rep["slice"] = {"_": {"ok": False, "error": slice_check(out / "x.stl")["error"]}}
        else:
            upper = res.shell.part_names()["upper"]
            bed = res.printer_bed[:2] if res.printer_bed else (250.0, 210.0)
            rep["slice"] = {n: slice_check(out / f"{n}.stl", rotate_x=180.0 if n == upper else 0.0, bed=bed)
                            for n in res.parts}
    elapsed = time.time() - t0
    rep["elapsed_s"] = round(elapsed, 1)
    (out / "check_report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    (out / "check_report.md").write_text(_md(rep, files, elapsed), encoding="utf-8")
    print(f"{'通过' if rep['ok'] else '未通过'}：报告 {out / 'check_report.md'}")
    for k, v in rep["checks"].items():
        print(f"  {k}: {v}")
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
