"""d01: mfg/cost.py vs an independent hand calculation at 100 and 1000 units (line D)."""
import csv

from common import task_dir, weighted


def _close(a, b, tol):
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False

META = {"id": "d01", "line": "D", "title": "BOM 成本 100/1000 台与手算核对", "kind": "capability"}
HERE = task_dir(__file__)

# Answer key: hand calculation written out in task.md
KEY = {
    100: {"per_unit": 5.86416, "quote": 250.616, "unverified": 225.80, "estimate": 110.00},
    1000: {"per_unit": 5.2316, "quote": 2176.60, "unverified": 1955.00, "estimate": 1100.00},
}
# summary.csv rounds per_unit to 4 decimals and amounts to 2, so compare with absolute tolerances just above
# the rounding error.  (A relative 0.1 % would hide e.g. a missed "buy up to the next break" of 0.0009/unit.)
TOL_UNIT, TOL_AMOUNT = 0.00006, 0.006


def produce(ctx):
    out = ctx.work / "cost"
    r = ctx.py("mfg/cost.py", HERE / "bom.csv", "--prices", HERE / "prices.yaml", "--qty", "100", "1000", "--out", out)
    ans = {"exit": r.returncode, "tiers": {}}
    p = out / "summary.csv"
    if p.exists():
        for row in csv.DictReader(p.open(encoding="utf-8")):
            ans["tiers"][int(row["qty"])] = {
                "per_unit": float(row["per_unit"]), "quote": float(row["quote_amount"]),
                "unverified": float(row["unverified_amount"]), "estimate": float(row["estimate_amount"]),
                "missing": int(row["missing_lines"])}
    return ans


def score(ans):
    t = {int(k): v for k, v in (ans.get("tiers") or {}).items()}
    parts = [(0.1, ans.get("exit") == 0 and bool(t) and all(v.get("missing") == 0 for v in t.values()),
              f"退出码 {ans.get('exit')}，缺价格行 {[v.get('missing') for v in t.values()]}")]
    for q in (100, 1000):
        got = t.get(q, {})
        parts.append((0.3, _close(got.get("per_unit"), KEY[q]["per_unit"], TOL_UNIT),
                      f"{q} 台单台 {got.get('per_unit')}（应 {KEY[q]['per_unit']}）"))
    split_ok = all(_close(t.get(q, {}).get(s), KEY[q][s], TOL_AMOUNT)
                   for q in (100, 1000) for s in ("quote", "unverified", "estimate"))
    parts.append((0.3, split_ok, "实查/待核实/估算金额：" + "；".join(
        f"{q}: {[t.get(q, {}).get(s) for s in ('quote', 'unverified', 'estimate')]} 应 "
        f"{[KEY[q][s] for s in ('quote', 'unverified', 'estimate')]}" for q in (100, 1000))))
    return weighted(parts)
