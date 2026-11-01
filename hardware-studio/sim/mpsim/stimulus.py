"""External inputs for a simulated run (buttons, pins, touch pads, ADC, I2C, UART).

The stimulus is a plain dict (or a JSON/YAML file with the same shape)::

    {
      "pins":    {"4": [[0, 1], [1500, 0], [1600, 1]]},      # [t_ms, level] steps
      "buttons": [{"pin": 0, "at_ms": 1000, "hold_ms": 80,    # a press
                   "active_level": 0, "bounce_ms": 4}],
      "touch":   {"7": {"idle": 20000, "touched": 60000,      # TouchPad.read() values
                        "windows": [[2000, 2300]]}},          # touched while start<=t<end
      "adc":     {"1": [[0, 4.10], [60000, 3.55]]},           # volts at the pin, linear
      "i2c_devices": [60, 104],                               # addresses that ACK
      "i2c_registers": {"104": {"117": [104]}},               # readfrom_mem contents
      "uart_rx": [[500, "hello\\n"]],                          # bytes arriving at t_ms
      "wifi": {"connect": false}
    }

All times are virtual milliseconds since the first power-on.  Pin keys are the
pin ids used by the firmware (``Pin(4)`` -> ``"4"``).
"""

import bisect


def _key(pin):
    return str(pin)


class Stimulus:
    def __init__(self, spec):
        spec = dict(spec or {})
        self.spec = spec
        steps = {}
        for pin, seq in (spec.get("pins") or {}).items():
            for t_ms, level in seq:
                steps.setdefault(_key(pin), []).append((int(round(float(t_ms) * 1000)), 1 if level else 0))
        for b in spec.get("buttons") or []:
            pin = _key(b["pin"])
            active = 1 if b.get("active_level", 0) else 0
            idle = 1 - active
            at = int(round(float(b["at_ms"]) * 1000))
            hold = int(round(float(b.get("hold_ms", 100)) * 1000))
            bounce = int(round(float(b.get("bounce_ms", 0)) * 1000))
            seq = steps.setdefault(pin, [])
            if not any(t == 0 for t, _ in seq):
                seq.append((0, idle))
            for start, level in ((at, active), (at + hold, idle)):
                # contact bounce: toggle every 1 ms during bounce_ms, end on `level`
                n = bounce // 1000
                t = start
                for i in range(n):
                    seq.append((t, level if i % 2 == 0 else 1 - level))
                    t += 1000
                seq.append((t, level))
        self.steps = {}
        for pin, seq in steps.items():
            seq.sort(key=lambda s: s[0])
            # drop non-changes but keep the first entry (initial level)
            out = []
            for t, lv in seq:
                if out and out[-1][0] == t:
                    out[-1] = (t, lv)
                elif not out or out[-1][1] != lv:
                    out.append((t, lv))
            self.steps[pin] = out
        self.touch = {}
        for pin, cfg in (spec.get("touch") or {}).items():
            self.touch[_key(pin)] = {
                "idle": int(cfg.get("idle", 20000)),
                "touched": int(cfg.get("touched", 60000)),
                "windows": [(int(round(float(a) * 1000)), int(round(float(b) * 1000)))
                            for a, b in cfg.get("windows", [])],
            }
        self.adc = {}
        for pin, seq in (spec.get("adc") or {}).items():
            pts = sorted((int(round(float(t) * 1000)), float(v)) for t, v in seq)
            self.adc[_key(pin)] = pts
        self.i2c_devices = spec.get("i2c_devices")
        self.i2c_registers = {}
        for addr, regs in (spec.get("i2c_registers") or {}).items():
            self.i2c_registers[int(addr)] = {int(r): bytes(v) for r, v in regs.items()}
        self.uart_rx = sorted((int(round(float(t) * 1000)), s.encode() if isinstance(s, str) else bytes(s))
                              for t, s in (spec.get("uart_rx") or []))
        self.wifi = dict(spec.get("wifi") or {})

    # ---------------------------------------------------------------- digital
    def has_pin(self, pin):
        return _key(pin) in self.steps

    def pin_edges(self):
        out = []
        for pin, seq in self.steps.items():
            for t, lv in seq:
                out.append((t, pin, lv))
        out.sort(key=lambda e: e[0])
        return out

    def level_at(self, pin, t_us):
        seq = self.steps.get(_key(pin))
        if not seq:
            return None
        i = bisect.bisect_right([t for t, _ in seq], t_us) - 1
        return seq[i][1] if i >= 0 else None

    def level_before(self, pin, t_us):
        seq = self.steps.get(_key(pin))
        if not seq:
            return None
        i = bisect.bisect_left([t for t, _ in seq], t_us) - 1
        return seq[i][1] if i >= 0 else None

    def change_times(self, pins, after_us, until_us):
        """Sorted step times t of the given pins with after_us < t <= until_us."""
        ts = set()
        for p in pins:
            for t, _ in self.steps.get(_key(p), ()):
                if t > after_us and (until_us is None or t <= until_us):
                    ts.add(t)
        return sorted(ts)

    # ---------------------------------------------------------------- touch
    def touch_value(self, pin, t_us):
        cfg = self.touch.get(_key(pin))
        if cfg is None:
            return None
        for a, b in cfg["windows"]:
            if a <= t_us < b:
                return cfg["touched"]
        return cfg["idle"]

    def touch_starts(self, after_us, until_us):
        out = []
        for pin, cfg in self.touch.items():
            for a, _b in cfg["windows"]:
                if a > after_us and (until_us is None or a <= until_us):
                    out.append((a, pin))
        out.sort()
        return out

    # ---------------------------------------------------------------- analog
    def adc_volts(self, pin, t_us):
        pts = self.adc.get(_key(pin))
        if not pts:
            return None
        if t_us <= pts[0][0]:
            return pts[0][1]
        for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
            if t0 <= t_us <= t1:
                if t1 == t0:
                    return v1
                return v0 + (v1 - v0) * (t_us - t0) / (t1 - t0)
        return pts[-1][1]


def load(path):
    """Load a stimulus file (.json or .yaml/.yml)."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if str(path).endswith((".yaml", ".yml")):
        import yaml
        return yaml.safe_load(text) or {}
    import json
    return json.loads(text)
