"""Run a MicroPython firmware file on the desktop with simulated modules.

Usage from Python::

    from mpsim import run
    res = run("main.py", display="ssd1306", max_seconds=10, seed=1)
    res.save("sim_out.gif")

The firmware is executed unmodified with ``__name__ == "__main__"``.  While it
runs, ``sys.modules`` maps MicroPython module names (machine, time, utime,
random, framebuf, micropython, esp32, gc, network, asyncio, ssd1306, st7789, epaper ...)
to the simulated implementations; the originals are restored afterwards.
"""

import builtins
import io
import os
import shutil
import sys
import tempfile
import threading
import traceback
import types
from pathlib import Path

from . import runtime as _rt
from . import stimulus as _stim
from . import mp_time, mp_random, mp_framebuf, mp_machine, mp_esp32, mp_misc
from . import mp_ssd1306, mp_st7789, mp_epaper, mp_fonts, mp_asyncio, render
from .runtime import unsupported as _r_unsupported
from .runtime import SimRuntime, SimStop, SimReboot

SIM_MODULES = {
    "machine": mp_machine,
    "time": mp_time, "utime": mp_time,
    "random": mp_random, "urandom": mp_random,
    "framebuf": mp_framebuf,
    "micropython": mp_misc.micropython,
    "esp32": mp_esp32,
    "gc": mp_misc.gc,
    "network": mp_misc.network,
    "ssd1306": mp_ssd1306,
    "st7789": mp_st7789, "st7789py": mp_st7789,
    "epaper": mp_epaper, "ssd1680": mp_epaper, "ssd1681": mp_epaper, "ssd168x": mp_epaper,
    "asyncio": mp_asyncio, "uasyncio": mp_asyncio,
}

# MicroPython "u"-prefixed names that behave like the CPython module closely enough.
ALIASES = {
    "ustruct": "struct", "ujson": "json", "ubinascii": "binascii", "ucollections": "collections",
    "uerrno": "errno", "uio": "io", "uos": "os", "uhashlib": "hashlib", "uarray": "array",
    "ure": "re", "uzlib": "zlib", "uselect": "select", "usys": "sys", "uctypes": None,
}

# MicroPython modules that are known but NOT simulated: importing works, any use
# raises SimUnsupported with a clear message (and is listed in the result).
UNSUPPORTED_MODULES = (
    "bluetooth", "ubluetooth", "aioble", "usocket", "urequests",
    "requests", "umqtt", "umqtt.simple", "espnow", "aioespnow", "webrepl", "ntptime", "dht",
    "onewire", "ds18x20", "neopixel", "machine.I2S", "uctypes", "btree", "deflate", "cryptolib",
)

DISPLAY_KINDS = {"ssd1306": "oled", "oled": "oled", "st7789": "lcd", "lcd": "lcd",
                 "epaper": "epaper", "ssd1680": "epaper", "ssd1681": "epaper"}

COPY_MAX_FILE = 2 * 1024 * 1024
COPY_MAX_TOTAL = 50 * 1024 * 1024


def _unsupported_module(name):
    m = types.ModuleType(name)
    m.__doc__ = "mpsim: module %r is not simulated" % name

    def __getattr__(attr):
        raise _r_unsupported(name, attr)
    m.__getattr__ = __getattr__
    return m


_SANDBOXES = []


def _new_sandbox():
    """Temporary device filesystem; removed when the Python process exits."""
    d = tempfile.mkdtemp(prefix="mpsim_fs_")
    if not _SANDBOXES:
        import atexit
        atexit.register(lambda: [shutil.rmtree(x, ignore_errors=True) for x in _SANDBOXES])
    _SANDBOXES.append(d)
    return d


def _inject(thread, exc):
    """Raise ``exc`` asynchronously in ``thread`` (best effort, CPython only)."""
    import ctypes
    ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(thread.ident), ctypes.py_object(exc))


class _Tee(io.TextIOBase):
    def __init__(self, echo, limit=200_000):
        self.echo = echo
        self.buf = []
        self.size = 0
        self.limit = limit
        self.real = sys.stdout

    def write(self, s):
        if self.size < self.limit:
            self.buf.append(s)
            self.size += len(s)
        if self.echo:
            self.real.write(s)
        return len(s)

    def flush(self):
        if self.echo:
            self.real.flush()


