"""g01: the source checker flags exactly the rows that break the research method (line G)."""
import re

from common import task_dir, weighted

META = {"id": "g01", "line": "G", "title": "来源检查器抓出缺来源的行", "kind": "capability"}
HERE = task_dir(__file__)

# Answer key: judged by hand against research-method sections 3-4
MUST_FLAG = ["深睡电流", "最大频率", "封装", "典型电流", "输入电压"]
MUST_PASS = ["工作电压", "参考价", "内部上拉", "论坛说法", "代码块示例"]


def produce(ctx):
    r = ctx.py("knowledge/check_sources.py", HERE / "fixture_facts.md")
    flagged = []
    for ln in r.stdout.splitlines():
        m = re.search(r":\d+: [^|]*\|\s*([^|]+?)\s*\|", ln)
        if m:
            flagged.append(m.group(1))
    return {"exit": r.returncode, "flagged": flagged}


def score(ans):
    fl = set(ans.get("flagged") or [])
    return weighted([(0.12, k in fl, f"报出 {k}") for k in MUST_FLAG] +
                    [(0.08, k not in fl, f"没误报 {k}") for k in MUST_PASS])
