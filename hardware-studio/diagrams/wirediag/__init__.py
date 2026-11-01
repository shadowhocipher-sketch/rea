"""wirediag: wiring diagrams (SVG + PNG) from pins.csv, plus a drawn-vs-csv checker."""

from .check import CheckResult, check, check_files
from .layout import Layout, build_layout, check_layout
from .model import PinsCsvError, Wire, parse_pins_csv, read_pins_csv


def draw_wiring(pins_csv, out_dir, name=None, title=None, subtitle=None, scale=2.0):
    """Read pins.csv, write wiring_<name>.svg/.png; returns (svg_path, png_path, layout, problems)."""
    from pathlib import Path
    import re

    from .draw import to_png, to_svg

    pins_csv = Path(pins_csv)
    wires = read_pins_csv(pins_csv)
    name = re.sub(r"[^A-Za-z0-9_-]+", "-", name or pins_csv.parent.name).strip("-") or "diagram"
    lay = build_layout(wires, title or f"接线图 / Wiring diagram — {name}",
                       subtitle if subtitle is not None else f"由 {pins_csv.name} 自动生成，共 {len(wires)} 根线")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_path = out / f"wiring_{name}.svg"
    png_path = out / f"wiring_{name}.png"
    svg_path.write_text(to_svg(lay), encoding="utf-8")
    to_png(lay, png_path, scale=scale)
    return svg_path, png_path, lay, check_layout(lay)


__all__ = ["CheckResult", "check", "check_files", "Layout", "build_layout", "check_layout",
           "PinsCsvError", "Wire", "parse_pins_csv", "read_pins_csv", "draw_wiring"]
