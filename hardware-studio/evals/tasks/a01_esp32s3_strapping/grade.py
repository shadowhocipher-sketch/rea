"""a01: ESP32-S3 strapping pins with sources (line A)."""
import re
from pathlib import Path

from common import table_rows, has_source, weighted

META = {"id": "a01", "line": "A", "title": "ESP32-S3 strapping 引脚带来源", "kind": "capability"}

# Answer key (independent): ESP32-S3 datasheet, "Strapping Pins" / "Boot Configurations".
KEY_PINS = {0, 3, 45, 46}


def _gpios(text):
    return {int(n) for n in re.findall(r"GPIO\s*(\d+)", text)}


def produce(ctx):
    pages = sorted(Path(ctx.root, "knowledge").rglob("esp32-s3*.md"))
    ans = {"page": None, "strap_row": "", "pins": [], "gpio45_row": "", "gpio3_row": ""}
    if not pages:
        return ans
    page = pages[0]
    ans["page"] = str(page.relative_to(ctx.root))
    rows = table_rows(page)
    for _, cells, raw in rows:
        first = cells[0] if cells else ""
        if re.search(r"strapping", first, re.I) and not ans["strap_row"]:
            ans["strap_row"] = raw
            ans["pins"] = sorted(_gpios(" ".join(cells[1:-1] or cells[1:])))
        if re.search(r"GPIO\s*45\b", first) and not ans["gpio45_row"]:
            ans["gpio45_row"] = raw
        if re.search(r"GPIO\s*3(?!\d)", first):
            if not ans["gpio3_row"] or ("JTAG" in raw and "JTAG" not in ans["gpio3_row"]):
                ans["gpio3_row"] = raw
    return ans


def score(ans):
    pins = set(ans.get("pins") or [])
    strap = ans.get("strap_row") or ""
    g45 = ans.get("gpio45_row") or ""
    g3 = ans.get("gpio3_row") or ""
    return weighted([
        (0.5, pins == KEY_PINS, f"strapping 引脚 {sorted(pins)}，标准答案 {sorted(KEY_PINS)}"),
        (0.2, bool(strap) and has_source(strap), "strapping 行带链接+级别+日期"),
        (0.15, "VDD_SPI" in g45 and has_source(g45), "GPIO45 = VDD_SPI 电压选择并带来源"),
        (0.15, "JTAG" in g3 and has_source(g3) and "未查到" not in g3,
         "GPIO3 = JTAG 信号源选择并带来源（当前库写的是'未查到'则不得分）"),
    ])
