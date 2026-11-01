#!/usr/bin/env python3
"""Check that a wiring SVG draws every wire of pins.csv exactly once (and nothing else).

    python diagrams/check_wiring.py pins.csv wiring_x.svg      # exit 0 = OK, 1 = mismatch
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wirediag import PinsCsvError, check_files  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pins_csv")
    ap.add_argument("svg")
    args = ap.parse_args(argv)
    try:
        res = check_files(args.pins_csv, args.svg)
    except (PinsCsvError, FileNotFoundError, ValueError) as exc:
        print(f"check_wiring: error: {exc}", file=sys.stderr)
        return 2
    print(res.report())
    return 0 if res.ok else 1


if __name__ == "__main__":
    sys.exit(main())
