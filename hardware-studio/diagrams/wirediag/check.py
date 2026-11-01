"""Verify a wiring SVG against its pins.csv: every wire drawn exactly once, nothing extra,
and each drawn wire starts/ends on the pin markers it claims to connect."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .model import Wire, read_pins_csv

SVG_NS = "{http://www.w3.org/2000/svg}"


@dataclass
class CheckResult:
    expected: int
    drawn: int
    missing: list[tuple] = field(default_factory=list)
    extra: list[tuple] = field(default_factory=list)
    geometry: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.missing or self.extra or self.geometry)

    def report(self) -> str:
        lines = [f"pins.csv wires: {self.expected}; drawn wires: {self.drawn}"]
        for k in self.missing:
            lines.append(f"MISSING  {k[0]}.{k[1]} -> {k[2]}.{k[3]}  net={k[4]} kind={k[5]}")
        for k in self.extra:
            lines.append(f"EXTRA    {k[0]}.{k[1]} -> {k[2]}.{k[3]}  net={k[4]} kind={k[5]}")
        lines += [f"GEOMETRY {g}" for g in self.geometry]
        lines.append("OK: every wire drawn exactly once" if self.ok else "FAIL")
        return "\n".join(lines)


def _tag(el) -> str:
    return el.tag.replace(SVG_NS, "")


def parse_svg(svg_text: str):
    root = ET.fromstring(svg_text)
    wires, pins = [], {}
    for el in root.iter():
        t = _tag(el)
        cls = el.get("class", "")
        if t == "polyline" and "wire" in cls.split():
            key = tuple(el.get(a, "") for a in ("data-from-part", "data-from-pin", "data-to-part",
                                                 "data-to-pin", "data-net", "data-kind"))
            pts = []
            for tok in (el.get("points") or "").split():
                x, y = tok.split(",")
                pts.append((float(x), float(y)))
            wires.append((key, pts, el.get("data-row")))
        elif t == "g" and "pin" in cls.split():
            circle = next((c for c in el if _tag(c) == "circle"), None)
            if circle is not None:
                pins.setdefault((el.get("data-part"), el.get("data-pin")), []).append(
                    (float(circle.get("cx")), float(circle.get("cy"))))
    return wires, pins


def check(wires: list[Wire], svg_text: str, tol: float = 0.6) -> CheckResult:
    drawn, pins = parse_svg(svg_text)
    want = Counter(w.key for w in wires)
    have = Counter(k for k, _, _ in drawn)
    res = CheckResult(expected=sum(want.values()), drawn=sum(have.values()))
    res.missing = sorted((want - have).elements())
    res.extra = sorted((have - want).elements())

    def near(pt, cands):
        return any(abs(pt[0] - c[0]) <= tol and abs(pt[1] - c[1]) <= tol for c in cands)

    for key, pts, row in drawn:
        if len(pts) < 2:
            res.geometry.append(f"row {row}: wire has fewer than 2 points")
            continue
        a = pins.get((key[0], key[1]), [])
        b = pins.get((key[2], key[3]), [])
        if not a:
            res.geometry.append(f"row {row}: no pin marker for {key[0]}.{key[1]}")
        elif not near(pts[0], a):
            res.geometry.append(f"row {row}: wire does not start on {key[0]}.{key[1]}")
        if not b:
            res.geometry.append(f"row {row}: no pin marker for {key[2]}.{key[3]}")
        elif not near(pts[-1], b):
            res.geometry.append(f"row {row}: wire does not end on {key[2]}.{key[3]}")
    return res


def check_files(pins_csv: str | Path, svg_path: str | Path) -> CheckResult:
    return check(read_pins_csv(pins_csv), Path(svg_path).read_text(encoding="utf-8"))
