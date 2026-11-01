"""e03 (gap probe): share of compliance entries still marked 待核实 should be <= 20 %."""
from pathlib import Path

import yaml

from common import clamp01

META = {"id": "e03", "line": "E", "title": "【缺口】法规待核实比例 ≤ 20%", "kind": "gap"}
TARGET = 0.20


def produce(ctx):
    d = yaml.safe_load(Path(ctx.root, "compliance/data/requirements.yaml").read_text(encoding="utf-8"))
    reqs = d.get("requirements") or []
    unv = [r for r in reqs if r.get("status") == "待核实"]
    return {"total": len(reqs), "unverified": len(unv),
            "unverified_without_doubts": [r["id"] for r in unv if not r.get("doubts")],
            "without_source_url": [r["id"] for r in reqs
                                   if not any(str(s.get("url", "")).startswith("http") for s in r.get("sources") or [])]}


def score(ans):
    n, u = ans.get("total", 0), ans.get("unverified", 0)
    if not n:
        return 0.0, "没有合规条目"
    if ans.get("unverified_without_doubts") or ans.get("without_source_url"):
        return 0.0, (f"待核实但没写疑点：{ans.get('unverified_without_doubts')}；"
                     f"没有来源链接：{ans.get('without_source_url')}")
    r = u / n
    return round(clamp01(TARGET / r) if r > 0 else 1.0, 4), \
        f"待核实 {u}/{n} = {r:.1%}（目标 ≤ {TARGET:.0%}；得分 = min(1, {TARGET}/比例)）"