class SimResult:
    def __init__(self, rt, firmware, display_kind, error, console, files_written, sandbox):
        self.rt = rt
        self.firmware = str(firmware)
        self.all_frames = list(rt.frames)
        self.stop_reason = rt.stop_reason
        self.virtual_ms = rt.now_us / 1000.0
        self.boots = rt.boot_count
        self.warnings = list(rt.warnings)
        self.unsupported = list(rt.unsupported)
        self.error = error
        self.console = console
        self.files_written = files_written
        self.sandbox = sandbox
        self.outputs = []
        kind = display_kind
        if kind is None and self.all_frames:
            kind = self.all_frames[0].kind
        self.display_kind = kind
        sel = [f for f in self.all_frames if f.kind == kind]
        ids = []
        for f in sel:
            if f.display_id not in ids:
                ids.append(f.display_id)
        self.display_id = ids[0] if ids else None
        self.frames = [f for f in sel if f.display_id == self.display_id]
        if len(ids) > 1:
            self.warnings.append("several %s displays captured %s; rendering %s" % (kind, ids, self.display_id))

    # convenient views --------------------------------------------------------
    @property
    def log(self):
        return self.rt.log

    @property
    def log_counts(self):
        return self.rt.log_counts

    def pin_history(self, pin):
        st = self.rt.pins.get(pin)
        return [] if st is None else [(t / 1000.0, v) for t, v in st["history"]]

    def summary(self):
        f = self.frames
        return {
            "firmware": self.firmware,
            "stop_reason": self.stop_reason,
            "virtual_ms": round(self.virtual_ms, 3),
            "boots": self.boots,
            "frames_total": len(self.all_frames),
            "display": self.display_id,
            "display_kind": self.display_kind,
            "frames": len(f),
            "frame_size": None if not f else [int(f[0].rgb.shape[1]), int(f[0].rgb.shape[0])],
            "warnings": self.warnings,
            "unsupported_apis": self.unsupported,
            "error": self.error,
            "log_counts": self.rt.log_counts,
            "stats": self.rt.stats,
            "i2c": {hex(k): v for k, v in self.rt.i2c_stats.items()},
            "files_written": self.files_written,
            "outputs": self.outputs,
        }

    def save(self, path, *, png_mode="sheet", speed=1.0, scale=None, oled_color="white", glow=True,
             epaper_flash=True, enforce_prefix=True):
        """Write a .gif or .png of the selected display's frames; returns the path written."""
        p = Path(path)
        if enforce_prefix and not p.name.startswith("sim_"):
            p = p.with_name("sim_" + p.name)
            self.warnings.append("output renamed to %s (files must start with sim_)" % p.name)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not self.frames:
            raise ValueError("no frames captured for display kind %r (stop reason: %s, error: %s)"
                             % (self.display_kind, self.stop_reason, self.error))
        opts = {"scale": scale, "oled_color": oled_color, "glow": glow, "epaper_flash": epaper_flash}
        if p.suffix.lower() == ".gif":
            render.save_gif(self.frames, str(p), self.rt.now_us, opts, speed=speed)
        elif p.suffix.lower() == ".png":
            render.save_png(self.frames, str(p), opts, mode=png_mode)
        else:
            raise ValueError("output must be .gif or .png")
        self.outputs.append(str(p))
        return str(p)


def _copy_firmware_dir(src_dir, dst):
    total = 0
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "out", "node_modules")]
        rel = os.path.relpath(root, src_dir)
        if rel.count(os.sep) > 2:
            dirs[:] = []
            continue
        for fn in files:
            if fn.startswith("sim_"):
                continue
            sp = os.path.join(root, fn)
            try:
                size = os.path.getsize(sp)
            except OSError:
                continue
            if size > COPY_MAX_FILE or total + size > COPY_MAX_TOTAL:
                continue
            dp = os.path.join(dst, rel, fn)
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            shutil.copy2(sp, dp)
            total += size


def _snapshot(d):
    out = {}
    for root, _dirs, files in os.walk(d):
        for fn in files:
            p = os.path.join(root, fn)
            try:
                st = os.stat(p)
            except OSError:
                continue
            out[os.path.relpath(p, d)] = (st.st_size, st.st_mtime_ns)
    return out


