"""Virtual clock, stop conditions, inputs, sleep/reset and module isolation."""
import os
import sys
import textwrap
import time as real_time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from mpsim import run, session, SimStop  # noqa: E402


def fw(tmp_path, body, name="main_fw.py"):
    p = tmp_path / name
    p.write_text(textwrap.dedent(body), encoding="utf-8")
    return p


def test_sleep_is_virtual_and_ticks_advance(tmp_path):
    p = fw(tmp_path, """
        import time
        t0 = time.ticks_ms()
        time.sleep(30)
        time.sleep_ms(250)
        time.sleep_us(500)
        print("elapsed", time.ticks_diff(time.ticks_ms(), t0))
    """)
    t = real_time.monotonic()
    r = run(p, max_seconds=100, echo=False)
    assert real_time.monotonic() - t < 5
    assert r.stop_reason == "finished"
    elapsed = int(r.console.split("elapsed")[1])
    assert 30250 <= elapsed <= 30252          # + tick polling (50 us per ticks call)


def test_ticks_wraparound_arithmetic(tmp_path):
    with session(max_seconds=1, echo=False):
        import time
        MAX = time.ticks_add(0, -1)
        assert MAX == (1 << 30) - 1
        assert time.ticks_diff(time.ticks_add(MAX, 5), MAX) == 5
        assert time.ticks_diff(2, MAX - 2) == 5
        with pytest.raises(OverflowError):
            time.ticks_add(0, 1 << 29)


def test_busy_wait_on_ticks_terminates(tmp_path):
    p = fw(tmp_path, """
        import time
        d = time.ticks_add(time.ticks_ms(), 200)
        n = 0
        while time.ticks_diff(d, time.ticks_ms()) > 0:
            n += 1
        print("loops", n)
    """)
    r = run(p, max_seconds=5, echo=False)
    assert r.stop_reason == "finished" and 199.9 <= r.virtual_ms <= 201


def test_frame_limit_stops_while_true_even_with_except_exception(tmp_path):
    p = fw(tmp_path, """
        from machine import Pin, I2C
        import ssd1306, time
        oled = ssd1306.SSD1306_I2C(128, 64, I2C(0, scl=Pin(9), sda=Pin(8)))
        i = 0
        while True:
            try:
                oled.fill(0); oled.text(str(i), 0, 0, 1); oled.show()
                time.sleep_ms(100)
            except Exception:
                pass
            i += 1
    """)
    r = run(p, display="ssd1306", max_frames=7, echo=False)
    assert r.stop_reason == "frame_limit" and len(r.frames) == 7
    assert not r.rt.parked and r.warnings == []


def test_time_limit_and_bare_except_cannot_swallow_stop(tmp_path):
    p = fw(tmp_path, """
        import time
        while True:
            try:
                time.sleep_ms(100)
            except:
                pass
    """)
    r = run(p, max_seconds=2.5, echo=False)
    assert r.stop_reason == "time_limit" and r.virtual_ms == 2500
    assert r.rt.parked and any("parked" in w for w in r.warnings)


def test_wall_timeout_on_pure_python_loop(tmp_path):
    p = fw(tmp_path, """
        x = 0
        while True:
            x += 1
    """)
    t = real_time.monotonic()
    r = run(p, max_seconds=5, wall_timeout_s=0.5, echo=False)
    assert r.stop_reason == "wall_timeout" and real_time.monotonic() - t < 5


def test_random_is_reproducible_with_seed(tmp_path):
    p = fw(tmp_path, """
        import random
        print([random.randint(0, 1000) for _ in range(5)])
    """)
    a = run(p, seed=3, echo=False).console
    b = run(p, seed=3, echo=False).console
    c = run(p, seed=4, echo=False).console
    assert a == b and a != c


def test_pin_irq_timer_and_button_stimulus(tmp_path):
    p = fw(tmp_path, """
        from machine import Pin, Timer
        import time
        ev = []
        b = Pin(0, Pin.IN, Pin.PULL_UP)
        b.irq(lambda p: ev.append(("fall", time.ticks_ms())), trigger=Pin.IRQ_FALLING)
        ticks = []
        t = Timer(0)
        t.init(period=100, mode=Timer.PERIODIC, callback=lambda tm: ticks.append(1))
        time.sleep_ms(1000)
        t.deinit()
        print("falls", [e[1] for e in ev], "ticks", len(ticks), "level", b.value())
    """)
    inputs = {"buttons": [{"pin": 0, "at_ms": 300, "hold_ms": 200, "active_level": 0}]}
    r = run(p, max_seconds=5, inputs=inputs, echo=False)
    assert "falls [300] ticks 10 level 1" in r.console


