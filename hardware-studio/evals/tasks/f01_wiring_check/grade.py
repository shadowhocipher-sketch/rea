"""f01: wiring diagram drawn from pins.csv matches it exactly; checker catches missing/extra wires (line F)."""
import csv
import re
from collections import Counter

from common import task_dir, weighted

META = {"id": "f01", "line": "F", "title": "接线图与 pins.csv 一一对应", "kind": "capability"}
HERE = task_dir(__file__)
WIRE_RE = re.compile(r"<polyline\b[^>]*\bclass=\"wire\"[^>]*>.*?</polyline>", re.S)


def _key(fp, fpin, tp, tpin, net, kind):
    return (frozenset((f"{fp}.{fpin}", f"{tp}.{tpin}")), net, kind)


def expected_wires():
    rows = [r for r in csv.reader((HERE / "pins.csv").open(encoding="utf-8")) if r and not r[0].startswith("#")]
    return Counter(_key(*r[:6]) for r in rows[1:])


def svg_wires(svg: str):
    out = Counter()
    for m in WIRE_RE.finditer(svg):
        a = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(0).split(">", 1)[0]))
        f, t = a.get("data-from", ""), a.get("data-to", "")
        out[(frozenset((f, t)), a.get("data-net"), a.get("data-kind"))] += 1
    return out


def produce(ctx):
    out = ctx.work / "w"
    r = ctx.py("diagrams/wiring.py", HERE / "pins.csv", "--out", out, "--name", "f01")
    svg_p = out / "wiring_f01.svg"
    ans = {"exit": r.returncode, "drawn": [], "missing_check": None, "extra_check": None}
    if not svg_p.exists():
        return ans
    svg = svg_p.read_text(encoding="utf-8")
    drawn = svg_wires(svg)
    ans["drawn"] = [[sorted(k[0]), k[1], k[2], n] for k, n in drawn.items()]
    wires = WIRE_RE.findall(svg)
    if wires:
        miss = ctx.work / "missing.svg"
        miss.write_text(svg.replace(wires[0], "", 1), encoding="utf-8")
        r1 = ctx.py("diagrams/check_wiring.py", HERE / "pins.csv", miss)
        ans["missing_check"] = [r1.returncode, "MISSING" in r1.stdout + r1.stderr]
        extra = ctx.work / "extra.svg"
        extra.write_text(svg.replace(wires[-1], wires[-1] + wires[-1], 1), encoding="utf-8")
        r2 = ctx.py("diagrams/check_wiring.py", HERE / "pins.csv", extra)
        ans["extra_check"] = [r2.returncode, "EXTRA" in r2.stdout + r2.stderr]
    return ans


def score(ans):
    exp = expected_wires()
    got = Counter({(frozenset(a), net, kind): n for a, net, kind, n in ans.get("drawn", [])})
    mc, ec = ans.get("missing_check") or [None, False], ans.get("extra_check") or [None, False]
    return weighted([
        (0.2, ans.get("exit") == 0, f"wiring.py 退出码 {ans.get('exit')}"),
        (0.4, got == exp, f"图中 {sum(got.values())} 根线，表中 {sum(exp.values())} 根；"
                          f"缺 {sum((exp - got).values())}，多 {sum((got - exp).values())}"),
        (0.2, mc[0] == 1 and mc[1], f"删一根线后核对：退出码 {mc[0]}，报 MISSING={mc[1]}"),
        (0.2, ec[0] == 1 and ec[1], f"多画一根线后核对：退出码 {ec[0]}，报 EXTRA={ec[1]}"),
    ])
