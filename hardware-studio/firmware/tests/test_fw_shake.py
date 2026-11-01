"""shake.py template: register values vs. the LIS3DH datasheet tables, INT1 edge
handling, deep-sleep wake on INT1, and the software detector.

Simulator-only: the simulated I2C device is a register table, not a sensor model,
so this does not validate thresholds or behaviour on hardware.
"""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.normpath(os.path.join(HERE, "..", "templates"))
SIM = os.path.normpath(os.path.join(HERE, "..", "..", "sim"))
sys.path.insert(0, SIM)

from mpsim import run, session  # noqa: E402

ACC = {"i2c_devices": [0x18], "i2c_registers": {"24": {"15": [0x33]}}}


def test_motion_registers_match_datasheet_bits():
    with session(max_seconds=5, paths=[TEMPLATES], echo=False):
        from shake import motion_registers
        regs = dict(motion_registers(1600, odr_hz=50, range_g=4))
        assert regs[0x20] == 0x4F          # ODR 0100 (50 Hz) | LPen | Z Y X enable  (Table 29-31)
        assert regs[0x23] == 0x10          # FS = 01 -> +-4 g                      (Table 37-38)
        assert regs[0x32] == 50            # 1600 mg / 32 mg per LSb               (Table 59)
        assert regs[0x30] == 0x2A          # ZHIE | YHIE | XHIE, OR                (Table 53-55)
        assert regs[0x22] == 0x40          # I1_IA1                                (Table 35-36)
        assert regs[0x24] == 0x08          # LIR_INT1                              (Table 40-41)
        assert regs[0x25] == 0x00          # active-high                           (Table 43)
        # 1 g of gravity would trigger forever without the high-pass filter
        with pytest.raises(ValueError):
            motion_registers(900, range_g=2)
        assert dict(motion_registers(300, range_g=2, hp_filter=True))[0x21] == 0x01
        with pytest.raises(ValueError):
            motion_registers(5000, range_g=2)   # 312 LSb > 127
        with pytest.raises(ValueError):
            motion_registers(1600, odr_hz=60)


def test_sensor_probe_and_register_writes():
    with session(inputs=ACC, max_seconds=5, paths=[TEMPLATES], echo=False) as s:
        from machine import I2C, Pin
        from shake import LIS3DH, SensorError
        i2c = I2C(0, sda=Pin(4), scl=Pin(5))
        acc = LIS3DH(i2c)
        assert acc.addr == 0x18
        acc.setup_motion_interrupt(1600, odr_hz=50, range_g=4)
        mem = s.rt.i2c_mem[0x18]
        assert (mem[0x20], mem[0x23], mem[0x32], mem[0x30], mem[0x22]) == (0x4F, 0x10, 50, 0x2A, 0x40)
        with pytest.raises(SensorError, match="0x19"):
            LIS3DH(i2c, addr=0x19)          # explicit address that does not answer


def test_wrong_who_am_i_is_rejected():
    bad = {"i2c_devices": [0x19], "i2c_registers": {"25": {"15": [0x44]}}}
    with session(inputs=bad, max_seconds=5, paths=[TEMPLATES], echo=False):
        from machine import I2C, Pin
        from shake import LIS3DH, SensorError
        with pytest.raises(SensorError, match="0x44"):
            LIS3DH(I2C(0, sda=Pin(4), scl=Pin(5)))


def test_int1_edges_become_shakes_with_cooldown():
    pulses = [[0, 0]]
    for t in (1000, 1300, 2500, 2550, 4000):      # 1300 and 2550 fall inside the 800 ms cooldown
        pulses += [[t, 1], [t + 40, 0]]
    inputs = dict(ACC, pins={"3": pulses})
    with session(inputs=inputs, max_seconds=10, paths=[TEMPLATES], echo=False):
        import time
        from machine import Pin
        from shake import ShakeInput
        sh = ShakeInput(Pin(3, Pin.IN, Pin.PULL_DOWN), None, cooldown_ms=800)
        hits = []
        for _ in range(250):                       # 5 s at 20 ms
            if sh.update():
                hits.append(time.ticks_ms())
            time.sleep_ms(20)
        assert [round(h, -2) for h in hits] == [1000, 2500, 4000]
        assert sh.count == 3 and sh.ignored == 2


def test_software_detector():
    with session(max_seconds=5, paths=[TEMPLATES], echo=False):
        from shake import ShakeDetector
        d = ShakeDetector(delta_mg=600, peaks=3, window_ms=600, cooldown_ms=800)
        rest = [d.feed(t, 0, 0, 1000) for t in range(0, 1000, 20)]
        assert not any(rest)
        got = [t for t in range(1000, 3000, 20)
               if d.feed(t, 1800 if (t // 20) % 2 else -1800, 0, 1000)]
        # shaking 2 s: first shake at the 3rd peak, then one per cooldown
        assert got[0] == 1040 and all(b - a >= 800 for a, b in zip(got, got[1:]))
        assert not d.feed(5000, 0, 0, 1000)


def test_demo_runs_with_eval_stimulus_and_reports_shakes():
    stim = dict(ACC, i2c_devices=[0x18, 0x3C], pins={"3": [[0, 0], [1000, 1], [1040, 0], [3000, 1], [3040, 0]]})
    r = run(os.path.join(TEMPLATES, "shake.py"), inputs=stim, max_seconds=5, echo=False)
    assert r.error is None and r.stop_reason == "time_limit"
    assert "SELFTEST accel OK addr=0x18" in r.console
    assert [int(n) for n in re.findall(r"EVENT shake (\d+)", r.console)] == [1, 2]


def test_deep_sleep_wakes_on_int1():
    src = (
        "import machine, time\n"
        "from machine import Pin\n"
        "from shake import wake_on_int1\n"
        "if machine.reset_cause() == machine.DEEPSLEEP_RESET:\n"
        "    print('WOKE', machine.wake_reason())\n"
        "    while True: time.sleep(1)\n"
        "p = Pin(3, Pin.IN, Pin.PULL_DOWN)\n"
        "print('API', wake_on_int1(p))\n"
        "machine.deepsleep()\n"
    )
    import shutil
    import tempfile
    d = tempfile.mkdtemp()
    try:
        shutil.copy(os.path.join(TEMPLATES, "shake.py"), d)
        fw = os.path.join(d, "main.py")
        with open(fw, "w") as f:
            f.write(src)
        r = run(fw, inputs={"pins": {"3": [[0, 0], [7000, 1], [7040, 0]]}}, max_seconds=10, echo=False)
    finally:
        shutil.rmtree(d)
    assert "API wake_on_gpio" in r.console
    assert r.boots == 2 and "WOKE" in r.console
    assert 7000 <= r.rt.stats["deepsleep_ms"] < 7100     # slept until the INT1 pulse
