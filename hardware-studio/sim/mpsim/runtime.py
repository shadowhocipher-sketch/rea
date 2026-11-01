"""Simulation runtime: virtual clock, event scheduler, stimulus, call log, frames.

One ``SimRuntime`` object holds all state of one simulated run.  The simulated
MicroPython modules (``mp_machine``, ``mp_time`` ...) look it up with
``current()`` so that the module objects themselves stay stateless.

Time is kept in integer microseconds since power-on of the first boot.
"""

import heapq
import threading
import itertools
import time as _real_time  # real clock, only for the wall-clock guard

from . import stimulus as _stimulus

_CURRENT = None

# Reset causes / wake reasons: values as defined in MicroPython's esp32 port
# (ports/esp32/modmachine.c, MP_PWRON_RESET = 1 ... MP_SOFT_RESET = 5) and
# ESP-IDF esp_sleep_wakeup_cause_t (EXT0 = 2, EXT1 = 3, TIMER = 4, TOUCHPAD = 5,
# ULP = 6, GPIO = 7).  https://github.com/micropython/micropython/blob/master/ports/esp32/modmachine.c
PWRON_RESET, HARD_RESET, WDT_RESET, DEEPSLEEP_RESET, SOFT_RESET = 1, 2, 3, 4, 5
WAKE_UNDEFINED, WAKE_EXT0, WAKE_EXT1, WAKE_TIMER, WAKE_TOUCHPAD, WAKE_ULP, WAKE_GPIO = 0, 2, 3, 4, 5, 6, 7

LOG_LIMIT = 5000  # keep at most this many detailed log entries; counts are always kept


class SimStop(BaseException):
    """Raised to end the run (frame/time limit, sleep forever, wall timeout).

    Derives from BaseException so that firmware ``except Exception:`` blocks do
    not swallow it.  Once raised, every later simulated call raises it again.
    """

    def __init__(self, reason="wall_timeout"):
        super().__init__(reason)
        self.reason = reason


class SimReboot(BaseException):
    """Raised by deepsleep()/reset()/WDT to restart the firmware from the top."""

    def __init__(self, cause, wake_reason=WAKE_UNDEFINED, wake_pins=()):
        super().__init__(cause)
        self.cause = cause
        self.wake_reason = wake_reason
        self.wake_pins = tuple(wake_pins)


class SimUnsupported(AttributeError):
    """A MicroPython API that this simulator does not implement."""


class Frame:
    """One captured display frame.

    ``rgb`` is a numpy uint8 array (H, W, 3) of what the panel shows, in the
    orientation the viewer sees.  ``kind`` is 'oled', 'lcd' or 'epaper'.
    """

    __slots__ = ("t_us", "display_id", "kind", "rgb", "meta")

    def __init__(self, t_us, display_id, kind, rgb, meta):
        self.t_us = t_us
        self.display_id = display_id
        self.kind = kind
        self.rgb = rgb
        self.meta = meta

    @property
    def t_ms(self):
        return self.t_us / 1000.0


