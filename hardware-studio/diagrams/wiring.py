#!/usr/bin/env python3
"""Draw a wiring diagram (wiring_<name>.svg + .png) from a pins.csv and verify it.

    python diagrams/wiring.py products/<product>/pins.csv --out products/<product>/out
    python diagrams/wiring.py pins.csv --out out --name demo --subtitle "替身数据 / stand-in data"

Exit status: 0 = drawn, every wire verified and layout clean; 1 = verification or
layout problem (files are still written); 2 = bad input.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wirediag import PinsCsvError, check_files, draw_wiring  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pins_csv")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--name", help="file name part: wiring_<name>.svg (default: folder of pins.csv)")
    ap.add_argument("--title")
    ap.add_argument("--subtitle")
    ap.add_argument("--scale", type=float, default=2.0, help="PNG pixels per SVG unit (default 2)")
    args = ap.parse_args(argv)
    try:
        svg, png, lay, problems = draw_wiring(args.pins_csv, args.out, args.name, args.title,
                                              args.subtitle, args.scale)
    except (PinsCsvError, FileNotFoundError) as exc:
        print(f"wiring: error: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {svg}\nwrote {png}")
    res = check_files(args.pins_csv, svg)
    print(res.report())
    for p in problems:
        print(f"LAYOUT   {p}")
    if not lay.measurer.cjk:
        print("note: no CJK font found; Chinese text in the PNG may be missing (install fonts-noto-cjk)",
              file=sys.stderr)
    return 0 if res.ok and not problems else 1


if __name__ == "__main__":
    sys.exit(main())
