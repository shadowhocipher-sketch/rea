"""Run the four firmware templates in the simulator and check their logic.

These are simulator-only checks: they do not establish behaviour on hardware.
"""
import json
import os
import re
import shutil
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.normpath(os.path.join(HERE, "..", "templates"))
SIM = os.path.normpath(os.path.join(HERE, "..", "..", "sim"))
sys.path.insert(0, SIM)

from mpsim import run, session  # noqa: E402


def tpl(name):
    return os.path.join(TEMPLATES, name)


# ===================================================================== state machine
def test_fsm_transitions_timeouts_and_actions():
    with session(max_seconds=60, paths=[TEMPLATES], echo=False):
        import time
        from state_machine import StateMachine
        log, acted = [], []
        table = {
            "A": {"on": {"go": "B", "ping": (None, lambda f, d: acted.append(d))},
                  "timeout_ms": 1000, "timeout_to": "C"},
            "B": {"on": {"back": ("A", lambda f, d: acted.append("back"))},
                  "enter": lambda f: log.append("enterB"), "exit": lambda f: log.append("exitB")},
            "C": {"on": {}},
        }
        fsm = StateMachine(table, "A", on_transition=lambda o, n, w: log.append((o, n, w)))
        fsm.post("ping", 7)
        fsm.post("unknown")                    # ignored
        assert fsm.poll() == "A" and acted == [7]
        fsm.post("go")
        assert fsm.poll() == "B"
        time.sleep_ms(5000)                    # B has no timeout
        assert fsm.poll() == "B"
        fsm.post("back")
        assert fsm.poll() == "A" and acted == [7, "back"]
        time.sleep_ms(999)
        assert fsm.poll() == "A"
        time.sleep_ms(2)
        assert fsm.poll() == "C"
        assert log == [(None, "A", "init"), ("A", "B", "go"), "enterB", "exitB",
                       ("B", "A", "back"), ("A", "C", "timeout")]


def test_fsm_validation_and_queue_overflow():
    with session(max_seconds=5, paths=[TEMPLATES], echo=False):
        from state_machine import StateMachine
        with pytest.raises(ValueError):
            StateMachine({"A": {"on": {"x": "Z"}}}, "A")
        with pytest.raises(ValueError):
            StateMachine({"A": {}}, "B")
        fsm = StateMachine({"A": {"on": {}}}, "A", queue_len=2)
        assert fsm.post(1) and fsm.post(2) and not fsm.post(3) and fsm.dropped == 1


def test_fsm_demo_runs_in_simulator():
    r = run(tpl("state_machine.py"), max_seconds=20, echo=False)
    assert r.stop_reason == "time_limit" and r.error is None
    trans = re.findall(r"FSM (\S+) -> (\S+) \((\w+)\)", r.console)
    assert trans == [("None", "IDLE", "init"), ("IDLE", "HAPPY", "touch"), ("HAPPY", "IDLE", "timeout"),
                     ("IDLE", "MENU", "button"), ("MENU", "IDLE", "button"),
                     ("IDLE", "SLEEPY", "timeout"), ("SLEEPY", "IDLE", "touch")]
    assert len(r.frames) == 8                  # init frame + one per transition on the OLED