def test_deepsleep_reboots_with_reset_cause_and_rtc_memory(tmp_path):
    p = fw(tmp_path, """
        import machine
        rtc = machine.RTC()
        n = int(rtc.memory() or b"0") + 1
        rtc.memory(str(n).encode())
        print("boot", n, machine.reset_cause() == machine.DEEPSLEEP_RESET,
              machine.wake_reason() == machine.TIMER_WAKE)
        if n < 3:
            machine.deepsleep(1000)
    """)
    r = run(p, max_seconds=10, echo=False)
    assert r.boots == 3 and r.stop_reason == "finished"
    assert "boot 1 False False" in r.console and "boot 3 True True" in r.console
    assert r.rt.stats["deepsleep_ms"] == 2000


def test_wdt_resets_when_not_fed(tmp_path):
    p = fw(tmp_path, """
        import machine, time
        print("cause", machine.reset_cause())
        if machine.reset_cause() != machine.WDT_RESET:
            w = machine.WDT(timeout=2000)
            time.sleep(5)
    """)
    r = run(p, max_seconds=10, echo=False)
    assert r.boots == 2 and "cause 3" in r.console and 1999 <= r.virtual_ms <= 2001


def test_lightsleep_wakes_on_ext0(tmp_path):
    p = fw(tmp_path, """
        import machine, esp32
        from machine import Pin
        esp32.wake_on_ext0(Pin(4, Pin.IN, Pin.PULL_UP), esp32.WAKEUP_ALL_LOW)
        machine.lightsleep(10000)
        print("woke", machine.wake_reason())
    """)
    r = run(p, max_seconds=20, inputs={"pins": {"4": [[0, 1], [1234, 0]]}}, echo=False)
    assert "woke 2" in r.console and r.virtual_ms == 1234


def test_unsupported_api_is_reported(tmp_path):
    p = fw(tmp_path, """
        import machine
        machine.mem32[0x3FF00000] = 1
    """)
    r = run(p, max_seconds=1, echo=False)
    assert r.stop_reason == "exception" and "machine.mem32" in r.unsupported
    assert "not implemented by the simulator" in r.error


def test_unsupported_module_imports_but_fails_on_use(tmp_path):
    p = fw(tmp_path, """
        import neopixel
        neopixel.NeoPixel(1, 8)
    """)
    r = run(p, max_seconds=1, echo=False)
    assert "neopixel.NeoPixel" in r.unsupported


def test_real_modules_restored_after_run(tmp_path):
    import time as t1
    import random as r1
    p = fw(tmp_path, "import time, random, machine\n")
    run(p, max_seconds=1, echo=False)
    assert sys.modules["time"] is t1 and sys.modules["random"] is r1
    assert "machine" not in sys.modules


def test_session_limit_raises_simstop():
    with pytest.raises(SimStop):
        with session(max_seconds=1, echo=False):
            import time
            time.sleep(2)


def test_i2c_scan_and_missing_device(tmp_path):
    p = fw(tmp_path, """
        from machine import I2C, Pin
        i2c = I2C(0, scl=Pin(9), sda=Pin(8))
        print("scan", i2c.scan())
        i2c.writeto_mem(0x68, 0x10, b"\\x05")
        print("mem", i2c.readfrom_mem(0x68, 0x10, 1), i2c.readfrom_mem(0x68, 0x75, 1))
        try:
            i2c.writeto(0x50, b"x")
        except OSError as e:
            print("nack", e.args[0])
    """)
    r = run(p, max_seconds=1, inputs={"i2c_devices": [0x3C, 0x68], "i2c_registers": {"104": {"117": [0x68]}}},
            echo=False)
    assert "scan [60, 104]" in r.console
    assert "mem b'\\x05' b'h'" in r.console and "nack 19" in r.console