def _make_runtime(inputs, display, max_frames, max_seconds, seed, wall_timeout_s, tick_poll_us):
    if isinstance(inputs, (str, os.PathLike)):
        inputs = _stim.load(inputs)
    inputs = dict(inputs or {})
    kind = DISPLAY_KINDS.get(display) if display else None
    if display and kind is None:
        raise ValueError("unknown display %r (use ssd1306, st7789 or epaper)" % display)
    if "i2c_devices" not in inputs:
        inputs["i2c_devices"] = [0x3C] if kind in (None, "oled") else []
    rt = SimRuntime(max_frames=max_frames, max_seconds=max_seconds, seed=seed, inputs=inputs,
                    wall_timeout_s=wall_timeout_s, tick_poll_us=tick_poll_us)
    if inputs.get("rtc_start"):
        import datetime as _dt
        d = _dt.datetime.fromisoformat(inputs["rtc_start"])
        rt.rtc_offset_s = int((d - _dt.datetime(2000, 1, 1)).total_seconds())
    return rt, kind


class _SimEnv:
    """Install simulated modules + sandbox cwd/sys.path; restore everything on exit."""

    def __init__(self, rt, sandbox, echo=True, extra_paths=()):
        self.rt = rt
        self.sandbox = sandbox
        self.echo = echo
        self.extra_paths = list(extra_paths)
        self.tee = _Tee(echo)

    def __enter__(self):
        install = dict(SIM_MODULES)
        for alias, real in ALIASES.items():
            if real is None:
                continue
            __import__(real)
            install[alias] = sys.modules[real]
        for name in UNSUPPORTED_MODULES:
            if "." not in name:
                install[name] = _unsupported_module(name)
        for fname in mp_fonts.FONT_SIZES:
            if not os.path.exists(os.path.join(self.sandbox, fname + ".py")) and \
                    not os.path.exists(os.path.join(self.sandbox, "lib", fname + ".py")):
                install[fname] = mp_fonts.make_font_module(fname)
        self._missing = object()
        self.saved_modules = {n: sys.modules.get(n, self._missing) for n in install}
        self.saved_path = list(sys.path)
        self.saved_cwd = os.getcwd()
        self.saved_stdout = sys.stdout
        self.modules_before = set(sys.modules)
        mp_random._reseed_for_run(self.rt.seed)
        _rt.set_current(self.rt)
        sys.modules.update(install)
        sys.path[:0] = [self.sandbox, os.path.join(self.sandbox, "lib")] + self.extra_paths
        os.chdir(self.sandbox)
        sys.stdout = self.tee
        return self

    def forget_local_modules(self):
        roots = [self.sandbox] + self.extra_paths
        for name in list(sys.modules):
            if name in self.modules_before:
                continue
            f = getattr(sys.modules.get(name), "__file__", None) or ""
            if any(f.startswith(r) for r in roots):
                del sys.modules[name]

    def __exit__(self, *exc):
        rt = self.rt
        reason = rt.stop_reason
        rt.stop_reason = None
        rt.max_frames = None
        rt.wall_timeout_s = 0
        try:
            rt.run_idle_hooks()   # capture what direct-draw displays show at the end
        except SimStop:
            pass
        rt.stop_reason = reason
        sys.stdout = self.saved_stdout
        os.chdir(self.saved_cwd)
        sys.path[:] = self.saved_path
        for n, m in self.saved_modules.items():
            if m is self._missing:
                sys.modules.pop(n, None)
            else:
                sys.modules[n] = m
        self.forget_local_modules()
        _rt.set_current(None)
        return False


class session:
    """Context manager for tests: simulated modules are importable inside the block.

    ::

        with session(inputs={...}, max_seconds=5, paths=["firmware/templates"]) as s:
            import buttons                     # imports the simulated machine/time
            ...
            s.rt.now_us                        # virtual clock

    A run limit reached inside the block raises SimStop (a BaseException).
    """

    def __init__(self, *, inputs=None, display=None, max_frames=None, max_seconds=None, seed=0,
                 paths=(), echo=True, tick_poll_us=50, wall_timeout_s=60.0):
        self.rt, _ = _make_runtime(inputs, display, max_frames, max_seconds, seed,
                                   wall_timeout_s, tick_poll_us)
        self.sandbox = _new_sandbox()
        self.env = _SimEnv(self.rt, self.sandbox, echo, [str(Path(p).resolve()) for p in paths])

    def __enter__(self):
        self.env.__enter__()
        self.rt.boot_count = 1
        return self

    @property
    def console(self):
        return "".join(self.env.tee.buf)

    def __exit__(self, *exc):
        return self.env.__exit__(*exc)


