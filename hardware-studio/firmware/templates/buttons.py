# buttons.py - debounced push buttons and capacitive touch pads with
#              click / double-click / long-press detection (polling, no IRQs).
#
# Licence: MIT.
#
# Verification status (2026-11-01):
#   - Verified: ONLY in the hardware-studio desktop simulator (sim/, mpsim),
#     with scripted button bounce and touch readings
#     (firmware/tests/test_fw_buttons.py).
#   - NOT verified on any real board.  Real contact bounce, touch-pad raw
#     ranges and noise depend on the switch, pad size, cover material and board
#     layout: calibrate debounce_ms and the touch threshold on hardware.
#   - Not verified: ESP32 (original) touch direction on hardware; the class
#     supports both directions (see TouchSource.increases).
#
# API references:
#   machine.Pin                     https://docs.micropython.org/en/latest/library/machine.Pin.html
#   machine.TouchPad (ESP32 port)   https://docs.micropython.org/en/latest/esp32/quickref.html#capacitive-touch
#     "On ESP32 the number becomes smaller when the pin is touched, on ESP32-S2
#      and ESP32-S3 the number becomes larger" - quickref, Capacitive touch.
#   time.ticks_ms / ticks_diff      https://docs.micropython.org/en/latest/library/time.html
#
# Usage:
#   btn = Button(PinSource(Pin(0, Pin.IN, Pin.PULL_UP), active_low=True))
#   pad = Button(TouchSource(TouchPad(Pin(7)), increases=True))
#   while True:
#       ev = btn.update()          # None, CLICK, DOUBLE, LONG, or HOLD_END
#       ...
#       time.sleep_ms(10)          # poll every 5..20 ms
#
# Timing model (all configurable):
#   * a level change is accepted after it is stable for debounce_ms;
#   * LONG fires once while still held, when held >= long_ms (HOLD_END on release);
#   * a release after a short press waits double_ms for a second press:
#     second press -> DOUBLE (on its release), otherwise CLICK.
#   So a CLICK is reported double_ms after release; set double_ms=0 to disable
#   double-click and get CLICK immediately on release.
import time

CLICK = "click"
DOUBLE = "double"
LONG = "long"
HOLD_END = "hold_end"

# ---- configuration for the demo ----
CONFIG = {
    "button_pin": 0, "button_active_low": True,
    "touch_pin": 7, "touch_increases": True,     # True for ESP32-S2/S3, False for ESP32
    "touch_ratio": 0.3,                          # touched if |raw-baseline| > ratio * baseline
    "debounce_ms": 25, "long_ms": 700, "double_ms": 300, "poll_ms": 5,
    "demo_seconds": 0,                           # 0 = run forever
}


def load_config(defaults, path="config.json"):
    cfg = dict(defaults)
    try:
        import json
        with open(path) as f:
            cfg.update(json.load(f))
    except (OSError, ValueError):
        pass
    return cfg


class PinSource:
    """Digital input; returns True while pressed."""

    def __init__(self, pin, active_low=True):
        self.pin = pin
        self.active_low = active_low

    def pressed(self):
        v = self.pin.value()
        return (v == 0) if self.active_low else (v == 1)


class TouchSource:
    """Capacitive pad with a slowly tracking baseline.

    increases=True : reading grows when touched (ESP32-S2/S3)
    increases=False: reading drops when touched (ESP32)
    """

    def __init__(self, pad, increases=True, ratio=0.3, calib_samples=8, track=0.02):
        self.pad = pad
        self.increases = increases
        self.ratio = ratio
        self.track = track
        s = 0
        for _ in range(calib_samples):
            s += pad.read()
        self.baseline = s / calib_samples

    def pressed(self):
        raw = self.pad.read()
        delta = (raw - self.baseline) if self.increases else (self.baseline - raw)
        touched = delta > self.ratio * self.baseline
        if not touched:  # follow slow drift (temperature, humidity) only while untouched
            self.baseline += (raw - self.baseline) * self.track
        return touched


class Button:
    def __init__(self, source, *, debounce_ms=25, long_ms=700, double_ms=300, callback=None,
                 clock=None):
        self.src = source
        self.debounce_ms = debounce_ms
        self.long_ms = long_ms
        self.double_ms = double_ms
        self.callback = callback
        self._clock = clock or time.ticks_ms
        now = self._clock()
        self._raw = self.src.pressed()
        self._raw_t = now
        self.down = self._raw          # debounced state
        self._t_down = now
        self._t_up = now
        self._clicks = 0
        self._long_fired = False

    def _emit(self, ev):
        if self.callback and ev:
            self.callback(ev)
        return ev

    def update(self):
        """Poll once.  Returns an event constant or None."""
        now = self._clock()
        raw = self.src.pressed()
        if raw != self._raw:
            self._raw = raw
            self._raw_t = now
        ev = None
        if raw != self.down and time.ticks_diff(now, self._raw_t) >= self.debounce_ms:
            self.down = raw
            if raw:                                   # debounced press
                self._t_down = now
                self._long_fired = False
            else:                                     # debounced release
                self._t_up = now
                if self._long_fired:
                    ev = HOLD_END
                    self._clicks = 0
                else:
                    self._clicks += 1
                    if self._clicks >= 2:
                        ev = DOUBLE
                        self._clicks = 0
                    elif self.double_ms <= 0:
                        ev = CLICK
                        self._clicks = 0
        if ev is None and self.down and not self._long_fired and \
                time.ticks_diff(now, self._t_down) >= self.long_ms:
            self._long_fired = True
            self._clicks = 0
            ev = LONG
        if ev is None and not self.down and self._clicks == 1 and \
                time.ticks_diff(now, self._t_up) >= self.double_ms:
            self._clicks = 0
            ev = CLICK
        return self._emit(ev)


# ---------------------------------------------------------------------- demo
def demo():
    from machine import Pin
    cfg = load_config(CONFIG)
    buttons = {
        "button": Button(PinSource(Pin(cfg["button_pin"], Pin.IN, Pin.PULL_UP if cfg["button_active_low"]
                                       else Pin.PULL_DOWN), cfg["button_active_low"]),
                         debounce_ms=cfg["debounce_ms"], long_ms=cfg["long_ms"], double_ms=cfg["double_ms"]),
    }
    if cfg["touch_pin"] is not None:
        try:
            from machine import TouchPad
            pad = TouchSource(TouchPad(Pin(cfg["touch_pin"])), cfg["touch_increases"], cfg["touch_ratio"])
            buttons["touch"] = Button(pad, debounce_ms=cfg["debounce_ms"], long_ms=cfg["long_ms"],
                                      double_ms=cfg["double_ms"])
        except (ImportError, ValueError) as e:
            print("touch disabled:", e)
    t0 = time.ticks_ms()
    while not cfg["demo_seconds"] or time.ticks_diff(time.ticks_ms(), t0) < cfg["demo_seconds"] * 1000:
        for name, b in buttons.items():
            ev = b.update()
            if ev:
                print("EVENT %s %s t=%d" % (name, ev, time.ticks_diff(time.ticks_ms(), t0)))
        time.sleep_ms(cfg["poll_ms"])


if __name__ == "__main__":
    demo()
