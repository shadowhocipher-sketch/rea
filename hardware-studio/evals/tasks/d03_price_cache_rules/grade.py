"""d03: price-cache validator rejects entries that break the research method (line D)."""
from common import task_dir, weighted

META = {"id": "d03", "line": "D", "title": "价格缓存来源规则校验", "kind": "capability"}
HERE = task_dir(__file__)

# Answer key: judged by hand (see bad_prices.yaml header)
BAD = ["e:no-url", "e:no-basis", "e:no-date", "e:bad-status"]
GOOD = "e:ok"


def produce(ctx):
    r = ctx.py("mfg/cost.py", "--check-prices", "--prices", HERE / "bad_prices.yaml")
    lib = ctx.py("mfg/cost.py", "--check-prices")
    return {"exit": r.returncode, "output": r.stdout + r.stderr, "lib_exit": lib.returncode}


def score(ans):
    out = ans.get("output") or ""
    parts = [(0.2, ans.get("exit") == 2, f"坏缓存退出码 {ans.get('exit')}（应 2）")]
    parts += [(0.15, k in out, f"点名 {k}") for k in BAD]
    parts.append((0.1, ans.get("exit") == 2 and GOOD not in out, f"合格条目 {GOOD} 没被点名"))
    parts.append((0.1, ans.get("lib_exit") == 0, f"库价格缓存检查退出码 {ans.get('lib_exit')}"))
    return weighted(parts)
