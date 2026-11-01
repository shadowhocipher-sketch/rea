#!/usr/bin/env python3
"""Run the capability self-test (evals/tasks/*) and record the score.

    python evals/run.py                                   # all tasks, writes evals/results/run-<date>.json/.md
    python evals/run.py --label baseline-2026-11-01       # name the result files
    python evals/run.py --only a01 d01                    # subset (ids or directory-name prefixes)
    python evals/run.py --compare evals/results/baseline-2026-11-01.json   # show per-task change

Each task scores 0..1, total out of the number of tasks (20).  A task that crashes scores 0 with the
exception as its reason.  Exit code 0 when every task ran (whatever the score), 1 if a grader crashed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import platform
import sys
import time
import traceback
from pathlib import Path

EVALS = Path(__file__).resolve().parent
sys.path.insert(0, str(EVALS))
from common import ROOT, new_ctx  # noqa: E402

TASKS = EVALS / "tasks"
RESULTS = EVALS / "results"


def load_task(d: Path):
    spec = importlib.util.spec_from_file_location(f"eval_{d.name}", d / "grade.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def task_dirs(only=None):
    dirs = sorted(p for p in TASKS.iterdir() if (p / "grade.py").exists())
    if only:
        dirs = [d for d in dirs if any(d.name == o or d.name.startswith(o) for o in only)]
    return dirs


def run_one(d: Path) -> dict:
    t0 = time.time()
    rec = {"dir": d.name}
    ctx, td = new_ctx(ROOT)
    try:
        mod = load_task(d)
        rec.update(mod.META)
        ans = mod.produce(ctx)
        s, reason = mod.score(ans)
        rec["score"], rec["reason"], rec["crashed"] = round(float(s), 4), reason, False
    except Exception as exc:  # a crashing grader scores 0 and is reported
        rec.setdefault("id", d.name.split("_")[0])
        rec["score"], rec["crashed"] = 0.0, True
        rec["reason"] = f"评分脚本异常：{type(exc).__name__}: {exc}"
        rec["traceback"] = traceback.format_exc()[-1500:]
    finally:
        td.cleanup()
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def to_markdown(res: dict, prev: dict | None) -> str:
    pv = {r["id"]: r["score"] for r in (prev or {}).get("tasks", [])}
    L = [f"# 能力库自测：{res['label']}", "",
         f"日期 {res['date']}；总分 **{res['total']:.2f} / {res['max']}**"
         f"（能力题 {res['by_kind'].get('capability', 0):.2f}，缺口题 {res['by_kind'].get('gap', 0):.2f}）；"
         f"用时 {res['seconds']:.0f} s。", ""]
    if prev:
        L += [f"对比 {prev.get('label')}：{prev.get('total'):.2f} → {res['total']:.2f}", ""]
    L += ["| 题 | 线 | 类型 | 考什么 | 得分 | " + ("变化 | " if prev else "") + "理由 |",
          "|---|---|---|---|---:|" + ("---:|" if prev else "") + "---|"]
    for r in res["tasks"]:
        delta = ""
        if prev:
            d = r["score"] - pv.get(r["id"], 0.0) if r["id"] in pv else None
            delta = ("新题" if d is None else f"{d:+.2f}") + " | "
        reason = str(r.get("reason", "")).replace("|", "/").replace("\n", " ")
        L.append(f"| {r['id']} | {r.get('line', '')} | {'缺口' if r.get('kind') == 'gap' else '能力'} | "
                 f"{r.get('title', r['dir'])} | {r['score']:.2f} | {delta}{reason} |")
    L += ["", "按线汇总：" + "，".join(f"{k} {v['score']:.2f}/{v['n']}" for k, v in res["by_line"].items()), ""]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", nargs="*", help="task ids / directory prefixes")
    ap.add_argument("--label", help="result file name (default run-<date>-<time>)")
    ap.add_argument("--compare", help="earlier result JSON to diff against")
    ap.add_argument("--no-write", action="store_true", help="print only")
    a = ap.parse_args(argv)
    now = dt.datetime.now()
    label = a.label or f"run-{now:%Y-%m-%d-%H%M}"
    t0 = time.time()
    tasks = []
    for d in task_dirs(a.only):
        r = run_one(d)
        tasks.append(r)
        print(f"{r['id']:>4} {r['score']:.2f}  {r.get('title', d.name)}  ({r['seconds']} s)", flush=True)
        if r.get("crashed"):
            print("      " + r["reason"], flush=True)
    by_line, by_kind = {}, {}
    for r in tasks:
        bl = by_line.setdefault(r.get("line", "?"), {"score": 0.0, "n": 0})
        bl["score"] += r["score"]
        bl["n"] += 1
        by_kind[r.get("kind", "capability")] = by_kind.get(r.get("kind", "capability"), 0.0) + r["score"]
    res = {"label": label, "date": now.strftime("%Y-%m-%d %H:%M"), "max": len(tasks),
           "total": round(sum(r["score"] for r in tasks), 4), "by_line": dict(sorted(by_line.items())),
           "by_kind": by_kind, "seconds": round(time.time() - t0, 1),
           "env": {"python": platform.python_version(), "platform": platform.platform()}, "tasks": tasks}
    prev = json.loads(Path(a.compare).read_text(encoding="utf-8")) if a.compare else None
    md = to_markdown(res, prev)
    print()
    print(md)
    if not a.no_write:
        RESULTS.mkdir(parents=True, exist_ok=True)
        (RESULTS / f"{label}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        (RESULTS / f"{label}.md").write_text(md, encoding="utf-8")
        print(f"写出 {RESULTS / (label + '.json')} 和 .md")
    return 1 if any(r.get("crashed") for r in tasks) else 0


if __name__ == "__main__":
    sys.exit(main())
