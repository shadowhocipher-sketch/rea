"""d02 (gap probe): share of BOM cost backed by real quotes (status: quote) >= 50 %."""
import csv

from common import weighted, clamp01

META = {"id": "d02", "line": "D", "title": "【缺口】成本实查占比 ≥ 50%", "kind": "gap"}
BOM = "mfg/examples/generic-esp32s3-gadget.bom.csv"
TARGET = 0.5


def produce(ctx):
    out = ctx.work / "cost"
    r = ctx.py("mfg/cost.py", BOM, "--qty", "100", "1000", "--out", out)
    shares = {}
    p = out / "summary.csv"
    if p.exists():
        for row in csv.DictReader(p.open(encoding="utf-8")):
            shares[int(row["qty"])] = float(row["quote_share"])
    return {"exit": r.returncode, "quote_share": shares}


def score(ans):
    sh = {int(k): v for k, v in (ans.get("quote_share") or {}).items()}
    if ans.get("exit") != 0 or set(sh) != {100, 1000}:
        return 0.0, f"成本工具没有给出两档结果（退出码 {ans.get('exit')}）"
    s = sum(clamp01(v / TARGET) for v in sh.values()) / 2
    return round(s, 4), "实查占比 " + "，".join(f"{q} 台 {v:.1%}" for q, v in sorted(sh.items())) + \
        f"（目标 ≥ {TARGET:.0%}；得分 = min(1, 占比/{TARGET})，两档平均）"
