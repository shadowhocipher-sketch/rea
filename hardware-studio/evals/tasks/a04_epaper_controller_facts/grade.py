"""a04: SSD1680-class e-paper controller driver facts with sources (line A)."""
import re
from pathlib import Path

from common import table_rows, has_source, weighted

META = {"id": "a04", "line": "A", "title": "墨水屏控制器 BUSY/深睡/命令字", "kind": "capability"}

# Answer key (SSD1680 datasheet pin description + command table)
CHECKS = {
    "busy_high": lambda c, r: "BUSY" in c[0] and re.search(r"高\s*=\s*忙|高电平.{0,6}忙|high.{0,12}busy", r, re.I),
    "sleep_exit_hw_reset": lambda c, r: re.search(r"深睡|deep sleep", r, re.I)
                                        and re.search(r"硬件复位|hardware reset|HW ?reset", r, re.I),
    "cmd_deep_sleep_10h": lambda c, r: re.search(r"\b(10h|0x10)\b", r, re.I) and re.search(r"深睡|deep sleep", r, re.I),
    "cmd_master_activation_20h": lambda c, r: re.search(r"\b(20h|0x20)\b", r, re.I)
                                              and re.search(r"Master Activation|激活", r, re.I),
}
WEIGHTS = {"busy_high": 0.3, "sleep_exit_hw_reset": 0.3, "cmd_deep_sleep_10h": 0.2, "cmd_master_activation_20h": 0.2}


def produce(ctx):
    pages = sorted(Path(ctx.root, "knowledge").rglob("*ssd168*.md"))
    rows = [r for p in pages for r in table_rows(p)]
    ans = {"pages": [str(p.relative_to(ctx.root)) for p in pages]}
    for name, pred in CHECKS.items():
        # match on the fact cells only (not the source cell, whose link text may mention a command)
        hits = [raw for _, cells, raw in rows if len(cells) > 1 and pred(cells, " | ".join(cells[:-1]))]
        sourced = [h for h in hits if has_source(h)]
        ans[name] = (sourced or hits or [""])[0]
    return ans


def _fact_ok(name, raw):
    cells = [c.strip() for c in (raw or "").strip().strip("|").split("|")]
    return len(cells) > 1 and bool(CHECKS[name](cells, " | ".join(cells[:-1]))) and has_source(raw)


def score(ans):
    return weighted([(WEIGHTS[k], _fact_ok(k, ans.get(k)), k) for k in CHECKS])
