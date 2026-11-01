"""a02: single-cell Li-ion charge + protection selection with sources (line A)."""
import re
from pathlib import Path

from common import table_rows, has_source, weighted

META = {"id": "a02", "line": "A", "title": "锂电随身设备充电与保护方案", "kind": "capability"}

CHARGERS = ["TP4056", "TP4054", "MCP73831", "MCP73832", "BQ24040", "BQ24072", "BQ25100", "LTC4054", "CN3065", "ETA6003"]
PROTECTORS = ["DW01", "S-8261", "BQ2970", "BQ297", "XB5353", "FS312", "R5421", "AP9101"]
# Answer key (independent, see task.md)
FLOAT_V = 4.2
OVERCHARGE = (4.20, 4.35)
OVERDISCHARGE = (2.30, 2.90)


def _nums(text):
    return [float(x) for x in re.findall(r"(?<![\d.])(\d+\.\d+|\d+)(?![\d.])", text)]


def _first(rows, pred):
    for _, cells, raw in rows:
        if pred(cells, raw):
            return cells, raw
    return None, ""


def produce(ctx):
    power = Path(ctx.root, "knowledge", "power")
    ans = {"charger": None, "charger_row": "", "protector": None, "protector_row": "",
           "cc_row": "", "float_row": "", "ocp_row": "", "odp_row": ""}
    if not power.is_dir():
        return ans
    sel = power / "selection.md"
    rows = table_rows(sel) if sel.exists() else []
    for name in CHARGERS:
        _, raw = _first(rows, lambda c, r: name in r and "充电" in r)
        if raw:
            ans["charger"], ans["charger_row"] = name, raw
            break
    for name in PROTECTORS:
        _, raw = _first(rows, lambda c, r: name in r and "保护" in r)
        if raw:
            ans["protector"], ans["protector_row"] = name, raw
            break
    all_rows = [r for p in sorted(power.glob("*.md")) for r in table_rows(p)]
    _, ans["cc_row"] = _first(all_rows, lambda c, r: "CC" in r and re.search(r"5\.1\s*k", r) is not None)

    def page_rows(name):
        if not name:
            return []
        stem = name.lower().split("-")[0][:4]
        return [r for p in sorted(power.glob("*.md")) if stem in p.stem.lower() for r in table_rows(p)]

    _, ans["float_row"] = _first(page_rows(ans["charger"]),
                                 lambda c, r: re.search(r"浮充|恒压|充电电压|终止电压|regulat", c[0], re.I) is not None)
    prot = page_rows(ans["protector"])
    _, ans["ocp_row"] = _first(prot, lambda c, r: "过充" in c[0] and re.search(r"保护|检测", c[0]) is not None)
    _, ans["odp_row"] = _first(prot, lambda c, r: "过放" in c[0] and re.search(r"保护|检测", c[0]) is not None)
    return ans


def _value_in(row, lo, hi):
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    val = cells[1] if len(cells) > 1 else ""
    return any(lo <= v <= hi for v in _nums(val))


def score(ans):
    fr, ocp, odp = ans.get("float_row") or "", ans.get("ocp_row") or "", ans.get("odp_row") or ""
    ch, chr_ = ans.get("charger"), ans.get("charger_row") or ""
    pr, prr = ans.get("protector"), ans.get("protector_row") or ""
    cc = ans.get("cc_row") or ""
    return weighted([
        (0.2, ch in CHARGERS and ch in chr_ and "充电" in chr_ and has_source(chr_),
         f"选型表推荐充电芯片 {ch} 并带来源"),
        (0.2, pr in PROTECTORS and pr in prr and "保护" in prr and has_source(prr),
         f"选型表推荐保护 IC {pr} 并带来源"),
        (0.2, "CC" in cc and re.search(r"5\.1\s*k", cc) is not None and has_source(cc), "CC 下拉 5.1 kΩ 并带来源"),
        (0.2, bool(fr) and _value_in(fr, FLOAT_V - 0.001, FLOAT_V + 0.001) and has_source(fr),
         "充电芯片恒压电压含 4.2 V 并带来源"),
        (0.2, bool(ocp and odp) and _value_in(ocp, *OVERCHARGE) and _value_in(odp, *OVERDISCHARGE)
         and has_source(ocp) and has_source(odp), "保护 IC 过充 4.20–4.35 V、过放 2.3–2.9 V 并带来源"),
    ])
