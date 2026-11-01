"""g02: independent audit of source compliance over all fact records in the library (line G)."""
import re
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

from common import table_rows

META = {"id": "g02", "line": "G", "title": "全库事实记录来源合规率", "kind": "capability"}
MARKERS = ("未查到", "估算", "待核实")
URL = re.compile(r"https?://")
LEVEL = re.compile(r"·\s*[SABC](?![A-Za-z])")


def _valid_date(text):
    for y, m, d in re.findall(r"(?<!\d)(20\d\d)-(\d\d)-(\d\d)(?!\d)", text):
        try:
            date(int(y), int(m), int(d))
            return True
        except ValueError:
            pass
    return False


def row_ok(raw):
    return any(k in raw for k in MARKERS) or bool(URL.search(raw) and LEVEL.search(raw) and _valid_date(raw))


def price_ok(e):
    st = e.get("status")
    return (st in ("quote", "unverified", "estimate") and bool(e.get("date"))
            and (st == "estimate" or URL.match(str(e.get("source_url") or "")))
            and (st == "quote" or bool(e.get("basis"))))


def req_ok(r):
    srcs = r.get("sources") or []
    return (any(URL.match(str(s.get("url") or "")) for s in srcs) and all(s.get("level") for s in srcs)
            and r.get("status") in ("已核实", "待核实") and (r.get("status") == "已核实" or bool(r.get("doubts"))))


def produce(ctx):
    root = Path(ctx.root)
    bad, total = Counter(), Counter()
    pages = [p for p in sorted((root / "knowledge").rglob("*.md")) if p.name != "README.md"]
    pages += [root / "cad" / "DFM.md", root / "mfg" / "esp32s3-min-system.md"]
    for p in pages:
        if not p.exists():
            continue
        rel = str(p.relative_to(root))
        for _, _, raw in table_rows(p):
            total[rel] += 1
            bad[rel] += not row_ok(raw)
    for p in sorted((root / "mfg" / "prices").glob("*.yaml")):
        rel = str(p.relative_to(root))
        for e in yaml.safe_load(p.read_text(encoding="utf-8")) or []:
            total[rel] += 1
            bad[rel] += not price_ok(e)
    req = root / "compliance" / "data" / "requirements.yaml"
    if req.exists():
        for r in yaml.safe_load(req.read_text(encoding="utf-8")).get("requirements") or []:
            total["compliance/data/requirements.yaml"] += 1
            bad["compliance/data/requirements.yaml"] += not req_ok(r)
    return {"total": dict(total), "bad": {k: v for k, v in bad.items() if v}}


def score(ans):
    n = sum((ans.get("total") or {}).values())
    b = sum((ans.get("bad") or {}).values())
    if not n:
        return 0.0, "没有找到事实记录"
    worst = sorted((ans.get("bad") or {}).items(), key=lambda kv: -kv[1])[:4]
    return round((n - b) / n, 4), f"合规 {n - b}/{n}；不合规最多：{worst}"
