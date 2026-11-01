"""a03 (gap probe): knowledge pages for MCP73831 and a Li-ion fuel gauge exist and are sourced."""
import re
from pathlib import Path

from common import table_rows, has_source, weighted

META = {"id": "a03", "line": "A", "title": "【缺口】MCP73831 与电量计器件页", "kind": "gap"}

GAUGES = ["MAX17048", "MAX17049", "MAX17043", "MAX17055", "CW2015", "CW2017", "BQ27441", "BQ27220", "LC709203", "STC3115"]


def _page_stats(ctx, page):
    rows = table_rows(page)
    sourced = sum(1 for _, _, raw in rows if has_source(raw))
    r = ctx.py("knowledge/check_sources.py", str(page))
    return {"page": str(page.relative_to(ctx.root)), "sourced_rows": sourced, "check_ok": r.returncode == 0}


def produce(ctx):
    kn = Path(ctx.root, "knowledge")
    ans = {"mcp73831": None, "gauge": None}
    pages = sorted(p for p in kn.rglob("*.md") if p.name not in ("README.md", "selection.md"))
    for p in pages:
        head = p.read_text(encoding="utf-8")[:400]
        name = p.stem.lower() + " " + head
        if ans["mcp73831"] is None and re.search(r"mcp7383[12]", name, re.I):
            ans["mcp73831"] = _page_stats(ctx, p)
        if ans["gauge"] is None and (any(g.lower() in name.lower() for g in GAUGES)
                                     or re.search(r"电量计|fuel.?gauge", head, re.I)):
            ans["gauge"] = _page_stats(ctx, p)
    return ans


def _ok(st):
    return bool(st) and st.get("check_ok") and st.get("sourced_rows", 0) >= 5


def score(ans):
    m, g = ans.get("mcp73831"), ans.get("gauge")
    return weighted([
        (0.5, _ok(m), f"MCP73831 器件页：{m['page'] + '，带来源行 ' + str(m['sourced_rows']) if m else '没有'}"),
        (0.5, _ok(g), f"电量计器件页：{g['page'] + '，带来源行 ' + str(g['sourced_rows']) if g else '没有'}"),
    ])
