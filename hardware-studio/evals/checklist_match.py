"""Shared grader logic for the compliance checklist tasks (e01, e02).

The answer key is a list of regulation *concepts* (identified by official instrument numbers such as
"2014/53/EU"), written by the grader from regulatory knowledge, not from compliance/data/requirements.yaml.
An item of the checklist "mentions" a concept when its heading or its 依据 (legal basis) line matches."""
import re
from pathlib import Path

import yaml


def items(md: str) -> list[str]:
    """Each checklist item as 'heading + 依据 line'."""
    out = []
    for block in re.split(r"^### ", md, flags=re.M)[1:]:
        lines = block.splitlines()
        basis = next((ln for ln in lines if "**依据**" in ln), "")
        out.append(lines[0] + " " + basis)
    return out


def produce(ctx, product_yaml: Path):
    out = ctx.work / "checklist.md"
    r = ctx.py("compliance/checklist.py", "--product", product_yaml, "--out", out)
    md = out.read_text(encoding="utf-8") if out.exists() else ""
    return {"exit": r.returncode, "items": items(md)}


def score(ans, must, must_not):
    its = ans.get("items") or []
    if ans.get("exit") != 0 or not its:
        return 0.0, f"清单没有生成（退出码 {ans.get('exit')}，条目 {len(its)}）"
    hit = {k: any(re.search(p, t) for t in its) for k, p in must.items()}
    bad = {k: [t[:40] for t in its if re.search(p, t)] for k, p in must_not.items()}
    n = len(must) + len(must_not)
    got = sum(hit.values()) + sum(1 for v in bad.values() if not v)
    miss = [k for k, v in hit.items() if not v]
    wrong = {k: v for k, v in bad.items() if v}
    return round(got / n, 4), (f"共 {len(its)} 条；必须包含 {sum(hit.values())}/{len(must)}，缺 {miss}；"
                               f"不得包含 {len(must_not) - len(wrong)}/{len(must_not)} 干净，误含 {wrong}")