def run(firmware, *, display=None, max_frames=None, max_seconds=None, seed=0, inputs=None,
        wall_timeout_s=60.0, max_boots=50, fs_dir=None, echo=True, tick_poll_us=50,
        width=None, height=None):
    """Run ``firmware`` (path to a .py file) and return a :class:`SimResult`.

    Stops at ``max_frames`` captured frames or ``max_seconds`` of VIRTUAL time
    (default 10 s when neither is given), when the firmware returns, raises,
    sleeps forever, or after ``wall_timeout_s`` of real time.
    """
    firmware = Path(firmware).resolve()
    src_text = firmware.read_text(encoding="utf-8")
    if max_frames is None and max_seconds is None:
        max_seconds = 10.0
    rt, kind = _make_runtime(inputs, display, max_frames, max_seconds, seed, wall_timeout_s, tick_poll_us)

    own_sandbox = fs_dir is None
    sandbox = _new_sandbox() if own_sandbox else str(Path(fs_dir).resolve())
    if own_sandbox:
        _copy_firmware_dir(str(firmware.parent), sandbox)
    before = _snapshot(sandbox)

    scripts = [firmware]
    if firmware.name == "main.py" and (Path(sandbox) / "boot.py").exists():
        scripts = [Path(sandbox) / "boot.py", firmware]
    env = _SimEnv(rt, sandbox, echo)
    state = {"error": None}
    done = threading.Event()

    def worker():
        # The firmware runs in its own daemon thread so that the run can always
        # end: if firmware swallows SimStop with a bare ``except:`` the thread is
        # parked (see SimRuntime.check), and a pure-Python endless loop is
        # interrupted by an injected SimStop or, at worst, abandoned.
        rt.firmware_thread = threading.current_thread()
        rt.on_park = done.set
        try:
            while True:
                rt.boot_count += 1
                rt.record("boot", n=rt.boot_count, cause=rt.reset_cause, wake=rt.wake_reason)
                try:
                    for script in scripts:
                        text = src_text if script == firmware else script.read_text(encoding="utf-8")
                        code = compile(text, str(script), "exec")
                        g = {"__name__": "__main__", "__file__": str(script), "__builtins__": builtins}
                        exec(code, g)
                    rt.stop_reason = rt.stop_reason or "finished"
                    break
                except SimStop as e:
                    rt.stop_reason = rt.stop_reason or e.reason
                    break
                except SimReboot as rb:
                    rt.record("reboot", cause=rb.cause, wake=rb.wake_reason)
                    if rt.boot_count >= max_boots:
                        rt.stop_reason = "max_boots"
                        break
                    rt.reset_cause = rb.cause
                    rt.wake_reason = rb.wake_reason
                    rt.wake_pins = rb.wake_pins
                    rt.reset_boot_state()
                    env.forget_local_modules()   # RAM is lost: re-import firmware modules
                    continue
                except SystemExit:
                    rt.stop_reason = "sys_exit"
                    break
                except Exception:
                    state["error"] = traceback.format_exc()
                    env.tee.write(state["error"])
                    rt.stop_reason = "exception"
                    break
        except BaseException as e:  # SimStop injected outside the try above
            rt.stop_reason = rt.stop_reason or getattr(e, "reason", "wall_timeout")
        finally:
            done.set()

    with env:
        th = threading.Thread(target=worker, name="mpsim-firmware", daemon=True)
        th.start()
        finished = done.wait(wall_timeout_s + 1.0 if wall_timeout_s else None)
        if not finished:
            if rt.stop_reason is None:
                rt.stop_reason = "wall_timeout"
            _inject(th, SimStop)
            if not done.wait(2.0):
                rt.warn("firmware thread did not stop after wall timeout; abandoned")
        th.join(0.5)
        if rt.parked:
            rt.warn("firmware kept catching the stop signal (bare except?); its thread was parked")
    error = state["error"]

    after = _snapshot(sandbox)
    written = sorted(k for k, v in after.items() if before.get(k) != v)
    res = SimResult(rt, firmware, kind, error, "".join(env.tee.buf), written, sandbox)
    if width or height:
        if res.frames:
            fh, fw = res.frames[0].rgb.shape[:2]
            if (width and width != fw) or (height and height != fh):
                res.warnings.append("panel size %sx%s requested but firmware drew %dx%d"
                                    % (width, height, fw, fh))
    return res
