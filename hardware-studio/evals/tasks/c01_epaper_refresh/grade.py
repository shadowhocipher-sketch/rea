"""c01: e-paper refresh counts / timing in the simulator vs hand-computed values (line C)."""
import json

from common import task_dir, weighted

META = {"id": "c01", "line": "C", "title": "墨水屏固件刷新次数与节奏", "kind": "capability"}
HERE = task_dir(__file__)

# Answer key (hand-computed from fw_epaper_counter.py):
FULL, PARTIAL = 3, 8
REFRESH_MS = 3 * 2500 + 8 * 400            # 10700
VIRTUAL_MS = 10 * 60_000 + REFRESH_MS      # 610700
FRAMES, SIZE = 11, [200, 200]


def produce(ctx):
    log = ctx.work / "log.json"
    r = ctx.py("sim/run_firmware.py", HERE / "fw_epaper_counter.py", "--display", "epaper", "--seconds", "700",
               "--out", ctx.work / "sim_counter.png", "--log", log, timeout=300)
    ans = {"exit": r.returncode, "console_done": "done 10" in r.stdout}
    if log.exists():
        s = json.loads(log.read_text(encoding="utf-8"))["summary"]
        ep = list((s.get("stats", {}).get("epaper") or {}).values())
        ep = ep[0] if ep else {}
        ans.update(stop_reason=s.get("stop_reason"), virtual_ms=s.get("virtual_ms"), frames=s.get("frames"),
                   frame_size=s.get("frame_size"), full=ep.get("full"), partial=ep.get("partial"),
                   refresh_ms=ep.get("refresh_ms"))
    return ans


def score(ans):
    vm = ans.get("virtual_ms")
    return weighted([
        (0.2, ans.get("exit") == 0 and ans.get("stop_reason") == "finished" and ans.get("console_done"),
         f"退出码 {ans.get('exit')}，stop_reason={ans.get('stop_reason')}，done 10={ans.get('console_done')}"),
        (0.2, ans.get("full") == FULL, f"全刷 {ans.get('full')}（应 {FULL}）"),
        (0.2, ans.get("partial") == PARTIAL, f"局刷 {ans.get('partial')}（应 {PARTIAL}）"),
        (0.1, ans.get("refresh_ms") == REFRESH_MS, f"刷新耗时 {ans.get('refresh_ms')} ms（应 {REFRESH_MS}）"),
        (0.1, vm is not None and abs(vm - VIRTUAL_MS) <= 100, f"虚拟时间 {vm} ms（应 {VIRTUAL_MS}±100）"),
        (0.2, ans.get("frames") == FRAMES and ans.get("frame_size") == SIZE,
         f"帧 {ans.get('frames')} {ans.get('frame_size')}（应 {FRAMES} {SIZE}）"),
    ])