class SimRuntime:
    def __init__(self, *, max_frames=None, max_seconds=None, seed=0, inputs=None,
                 wall_timeout_s=60.0, tick_poll_us=50, frame_cap=5000):
        self.now_us = 0
        self.boot_us = 0                # virtual time of the current boot
        self.boot_count = 0
        self.max_frames = max_frames
        self.max_us = None if max_seconds is None else int(round(max_seconds * 1_000_000))
        self.frame_cap = frame_cap
        self.seed = seed
        self.tick_poll_us = tick_poll_us  # each ticks_*() call advances the clock this much
        self.wall_timeout_s = wall_timeout_s
        self._wall_start = _real_time.monotonic()
        self.stim = _stimulus.Stimulus(inputs or {})

        self.frames = []
        self.stop_reason = None
        self._stop_raises = 0
        self.firmware_thread = None
        self.on_park = None
        self.parked = False
        self.log = []
        self.log_counts = {}
        self.warnings = []
        self._warned = set()
        self.unsupported = []

        self._events = []               # heap of (t_us, seq, callback, tag)
        self._seq = itertools.count()
        self._in_irq = 0
        self._pending_sched = []
        self._idle_hooks = []           # callables run before time advances (direct-draw capture)
        self.displays = []

        # state that survives deep sleep / reset (RTC domain, flash)
        self.reset_cause = PWRON_RESET
        self.wake_reason = WAKE_UNDEFINED
        self.wake_pins = ()
        self.rtc_memory = b""
        self.rtc_offset_s = None        # RTC calendar seconds (2000 epoch) at now_us == 0
        self.nvs = {}
        self.stats = {"lightsleep_ms": 0.0, "deepsleep_ms": 0.0}
        self.i2c_devices = set(self.stim.i2c_devices or ())
        self.i2c_mem = {}
        self.i2c_stats = {}
        self.spi_stats = {}
        self.uart_tx = {}
        self.pwm = {}
        self.cpu_freq = 160_000_000

        # per-boot state (cleared by reset_boot_state)
        self.reset_boot_state()

    # ------------------------------------------------------------------ boot
    def reset_boot_state(self):
        self._events = []
        self._idle_hooks = []
        self.pins = {}                  # pin id -> Pin state dict
        self.irqs = {}                  # pin id -> (handler, trigger, wake, pin_obj)
        self.timers = {}
        self.wdt = None
        self.wake_cfg = {"ext0": None, "ext1": None, "touch": False, "gpio": None, "ulp": False}
        self.touch_threshold = {}
        self.boot_us = self.now_us
        self.displays = []              # same panel after reboot keeps the same display id
        for t_us, pin, level in self.stim.pin_edges():
            if t_us >= self.now_us:
                self.schedule_at(t_us, self._make_edge_cb(pin, level), tag="edge")

    def _make_edge_cb(self, pin, level):
        def cb():
            self._fire_pin_irq(pin, level)
        return cb

    # ------------------------------------------------------------------ logging
    def record(self, kind, **data):
        self.log_counts[kind] = self.log_counts.get(kind, 0) + 1
        if len(self.log) < LOG_LIMIT:
            entry = {"t_ms": round(self.now_us / 1000.0, 3), "kind": kind}
            entry.update(data)
            self.log.append(entry)

    def warn(self, msg, key=None):
        key = key or msg
        if key in self._warned:
            return
        self._warned.add(key)
        self.warnings.append("[t=%.1fms] %s" % (self.now_us / 1000.0, msg))

    def unsupported_api(self, module, name):
        if name.startswith("__") or name.startswith("_pytest") or name.startswith("_sim"):
            return AttributeError(name)  # import machinery / introspection probes
        full = "%s.%s" % (module, name)
        if full not in self.unsupported:
            self.unsupported.append(full)
        return SimUnsupported(
            "mpsim: %s is not implemented by the simulator (see sim/README.md, "
            "'Supported APIs')" % full)

    # ------------------------------------------------------------------ guards
    def check(self):
        """Called by every simulated API: re-raise a pending stop, wall guard."""
        if self.stop_reason is not None:
            self._stop_raises += 1
            if self._stop_raises > 200 and self.firmware_thread is threading.current_thread():
                # the firmware keeps catching SimStop (bare except): park this thread
                self.parked = True
                if self.on_park:
                    self.on_park()
                threading.Event().wait()
            raise SimStop(self.stop_reason)
        if self.wall_timeout_s and _real_time.monotonic() - self._wall_start > self.wall_timeout_s:
            self.stop("wall_timeout")

    def stop(self, reason):
        if self.stop_reason is None:
            self.stop_reason = reason
        raise SimStop(self.stop_reason)

    # ------------------------------------------------------------------ clock
    def ticks_us_raw(self):
        return self.now_us - self.boot_us

    def poll_tick(self):
        """A ticks_*() read: advance a tiny bit so busy-wait loops terminate."""
        self.check()
        if self.tick_poll_us:
            self.advance(self.tick_poll_us, poll=True)

    def schedule_at(self, t_us, callback, tag=""):
        heapq.heappush(self._events, (int(t_us), next(self._seq), callback, tag))

    def add_idle_hook(self, fn):
        self._idle_hooks.append(fn)

    def run_idle_hooks(self):
        for fn in list(self._idle_hooks):
            fn()

    def advance(self, us, poll=False):
        """Advance virtual time by ``us`` microseconds, firing due events."""
        self.check()
        us = int(us)
        if us < 0:
            us = 0
        if not poll:
            self.run_idle_hooks()
        target = self.now_us + us
        limit_hit = False
        if self.max_us is not None and target >= self.max_us:
            target = self.max_us
            limit_hit = True
        while self._events and self._events[0][0] <= target:
            t, _, cb, _tag = heapq.heappop(self._events)
            if t > self.now_us:
                self.now_us = t
            self._call_irq(cb)
            if self.stop_reason is not None:
                raise SimStop(self.stop_reason)
        if target > self.now_us:
            self.now_us = target
        if limit_hit:
            self.run_idle_hooks()
            self.stop("time_limit")

    def advance_until(self, deadline_us, wake_fn=None):
        """Advance to ``deadline_us`` (None = forever) or until ``wake_fn`` says wake.

        ``wake_fn(after_us, until_us)`` returns (t_us, reason, pins) of the first
        wake event in (after, until] or None.  Returns (reason, pins) or None if
        the deadline was reached.
        """
        until = deadline_us
        if self.max_us is not None and (until is None or until > self.max_us):
            until = self.max_us
        wake = wake_fn(self.now_us, until) if wake_fn else None
        if wake is not None:
            self.advance(wake[0] - self.now_us)
            return wake[1], wake[2]
        if deadline_us is None and until is None:
            self.stop("sleep_forever")
        if deadline_us is None:
            # sleeping forever but there is a time limit: run out the clock
            self.advance(until - self.now_us)
            self.stop("sleep_forever")
        self.advance(deadline_us - self.now_us)
        return None

    def _call_irq(self, cb):
        self._in_irq += 1
        try:
            cb()
        except (SimStop, SimReboot):
            raise
        except Exception as exc:  # MicroPython prints the traceback and keeps running
            import traceback
            self.record("irq_exception", error=repr(exc))
            self.warn("exception in IRQ/timer callback: %r" % (exc,))
            traceback.print_exc()
        finally:
            self._in_irq -= 1
        if not self._in_irq:
            self.run_scheduled()

    def run_scheduled(self):
        while self._pending_sched:
            fn, arg = self._pending_sched.pop(0)
            fn(arg)

    def schedule_soft(self, fn, arg):
        if self._in_irq:
            self._pending_sched.append((fn, arg))
        else:
            fn(arg)

    # ------------------------------------------------------------------ pins
    def _fire_pin_irq(self, pin, level):
        st = self.pins.get(pin)
        prev = self.stim.level_before(pin, self.now_us)
        if st is not None:
            st["ext"] = level
        irq = self.irqs.get(pin)
        if irq is None or irq["handler"] is None:
            return
        # Pin.OUT (3) pins follow their output buffer, not the external level.
        if st is not None and st["mode"] == 3:
            return
        trig = irq["trigger"]
        rising = prev == 0 and level == 1
        falling = prev == 1 and level == 0
        if trig in (4, 5):  # level triggers (esp32 WAKE_LOW / WAKE_HIGH)
            fire = level == (trig - 4)
        else:               # IRQ_RISING = 1, IRQ_FALLING = 2 (esp32 values)
            fire = (rising and trig & 1) or (falling and trig & 2)
        if fire:
            self.record("pin_irq", pin=pin, level=level)
            irq["handler"](irq["pin_obj"])

    # ------------------------------------------------------------------ frames
    def record_frame(self, display_id, kind, rgb, meta=None):
        self.check()
        self.frames.append(Frame(self.now_us, display_id, kind, rgb, dict(meta or {})))
        if len(self.frames) > self.frame_cap:
            self.frames.pop(0)
            self.warn("frame_cap %d reached; oldest frames dropped" % self.frame_cap, "frame_cap")
        if self.max_frames is not None and len(self.frames) >= self.max_frames:
            self.stop("frame_limit")

    def register_display(self, disp):
        self.displays.append(disp)


def current():
    if _CURRENT is None:
        raise RuntimeError("mpsim: no simulation is running (use mpsim.run or run_firmware.py)")
    return _CURRENT


def set_current(rt):
    global _CURRENT
    _CURRENT = rt


def unsupported(module, name):
    """Exception for a missing API: recorded when a run is active."""
    if _CURRENT is None or name.startswith("__"):
        return AttributeError("module %r has no attribute %r" % (module, name))
    return _CURRENT.unsupported_api(module, name)
