"""b02: interference check reports the right pairs and volumes (hand-computed) (line B)."""
import json

from common import task_dir, weighted, rel_close

META = {"id": "b02", "line": "B", "title": "干涉检查报对碰撞对和体积", "kind": "capability"}
HERE = task_dir(__file__)

# Answer key (hand-computed from the box coordinates in enclosure.yaml)
KEY = {frozenset(("module_a", "module_b")): 400.0, frozenset(("bottom", "module_d")): 100.0}
KEY_TOTAL = 500.0


def produce(ctx):
    out = ctx.work / "b02"
    r = ctx.py("cad/build_enclosure.py", HERE / "enclosure.yaml", "--out", out, "--no-slice", "--no-preview")
    ans = {"exit": r.returncode, "ok": None, "pairs": [], "total": None}
    rep = out / "check_report.json"
    if rep.exists():
        d = json.loads(rep.read_text(encoding="utf-8"))
        ans["ok"] = d.get("ok")
        inter = d.get("interference", {})
        ans["pairs"] = [[p["a"], p["b"], p["volume"]] for p in inter.get("pairs", []) if not p.get("ignored")]
        ans["total"] = inter.get("total")
    return ans


def score(ans):
    got = {frozenset((a, b)): v for a, b, v in ans.get("pairs", [])}
    ab = got.get(frozenset(("module_a", "module_b")))
    bd = got.get(frozenset(("bottom", "module_d")))
    extra = [sorted(k) for k in got if k not in KEY]
    return weighted([
        (0.2, ans.get("exit") == 1 and ans.get("ok") is False, f"退出码 {ans.get('exit')}，ok={ans.get('ok')}"),
        (0.3, ab is not None and rel_close(ab, 400.0, 0.02), f"module_a×module_b = {ab}（应 400）"),
        (0.3, bd is not None and rel_close(bd, 100.0, 0.02), f"bottom×module_d = {bd}（应 100）"),
        (0.2, not extra and rel_close(ans.get("total"), KEY_TOTAL, 0.02),
         f"多报的对 {extra}，总量 {ans.get('total')}（应 500，接触不算）"),
    ])
