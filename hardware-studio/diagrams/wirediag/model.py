"""Parse ``pins.csv`` (format in hardware-studio/CONVENTIONS.md section 2).

    from_part,from_pin,to_part,to_pin,net,kind,note

One row is one physical wire. ``kind`` is power / ground / signal.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

COLUMNS = ["from_part", "from_pin", "to_part", "to_pin", "net", "kind", "note"]
KINDS = ("power", "ground", "signal")


class PinsCsvError(ValueError):
    pass


@dataclass(frozen=True)
class Wire:
    row: int  # 1-based data row number (header excluded)
    from_part: str
    from_pin: str
    to_part: str
    to_pin: str
    net: str
    kind: str
    note: str = ""

    @property
    def key(self) -> tuple[str, str, str, str, str, str]:
        return (self.from_part, self.from_pin, self.to_part, self.to_pin, self.net, self.kind)

    @property
    def ends(self) -> tuple[tuple[str, str], tuple[str, str]]:
        return (self.from_part, self.from_pin), (self.to_part, self.to_pin)


def read_pins_csv(path: str | Path) -> list[Wire]:
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig")
    return parse_pins_csv(text, str(path))


def parse_pins_csv(text: str, source: str = "pins.csv") -> list[Wire]:
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.lstrip().startswith("#")]
    reader = csv.DictReader(lines)
    header = [h.strip() for h in (reader.fieldnames or [])]
    missing = [c for c in COLUMNS if c not in header]
    if missing:
        raise PinsCsvError(f"{source}: missing column(s) {missing}; expected header {','.join(COLUMNS)}")
    wires: list[Wire] = []
    errors: list[str] = []
    for i, raw in enumerate(reader, start=1):
        row = {k.strip(): (v or "").strip() for k, v in raw.items() if k is not None}
        w = Wire(i, row["from_part"], row["from_pin"], row["to_part"], row["to_pin"],
                 row["net"], row["kind"].lower(), row.get("note", ""))
        for col in COLUMNS[:6]:
            if not getattr(w, col):
                errors.append(f"row {i}: empty {col}")
        if w.kind and w.kind not in KINDS:
            errors.append(f"row {i}: kind {w.kind!r} is not one of {KINDS}")
        if (w.from_part, w.from_pin) == (w.to_part, w.to_pin):
            errors.append(f"row {i}: wire connects {w.from_part}.{w.from_pin} to itself")
        wires.append(w)
    if not wires:
        errors.append("no wires")
    # one pin belongs to exactly one net
    pin_net: dict[tuple[str, str], tuple[str, int]] = {}
    for w in wires:
        for end in w.ends:
            if end in pin_net and pin_net[end][0] != w.net:
                errors.append(f"row {w.row}: pin {end[0]}.{end[1]} is on net {pin_net[end][0]!r} "
                              f"(row {pin_net[end][1]}) and {w.net!r}")
            pin_net.setdefault(end, (w.net, w.row))
    # one net has one kind
    net_kind: dict[str, str] = {}
    for w in wires:
        if net_kind.setdefault(w.net, w.kind) != w.kind:
            errors.append(f"row {w.row}: net {w.net!r} marked both {net_kind[w.net]!r} and {w.kind!r}")
    dup = [k for k, n in Counter(w.key for w in wires).items() if n > 1]
    for k in dup:
        errors.append(f"duplicate wire {k[0]}.{k[1]} -> {k[2]}.{k[3]} ({k[4]})")
    if errors:
        raise PinsCsvError(f"{source}: " + "; ".join(errors))
    return wires
