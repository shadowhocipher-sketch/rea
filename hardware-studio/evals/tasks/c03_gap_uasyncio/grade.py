"""c03 (gap probe): can the simulator run a uasyncio firmware?"""
import json
import re

from common import task_dir, weighted

META = {"id": "c03", "line": "C", "title": "【缺口】模拟器支持 uasyncio", "kind": "gap"}
HERE = task_dir(__file__)


def produce(ctx):
    log = ctx.work / "log.json"
    r = ctx.py("sim/run_firmware.py", HERE / "fw_async.py", "--display", "ssd1306", "--seconds", "8",
               "--out", ctx.work / "sim_async.png", "--log", log, timeout=120)
    ans = {"exit": r.returncode, "stdout": r.stdout[-2000:]}
    if log.exists():
        s = json.loads(log.read_text(encoding="utf-8"))["summary"]
        ans.update(stop_reason=s.get("stop_reason"), frames=s.get("frames"), error=s.get("error"),
                   unsupported=s.get("unsupported_apis"))
    m = re.search(r"count (\d+) blinks (\d+)", r.stdout)
    ans["count"], ans["blinks"] = (int(m.group(1)), int(m.group(2))) if m else (None, None)
    return ans


def score(ans):
    return weighted([
        (0.4, ans.get("exit") == 0 and ans.get("stop_reason") == "finished",
         f"退出码 {ans.get('exit')}，stop_reason={ans.get('stop_reason')}，unsupported={ans.get('unsupported')}"),
        (0.3, ans.get("count") == 5, f"count={ans.get('count')}（应 5）"),
        (0.1, ans.get("blinks") in (20, 21), f"blinks={ans.get('blinks')}（应 20–21）"),
        # 6 = 驱动构造时 init_display() 末尾的一次 show()（micropython-lib ssd1306.py@660ddd8 第 77 行）
        #     + 计数任务的 5 次重画。2026-11-01 由统筹更正：原标准答案漏算了构造时这一帧。
        (0.2, ans.get("frames") == 6, f"帧数 {ans.get('frames')}（应 6 = 构造时 1 + 重画 5）"),
    ])
