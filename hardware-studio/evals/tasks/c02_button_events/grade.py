"""c02: debounced click/double/long/hold_end/touch events from the buttons template (line C)."""
import re

from common import task_dir, weighted

META = {"id": "c02", "line": "C", "title": "按键/触摸消抖模板事件时序", "kind": "capability"}
HERE = task_dir(__file__)

# Answer key, hand-computed (see task.md)
KEY = [("button", "click", 1405), ("button", "double", 3305), ("button", "long", 5725),
       ("button", "hold_end", 6225), ("touch", "click", 8475)]
TOL_MS = 50


def produce(ctx):
    r = ctx.py("sim/run_firmware.py", "firmware/templates/buttons.py", "--inputs", HERE / "stimulus.json",
               "--seconds", "9", timeout=120)
    ev = [(m.group(1), m.group(2), int(m.group(3)))
          for m in re.finditer(r"EVENT (\w+) (\w+) t=(\d+)", r.stdout)]
    return {"exit": r.returncode, "events": ev}


def score(ans):
    ev = [tuple(e) for e in ans.get("events", [])]
    seq_ok = [(a, b) for a, b, _ in ev] == [(a, b) for a, b, _ in KEY]
    parts = [(0.5, seq_ok, f"事件序列 {[(a, b) for a, b, _ in ev]}")]
    for i, (src, kind, t) in enumerate(KEY):
        got = ev[i][2] if i < len(ev) and ev[i][:2] == (src, kind) else None
        parts.append((0.1, got is not None and abs(got - t) <= TOL_MS, f"{src} {kind} t={got}（应 {t}±{TOL_MS}）"))
    return weighted(parts)
