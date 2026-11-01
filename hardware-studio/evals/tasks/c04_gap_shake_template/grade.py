"""c04 (gap probe): accelerometer shake-detection firmware template exists and runs in the simulator."""
import json
import re
from pathlib import Path

from common import task_dir, weighted

META = {"id": "c04", "line": "C", "title": "【缺口】加速度计摇一摇固件模板", "kind": "gap"}
HERE = task_dir(__file__)
PAT = re.compile(r"shake|摇一摇|accel|imu|lis3dh", re.I)


def produce(ctx):
    tdir = Path(ctx.root, "firmware", "templates")
    found = None
    for p in sorted(tdir.glob("*.py")):
        head = p.read_text(encoding="utf-8")[:3000]
        if PAT.search(p.stem) or (re.search(r"shake|摇一摇", head, re.I) and PAT.search(head)):
            found = p
            break
    ans = {"template": None, "status_header": False, "stop_reason": None}
    if not found:
        return ans
    ans["template"] = str(found.relative_to(ctx.root))
    ans["status_header"] = bool(re.search(r"Verification status|验证状态", found.read_text(encoding="utf-8")[:3000]))
    log = ctx.work / "log.json"
    r = ctx.py("sim/run_firmware.py", found, "--inputs", HERE / "stimulus.json", "--seconds", "5", "--log", log,
               timeout=120)
    ans["exit"] = r.returncode
    if log.exists():
        ans["stop_reason"] = json.loads(log.read_text(encoding="utf-8"))["summary"].get("stop_reason")
    return ans


def score(ans):
    sr = ans.get("stop_reason")
    return weighted([
        (0.4, bool(ans.get("template")), f"模板 {ans.get('template')}"),
        (0.3, bool(ans.get("status_header")), "文件头有验证状态"),
        (0.3, sr is not None and sr != "exception", f"模拟器 stop_reason={sr}"),
    ])
