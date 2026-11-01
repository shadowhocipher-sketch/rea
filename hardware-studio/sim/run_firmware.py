#!/usr/bin/env python3
"""Run MicroPython display firmware on the desktop and save what the screen shows.

Example::

    python sim/run_firmware.py products/desk-creature-standin/eyes.py \\
        --display ssd1306 --seconds 12 --out products/desk-creature-standin/sim_eyes.gif

Import use::

    import sys; sys.path.insert(0, "sim")
    from run_firmware import run_firmware
    res = run_firmware("eyes.py", display="ssd1306", seconds=5, out="sim_eyes.png")

Exit status: 0 when frames were captured and the run ended normally (frame/time
limit, firmware finished, or slept forever), 1 when the firmware raised an
exception or nothing was captured, 2 for usage errors.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from mpsim import run  # noqa: E402

OK_REASONS = ("frame_limit", "time_limit", "finished", "sleep_forever", "sys_exit", "max_boots")


def run_firmware(firmware, display=None, width=None, height=None, frames=None, seconds=None,
                 out=None, seed=0, inputs=None, png_mode="sheet", speed=1.0, scale=None,
                 oled_color="white", glow=True, epaper_flash=True, wall_timeout=60.0,
                 echo=True, log=None):
    """Run firmware, write outputs (list or single path), return the SimResult."""
    res = run(firmware, display=display, max_frames=frames, max_seconds=seconds, seed=seed,
              inputs=inputs, wall_timeout_s=wall_timeout, echo=echo, width=width, height=height)
    outs = [out] if isinstance(out, str) else list(out or [])
    for o in outs:
        res.save(o, png_mode=png_mode, speed=speed, scale=scale, oled_color=oled_color,
                 glow=glow, epaper_flash=epaper_flash)
    if log:
        with open(log, "w", encoding="utf-8") as f:
            json.dump({"summary": res.summary(), "log": res.log[:2000]}, f, ensure_ascii=False,
                      indent=1, default=str)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("firmware", help="MicroPython .py file to run (unmodified)")
    ap.add_argument("--display", choices=["ssd1306", "st7789", "epaper"], default=None,
                    help="which display's frames to render (default: first one used)")
    ap.add_argument("--width", type=int, help="expected panel width (warns on mismatch)")
    ap.add_argument("--height", type=int, help="expected panel height (warns on mismatch)")
    ap.add_argument("--frames", type=int, help="stop after N captured frames")
    ap.add_argument("--seconds", type=float, help="stop after S seconds of VIRTUAL time")
    ap.add_argument("--out", action="append", default=[],
                    help="output .gif or .png (repeatable); name must start with sim_")
    ap.add_argument("--seed", type=int, default=0, help="random seed (reproducible runs)")
    ap.add_argument("--inputs", help="stimulus file (.json/.yaml): buttons, touch, ADC, I2C devices")
    ap.add_argument("--png-mode", choices=["sheet", "last", "first"], default="sheet")
    ap.add_argument("--speed", type=float, default=1.0, help="GIF playback speed factor")
    ap.add_argument("--scale", type=int, help="pixel magnification")
    ap.add_argument("--oled-color", choices=["white", "blue", "yellow", "yellow-blue"], default="white")
    ap.add_argument("--no-glow", action="store_true", help="disable OLED glow effect")
    ap.add_argument("--no-flash", action="store_true", help="no e-paper full-refresh flash frames")
    ap.add_argument("--wall-timeout", type=float, default=60.0, help="real-time safety limit (s)")
    ap.add_argument("--log", help="write run summary + call log as JSON")
    ap.add_argument("--quiet", action="store_true", help="do not echo firmware print() output")
    a = ap.parse_args(argv)
    if not os.path.isfile(a.firmware):
        ap.error("firmware file not found: %s" % a.firmware)
    for o in a.out:
        if not o.lower().endswith((".gif", ".png")):
            ap.error("--out must end with .gif or .png: %s" % o)
    res = run_firmware(a.firmware, display=a.display, width=a.width, height=a.height,
                       frames=a.frames, seconds=a.seconds, out=a.out, seed=a.seed,
                       inputs=a.inputs, png_mode=a.png_mode, speed=a.speed, scale=a.scale,
                       oled_color=a.oled_color, glow=not a.no_glow, epaper_flash=not a.no_flash,
                       wall_timeout=a.wall_timeout, echo=not a.quiet, log=a.log)
    s = res.summary()
    print("--- mpsim summary ---", file=sys.stderr)
    for k in ("stop_reason", "virtual_ms", "boots", "display", "frames", "frame_size", "outputs",
              "files_written"):
        print("%-12s %s" % (k, s[k]), file=sys.stderr)
    if s["stats"].get("epaper"):
        print("%-12s %s" % ("epaper", s["stats"]["epaper"]), file=sys.stderr)
    for w in s["warnings"]:
        print("warning:     %s" % w, file=sys.stderr)
    if s["unsupported_apis"]:
        print("unsupported: %s" % ", ".join(s["unsupported_apis"]), file=sys.stderr)
    if res.error:
        print("firmware raised:\n" + res.error, file=sys.stderr)
    ok = res.stop_reason in OK_REASONS and res.frames
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
