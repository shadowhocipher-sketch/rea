# state_machine.py - event-driven finite state machine with per-state timeouts.
#
# Licence: MIT.  Pure MicroPython (uses only time.ticks_ms/ticks_diff), no pins.
#
# Verification status (2026-11-01):
#   - Verified: ONLY in the hardware-studio desktop simulator (sim/, mpsim) via
#     firmware/tests/test_fw_state_machine.py.
#   - NOT verified on any real board (no ESP32/ESP32-S3/C3 hardware was used).
#   - Not verified: behaviour under heavy GC pauses or with events posted from
#     hard IRQ handlers (post() allocates only when the queue grows; keep IRQ
#     handlers to micropython.schedule(fsm.post, ...) to be safe).
#
# API references: time.ticks_ms / ticks_diff semantics
#   https://docs.micropython.org/en/latest/library/time.html#time.ticks_diff
#
# Usage:
#   TABLE = {
#       "IDLE":   {"on": {"touch": "HAPPY"}, "timeout_ms": 10000, "timeout_to": "SLEEPY"},
#       "HAPPY":  {"on": {}, "timeout_ms": 3000, "timeout_to": "IDLE", "enter": say_hi},
#       "SLEEPY": {"on": {"touch": "IDLE", "button": ("IDLE", wake_action)}},
#   }
#   fsm = StateMachine(TABLE, "IDLE", on_transition=log)
#   fsm.post("touch")          # from anywhere (main loop, scheduled callback)
#   fsm.poll()                 # call often from the main loop
#
# Table rules: "on" maps event -> target state or (target, action(fsm, data)).
# A target of None means "handle the event (run the action) but stay".
# "enter"/"exit" are callables fsm -> None.  A timeout fires once per entry
# into the state; "timeout_to" may also be (target, action).
import time

# ---- configuration for the demo (no board-specific values in the class) ----
CONFIG = {
    "demo_display": True,      # draw the state on an SSD1306 if one answers on I2C
    "i2c_id": 0, "sda": 8, "scl": 9, "oled_addr": 0x3C, "width": 128, "height": 64,
    "loop_ms": 20,
}


def load_config(defaults, path="config.json"):
    """Return defaults updated with a JSON file on the device, if present."""
    cfg = dict(defaults)
    try:
        import json
        with open(path) as f:
            cfg.update(json.load(f))
    except (OSError, ValueError):
        pass
    return cfg


class StateMachine:
    def __init__(self, table, initial, *, on_transition=None, queue_len=16, clock=None):
        if initial not in table:
            raise ValueError("unknown initial state")
        for name, spec in table.items():
            for ev, tgt in spec.get("on", {}).items():
                t = tgt[0] if isinstance(tgt, tuple) else tgt
                if t is not None and t not in table:
                    raise ValueError("state %s: event %s -> unknown state %s" % (name, ev, t))
            to = spec.get("timeout_to")
            t = to[0] if isinstance(to, tuple) else to
            if t is not None and t not in table:
                raise ValueError("state %s: timeout_to unknown state %s" % (name, t))
        self.table = table
        self.on_transition = on_transition
        self._clock = clock or time.ticks_ms
        self._q = []
        self._qlen = queue_len
        self.dropped = 0
        self.state = None
        self._enter(initial, None, "init")

    # -------------------------------------------------------------- public
    def post(self, event, data=None):
        """Queue an event; returns False (and counts it) when the queue is full."""
        if len(self._q) >= self._qlen:
            self.dropped += 1
            return False
        self._q.append((event, data))
        return True

    def elapsed_ms(self):
        return time.ticks_diff(self._clock(), self._t_enter)

    def poll(self):
        """Process queued events, then the current state's timeout.  Returns state."""
        while self._q:
            event, data = self._q.pop(0)
            self._handle(event, data)
        spec = self.table[self.state]
        tmo = spec.get("timeout_ms")
        if tmo is not None and not self._timed_out and self.elapsed_ms() >= tmo:
            self._timed_out = True
            to = spec.get("timeout_to")
            if to is not None:
                self._go(to, None, "timeout")
        return self.state

    def dispatch(self, event, data=None):
        """Handle one event immediately (bypasses the queue)."""
        self._handle(event, data)
        return self.state

    # -------------------------------------------------------------- internals
    def _handle(self, event, data):
        tgt = self.table[self.state].get("on", {}).get(event)
        if tgt is None and event not in self.table[self.state].get("on", {}):
            return  # event not accepted in this state: ignored
        self._go(tgt, data, event)

    def _go(self, tgt, data, why):
        action = None
        if isinstance(tgt, tuple):
            tgt, action = tgt
        if action is not None:
            action(self, data)
        if tgt is None:
            return
        old = self.state
        ex = self.table[old].get("exit")
        if ex:
            ex(self)
        self._enter(tgt, old, why)

    def _enter(self, new, old, why):
        self.state = new
        self._t_enter = self._clock()
        self._timed_out = False
        if self.on_transition:
            self.on_transition(old, new, why)
        en = self.table[new].get("enter")
        if en:
            en(self)


# ---------------------------------------------------------------------- demo
def demo():
    cfg = load_config(CONFIG)
    oled = None
    if cfg["demo_display"]:
        try:
            from machine import Pin, I2C
            import ssd1306
            i2c = I2C(cfg["i2c_id"], scl=Pin(cfg["scl"]), sda=Pin(cfg["sda"]))
            if cfg["oled_addr"] in i2c.scan():
                oled = ssd1306.SSD1306_I2C(cfg["width"], cfg["height"], i2c, addr=cfg["oled_addr"])
        except (ImportError, OSError):
            oled = None

    def show(old, new, why):
        print("FSM %s -> %s (%s) t=%d" % (old, new, why, time.ticks_ms()))
        if oled:
            oled.fill(0)
            oled.text("state:", 0, 0, 1)
            oled.text(new, 0, 16, 1)
            oled.text("by: " + why, 0, 40, 1)
            oled.show()

    table = {
        "IDLE": {"on": {"touch": "HAPPY", "button": "MENU"}, "timeout_ms": 5000, "timeout_to": "SLEEPY"},
        "HAPPY": {"on": {"touch": None}, "timeout_ms": 2000, "timeout_to": "IDLE"},
        "MENU": {"on": {"button": "IDLE"}, "timeout_ms": 4000, "timeout_to": "IDLE"},
        "SLEEPY": {"on": {"touch": "IDLE", "button": "IDLE"}},
    }
    fsm = StateMachine(table, "IDLE", on_transition=show)
    # demo events at fixed times (use buttons.py to post real input events)
    script = [(1000, "touch"), (4000, "button"), (5000, "button"), (16000, "touch")]
    t0 = time.ticks_ms()
    while True:
        now = time.ticks_diff(time.ticks_ms(), t0)
        while script and now >= script[0][0]:
            fsm.post(script.pop(0)[1])
        fsm.poll()
        time.sleep_ms(cfg["loop_ms"])


if __name__ == "__main__":
    demo()