# ===================================================================== buttons
def _collect(inputs, seconds, make, poll_ms=5):
    """Poll a Button built by make() and return [(t_ms, event)]."""
    out = []
    with session(inputs=inputs, max_seconds=seconds + 1, paths=[TEMPLATES], echo=False, tick_poll_us=0) as s:
        import time
        btn = make()
        while s.rt.now_us < seconds * 1_000_000:
            ev = btn.update()
            if ev:
                out.append((s.rt.now_us // 1000, ev))
            time.sleep_ms(poll_ms)
    return out


def _pin_button(**kw):
    def make():
        from machine import Pin
        from buttons import Button, PinSource
        return Button(PinSource(Pin(0, Pin.IN, Pin.PULL_UP), True), **kw)
    return make


def test_click_with_contact_bounce_gives_one_click():
    inputs = {"buttons": [{"pin": 0, "at_ms": 100, "hold_ms": 80, "bounce_ms": 6}]}
    ev = _collect(inputs, 1.0, _pin_button(debounce_ms=20, long_ms=700, double_ms=300))
    assert [e for _, e in ev] == ["click"]
    t = ev[0][0]
    # release settles at 180+6 ms, debounce 20 ms, then double-click window 300 ms
    assert 186 + 20 + 300 <= t <= 186 + 20 + 300 + 10


def test_double_click_and_long_press():
    inputs = {"buttons": [
        {"pin": 0, "at_ms": 100, "hold_ms": 60, "bounce_ms": 4},
        {"pin": 0, "at_ms": 260, "hold_ms": 60, "bounce_ms": 4},     # second press within 300 ms
        {"pin": 0, "at_ms": 1000, "hold_ms": 1200, "bounce_ms": 4},  # long press
    ]}
    ev = _collect(inputs, 3.0, _pin_button(debounce_ms=20, long_ms=700, double_ms=300))
    names = [e for _, e in ev]
    assert names == ["double", "long", "hold_end"]
    t_long = dict((e, t) for t, e in ev)["long"]
    assert 1000 + 4 + 20 + 700 - 5 <= t_long <= 1000 + 4 + 20 + 700 + 10


def test_glitch_shorter_than_debounce_is_ignored():
    inputs = {"pins": {"0": [[0, 1], [500, 0], [510, 1]]}}          # 10 ms glitch
    ev = _collect(inputs, 1.5, _pin_button(debounce_ms=20))
    assert ev == []


def test_double_ms_zero_reports_click_on_release():
    inputs = {"buttons": [{"pin": 0, "at_ms": 100, "hold_ms": 50}]}
    ev = _collect(inputs, 0.5, _pin_button(debounce_ms=20, double_ms=0))
    assert [e for _, e in ev] == ["click"] and ev[0][0] <= 150 + 20 + 10


@pytest.mark.parametrize("increases,idle,touched", [(True, 20000, 60000), (False, 600, 200)])
def test_touch_click_both_directions(increases, idle, touched):
    inputs = {"touch": {"7": {"idle": idle, "touched": touched, "windows": [[300, 420]]}}}

    def make():
        from machine import Pin, TouchPad
        from buttons import Button, TouchSource
        return Button(TouchSource(TouchPad(Pin(7)), increases=increases, ratio=0.3),
                      debounce_ms=20, double_ms=250)
    ev = _collect(inputs, 1.2, make)
    assert [e for _, e in ev] == ["click"]


def test_buttons_demo_runs_in_simulator():
    inputs = {"buttons": [{"pin": 0, "at_ms": 500, "hold_ms": 900, "bounce_ms": 3}],
              "touch": {"7": {"idle": 20000, "touched": 60000, "windows": [[2000, 2100]]}}}
    r = run(tpl("buttons.py"), max_seconds=4, inputs=inputs, echo=False)
    assert r.error is None
    assert re.findall(r"EVENT (\w+) (\w+)", r.console) == [("button", "long"), ("button", "hold_end"),
                                                          ("touch", "click")]


# ===================================================================== power
def test_power_demo_deep_sleep_cycle_with_button_and_timer_wake():
    inputs = {"buttons": [{"pin": 0, "at_ms": 12000, "hold_ms": 200}]}
    r = run(tpl("power.py"), max_seconds=70, inputs=inputs, echo=False)
    assert r.error is None and r.stop_reason == "time_limit"
    boots = re.findall(r"BOOT (\d+) cause=([\w -]+) wake=([\w ]+)", r.console)
    assert boots[:3] == [("1", "power-on", "none"), ("2", "deep-sleep wake", "ext0 pin"),
                         ("3", "deep-sleep wake", "timer")]
    # awake 8 s -> sleep at 8 s; button at 12 s wakes (ext0).  The held button
    # (12.0-12.2 s) keeps kicking the idle timer, so the next sleep starts at
    # ~20.2 s and the 20 s timer wakes at ~40.2 s (50 ms polling granularity).
    starts = [e["t_ms"] for e in r.log if e["kind"] == "boot"]
    assert starts[:3] == [0, 12000, pytest.approx(40200, abs=60)]
    assert r.frames[-1].rgb.max() == 0 or any(f.meta.get("event") == "poweroff" for f in r.frames)


def test_power_light_sleep_and_touch_wake_from_config(tmp_path):
    shutil.copy(tpl("power.py"), tmp_path / "power.py")
    (tmp_path / "config.json").write_text(json.dumps(
        {"mode": "light", "sleep_ms": None, "wake_pin": None, "touch_pin": 7, "awake_ms": 1000}))
    inputs = {"touch": {"7": {"idle": 20000, "touched": 60000, "windows": [[5000, 5200]]}}}
    r = run(tmp_path / "power.py", max_seconds=20, inputs=inputs, echo=False)
    assert r.error is None and r.stop_reason == "finished"
    assert "SLEEP light wake on: touch pin 7" in r.console and "WOKE (light) reason=touch" in r.console
    assert r.rt.stats["lightsleep_ms"] == pytest.approx(4000, abs=60)


def test_boot_counter_resets_on_power_on():
    with session(max_seconds=5, paths=[TEMPLATES], echo=False):
        from power import BootCounter
        b = BootCounter()
        assert b.count == 0 and b.bump() == 1 and b.bump() == 2


# ===================================================================== self test
SELFTEST_IN = {"i2c_devices": [0x3C, 0x68], "adc": {"1": [[0, 1.95]]}}


def test_selftest_pass_warn_and_log():
    r = run(tpl("selftest.py"), max_seconds=10, inputs=SELFTEST_IN, echo=False)
    assert r.error is None and r.stop_reason == "finished"
    assert "SELFTEST PASS i2c OLED 0x3c" in r.console
    assert "SELFTEST WARN i2c extra" in r.console and "0x68" in r.console
    assert re.search(r"SELFTEST PASS battery\s+3\.90 V", r.console)
    assert "SELFTEST overall WARN" in r.console
    assert r.files_written == ["selftest.log"]
    rec = json.loads(open(os.path.join(r.sandbox, "selftest.log")).read().splitlines()[-1])
    assert rec["overall"] == "WARN" and abs(rec["battery_v"] - 3.9) < 0.01
    assert len(r.frames) == 6                   # init + 4 patterns + result screen


def test_selftest_missing_display_and_low_battery_fail():
    r = run(tpl("selftest.py"), max_seconds=10,
            inputs={"i2c_devices": [], "adc": {"1": [[0, 1.6]]}}, echo=False)
    assert r.error is None
    assert "SELFTEST FAIL i2c OLED 0x3c" in r.console and "SELFTEST FAIL display init" in r.console
    assert re.search(r"SELFTEST FAIL battery\s+3\.20 V", r.console)
    assert "SELFTEST overall FAIL" in r.console and r.frames == []


def test_selftest_log_is_bounded():
    with session(inputs=SELFTEST_IN, max_seconds=60, paths=[TEMPLATES], echo=False):
        import os as _os
        from selftest import write_log
        cfg = {"log_file": "t.log", "log_max_bytes": 300}
        for i in range(50):
            write_log(cfg, {"i": i, "pad": "x" * 40})
        assert _os.stat("t.log")[6] <= 300
