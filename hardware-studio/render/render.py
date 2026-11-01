#!/usr/bin/env python3
"""Render product images (render_*.png, labelled "渲染图 / Render") from STL/STEP parts.

Examples
  python render/render.py --part shell.stl:#EFE9DF --part knob.step:#C9A27C:matte \
      --views front,iso,side,back --scene desk --props book --out render/out
  python render/render.py --config scene.yaml            # YAML job (see README)
  python render/render.py --config scene.yaml --quality draft --views iso

Part spec: PATH[:COLOR[:MATERIAL[:DX,DY,DZ]]]; DX,DY,DZ is the exploded-view offset in mm.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prender import (PROPS, QUALITY, SCENES, VIEW_PRESETS, MeshLoadError, PartSpec,  # noqa: E402
                     RenderConfigError, RenderJob, load_job, render_product)
from prender.api import _as_list, _size  # noqa: E402
from prender.engine import MATERIALS  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", help="YAML job file; command-line options override it")
    p.add_argument("--part", action="append", default=[], metavar="SPEC",
                   help="PATH[:COLOR[:MATERIAL[:DX,DY,DZ]]] (repeatable). Materials: " + ", ".join(MATERIALS))
    p.add_argument("--views", help="comma list: " + ", ".join(VIEW_PRESETS) + " or azXXelYY")
    p.add_argument("--scene", choices=SCENES)
    p.add_argument("--props", help="desk props, comma list of: " + ", ".join(PROPS))
    p.add_argument("--exploded", action="store_true", help="also render exploded views (uses part offsets)")
    p.add_argument("--exploded-views", help="views for the exploded renders (default: --views)")
    p.add_argument("--explode-factor", type=float)
    p.add_argument("--size", help="WIDTHxHEIGHT, default 1600x1200")
    p.add_argument("--quality", choices=tuple(QUALITY))
    p.add_argument("--ss", type=int, help="supersampling factor (overrides quality)")
    p.add_argument("--name", help="name used in file names: render_<name>_<scene>_<view>.png")
    p.add_argument("--label", help='corner label, default "渲染图 / Render"')
    p.add_argument("--no-sheet", action="store_true", help="skip the contact sheet")
    p.add_argument("--out", help="output directory")
    p.add_argument("--json", action="store_true", help="print results as JSON")
    return p


def job_from_args(args) -> RenderJob:
    if args.config:
        job = load_job(args.config)
    else:
        if not args.part:
            raise RenderConfigError("give --part (one or more) or --config")
        job = RenderJob(parts=[])
    if args.part:
        job.parts = [PartSpec.parse(s) for s in args.part]
    if args.views:
        job.views = _as_list(args.views)
    if args.scene:
        job.scene = args.scene
    if args.props is not None:
        job.props = _as_list(args.props)
    if args.exploded:
        job.exploded = True
    if args.exploded_views:
        job.exploded = True
        job.exploded_views = _as_list(args.exploded_views)
    if args.explode_factor is not None:
        job.explode_factor = args.explode_factor
    if args.size:
        job.size = _size(args.size)
    if args.quality:
        job.quality = args.quality
    if args.ss:
        job.supersample = args.ss
    if args.name:
        job.name = args.name
    if args.label:
        job.label = args.label
    if args.no_sheet:
        job.sheet = False
    if args.out:
        job.out = args.out
    return job


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        job = job_from_args(args)
        results = render_product(job, log=None if args.json else print)
    except (RenderConfigError, MeshLoadError, FileNotFoundError) as exc:
        print(f"render: error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps([r.as_dict() for r in results], ensure_ascii=False, indent=2))
    else:
        for r in results:
            if not r.label.cjk:
                print(f"note: no CJK font found; {Path(r.path).name} is labelled {r.label.text!r} only "
                      "(install fonts-noto-cjk)", file=sys.stderr)
                break
    return 0


if __name__ == "__main__":
    sys.exit(main())
