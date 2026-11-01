#!/usr/bin/env python3
"""Generate the render self-test model with build123d: a rounded box body,
a dark screen window and a cylindrical knob. Writes STL and STEP.

    python render/examples/make_test_model.py [OUT_DIR]   # default render/examples/test_model
"""

from __future__ import annotations

import sys
from pathlib import Path

from build123d import (Align, Box, Cylinder, Pos, export_step, export_stl, fillet, Axis)


def build():
    body = Box(80, 50, 34, align=(Align.CENTER, Align.CENTER, Align.MIN))
    body = fillet(body.edges(), radius=7)
    # screen: thin dark slab sitting slightly proud of the front face (-Y)
    screen = Pos(0, -25.2, 18) * Box(46, 1.2, 18)
    screen = fillet(screen.edges().filter_by(Axis.Y), radius=2)
    knob = Pos(22, 6, 34) * Cylinder(8, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    knob = fillet(knob.edges(), radius=1.2)
    return {"body": body, "screen": screen, "knob": knob}


def main(out_dir: str | None = None) -> dict[str, Path]:
    out = Path(out_dir or Path(__file__).resolve().parent / "test_model")
    out.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, shape in build().items():
        stl = out / f"{name}.stl"
        export_stl(shape, str(stl), tolerance=0.02, angular_tolerance=0.1)
        written[name] = stl
    step = out / "knob.step"
    export_step(build()["knob"], str(step))
    written["knob_step"] = step
    return written


if __name__ == "__main__":
    for k, v in main(sys.argv[1] if len(sys.argv) > 1 else None).items():
        print(f"{k}: {v}")
