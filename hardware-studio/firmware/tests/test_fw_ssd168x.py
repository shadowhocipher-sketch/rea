"""firmware/drivers/ssd168x.py: SPI command stream vs. the SSD1680/SSD1681 datasheet flow,
BUSY handling, API parity with the simulator's e-paper model, and the example firmware.

The driver is executed under CPython inside an mpsim session (framebuf + virtual-clock
time), talking to FAKE SPI/Pin objects that record every byte.  This checks the command
order and parameters against the datasheet; it does NOT show that a real panel works.

Datasheet flow ([DS1680] SSD1680 Rev 0.14 s9.1 Fig 9-1, identical in [DS1681] s8.1):
  2. HW reset, SW reset 0x12, wait 10 ms   3. 0x01, 0x11, 0x44, 0x45, 0x3C
  4. 0x18, 0x22 + 0x20 (load LUT), wait BUSY low
  5. 0x4E, 0x4F, 0x24, 0x26, 0x22 + 0x20, wait BUSY low   6. deep sleep 0x10
"""
import importlib.util
import inspect
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
FW = os.path.normpath(os.path.join(HERE, ".."))
DRIVER = os.path.join(FW, "drivers", "ssd168x.py")
EXAMPLE = os.path.join(FW, "examples", "epaper_hello.py")
SIM = os.path.normpath(os.path.join(HERE, "..", "..", "sim"))
sys.path.insert(0, SIM)

from mpsim import run, session  # noqa: E402

# modelled BUSY-high times (us) after each operation; arbitrary but distinct values
BUSY_US = {"hw_reset": 1_000, 0x12: 2_000, 0xB1: 50_000, 0xF7: 2_000_000, 0xFF: 300_000}


class Bus:
    """Fake panel: pins + SPI that record traffic and model BUSY on the virtual clock."""

    def __init__(self, rt, stuck_busy=False):
        self.rt = rt
        self.cmds = []          # [cmd, bytearray(data)]
        self.events = []        # ("pin", name, value, t_us) / ("cmd", code, t_us)
        self.busy_until = 0
        self.asleep = False
        self.stuck = stuck_busy
        self.update_ctrl = None
        self.violations = []
        bus = self

        class FakePin:
            def __init__(self, name, level=1):
                self.name, self.level = name, level

            def value(self, v=None):
                if v is None:
                    if self.name == "busy":
                        return 1 if bus.is_busy() else 0
                    return self.level
                v = 1 if v else 0
                if self.name == "rst" and self.level == 0 and v == 1:
                    bus.asleep = False                       # HW reset leaves deep sleep
                    bus.busy_until = bus.rt.now_us + BUSY_US["hw_reset"]
                self.level = v
                bus.events.append(("pin", self.name, v, bus.rt.now_us))

            __call__ = value

        class FakeSPI:
            def write(self, data):
                data = bytes(data)
                if bus.cs.level != 0:
                    bus.violations.append("SPI write with CS high")
                if bus.is_busy():
                    bus.violations.append("SPI write while BUSY high (cmd stream %r)"
                                          % [hex(c[0]) for c in bus.cmds[-3:]])
                if bus.dc.level == 0:
                    for b in data:
                        bus.command(b)
                else:
                    bus.cmds[-1][1].extend(data)
                    if bus.cmds[-1][0] == 0x10 and data[0] & 0x03:
                        bus.asleep = True   # BUSY stays high once deep sleep starts [DS1680] 10h

        self.cs, self.dc, self.rst, self.busy = (FakePin("cs"), FakePin("dc"), FakePin("rst"),
                                                 FakePin("busy", 0))
        self.spi = FakeSPI()

    def is_busy(self):
        return self.stuck or self.asleep or self.rt.now_us < self.busy_until

    def command(self, b):
        # parameters of the previous command are complete now
        if self.cmds and self.cmds[-1][0] == 0x22:
            self.update_ctrl = self.cmds[-1][1][0]
        self.cmds.append([b, bytearray()])
        self.events.append(("cmd", b, self.rt.now_us))
        if b == 0x12:
            self.busy_until = self.rt.now_us + BUSY_US[0x12]
        elif b == 0x20:
            self.busy_until = self.rt.now_us + BUSY_US[self.update_ctrl]

    def codes(self, start=0):
        return [c for c, _ in self.cmds[start:]]

    def params(self, code, start=0):
        return [bytes(d) for c, d in self.cmds[start:] if c == code]

    def args(self):
        return (self.spi, self.cs, self.dc, self.rst, self.busy)


def load_driver():
    spec = importlib.util.spec_from_file_location("ssd168x_hw", DRIVER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


INIT = [0x12, 0x01, 0x11, 0x44, 0x45, 0x3C, 0x18, 0x22, 0x20]
REFRESH = [0x3C, 0x4E, 0x4F, 0x24, 0x4E, 0x4F, 0x26, 0x22, 0x20]


def test_init_sequence_matches_datasheet_flow():
    with session(max_seconds=60, echo=False) as s:
        drv = load_driver()
        bus = Bus(s.rt)
        epd = drv.SSD1681(*bus.args())
        assert bus.codes() == INIT
        p = dict((c, bytes(d)) for c, d in bus.cmds)
        assert p[0x01] == bytes((199, 0, 0))          # MUX = 200 gates - 1, scan B[2:0] = 000
        assert p[0x11] == b"\x03"                       # X+, Y+, X first (POR)
        assert p[0x44] == bytes((0, 200 // 8 - 1))      # X window in bytes
        assert p[0x45] == bytes((0, 0, 199, 0))         # Y window 0..199
        assert p[0x3C] == b"\x05" and p[0x18] == b"\x80" and p[0x22] == b"\xb1"
        assert bus.violations == []                     # never talked while BUSY was high
        # RES# pulsed low >= 10 ms before SW reset; SW reset waited >= 10 ms
        rst = [(v, t) for k, n, v, t in [e for e in bus.events if e[0] == "pin"] if n == "rst"]
        lows = [t for v, t in rst if v == 0]
        highs = [t for v, t in rst if v == 1 and t > lows[0]]
        assert highs[0] - lows[0] >= 10_000
        t12 = [e[2] for e in bus.events if e[0] == "cmd" and e[1] == 0x12][0]
        t01 = [e[2] for e in bus.events if e[0] == "cmd" and e[1] == 0x01][0]
        assert t12 > highs[0] and t01 - t12 >= 10_000
        # SSD1680 2.13" default: 122 x 250 -> 16 bytes per row, 250 gates
        bus2 = Bus(s.rt)
        drv.SSD1680(*bus2.args())
        p2 = dict((c, bytes(d)) for c, d in bus2.cmds)
        assert p2[0x01] == bytes((249, 0, 0)) and p2[0x44] == bytes((0, 15))
        assert p2[0x45] == bytes((0, 0, 249, 0))
        assert epd.width == 200 and epd.height == 200


def test_full_and_partial_refresh_sequences_and_ram_content():
    with session(max_seconds=60, echo=False) as s:
        drv = load_driver()
        bus = Bus(s.rt)
        epd = drv.SSD1681(*bus.args())
        n0 = len(bus.cmds)
        epd.fill(drv.WHITE)
        epd.fill_rect(0, 0, 8, 2, drv.BLACK)
        epd.show()
        assert bus.codes(n0) == REFRESH
        assert bus.params(0x3C, n0) == [b"\x05"] and bus.params(0x22, n0) == [b"\xf7"]
        assert bus.params(0x4E, n0) == [b"\x00"] * 2 and bus.params(0x4F, n0) == [b"\x00\x00"] * 2
        bw = bus.params(0x24, n0)[0]
        assert len(bw) == 25 * 200 and bw[0] == 0x00 and bw[25] == 0x00 and bw[1] == 0xFF
        assert bus.params(0x26, n0)[0] == bw            # B/W panel: both RAMs equal after full
        first = bytes(bw)
        n1 = len(bus.cmds)
        epd.fill_rect(0, 0, 8, 2, drv.WHITE)
        epd.pixel(199, 199, drv.BLACK)
        epd.show_partial()
        assert bus.codes(n1) == REFRESH
        assert bus.params(0x3C, n1) == [b"\x80"] and bus.params(0x22, n1) == [b"\xff"]
        new = bus.params(0x24, n1)[0]
        assert bus.params(0x26, n1)[0] == first           # old image for Display Mode 2
        assert new[0] == 0xFF and new[-1] == 0xFE
        n2 = len(bus.cmds)
        epd.show(full=False)
        assert bus.params(0x26, n2)[0] == new and bus.params(0x22, n2) == [b"\xff"]
        assert (epd.full_refreshes, epd.partial_refreshes) == (1, 2)
        # measured BUSY time: 2000 + 2 x 300 ms (poll granularity 5 ms + tick polling)
        assert 2600 <= epd.refresh_ms_total <= 2600 + 3 * 7
        assert bus.violations == []


def test_sleep_then_refresh_resets_and_reinitialises():
    with session(max_seconds=60, echo=False) as s:
        drv = load_driver()
        bus = Bus(s.rt)
        epd = drv.SSD1680(*bus.args())
        epd.show()
        n = len(bus.cmds)
        epd.sleep()
        assert bus.codes(n) == [0x10] and bus.params(0x10, n) == [b"\x01"]   # deep sleep mode 1
        epd.show_partial()
        assert bus.codes(n + 1) == INIT + REFRESH        # HW reset first: no command while asleep
        assert bus.violations == []
        epd2 = drv.SSD1680(bus.spi, bus.cs, bus.dc, None, bus.busy)
        with pytest.raises(ValueError):
            epd2.sleep()                                   # only RES# leaves deep sleep


def test_busy_timeout_raises():
    with session(max_seconds=120, echo=False) as s:
        drv = load_driver()
        bus = Bus(s.rt)
        epd = drv.SSD1681(*bus.args(), busy_timeout_ms=1500)
        bus.stuck = True
        t0 = s.rt.now_us
        with pytest.raises(drv.BusyTimeout) as ei:
            epd.show()
        assert isinstance(ei.value, OSError)
        assert 1500 <= (s.rt.now_us - t0) / 1000 <= 1600
        assert epd.full_refreshes == 0
        # default timeout = max(5 s, 3 x expected refresh time)
        bus2 = Bus(s.rt, stuck_busy=True)
        t0 = s.rt.now_us
        with pytest.raises(drv.BusyTimeout):
            drv.SSD1680(*bus2.args())
        assert 5000 <= (s.rt.now_us - t0) / 1000 <= 5100


def test_rotation_maps_logical_pixels_to_panel_ram():
    with session(max_seconds=60, echo=False) as s:
        drv = load_driver()
        bus = Bus(s.rt)
        epd = drv.SSD1680(*bus.args(), rotation=1)
        assert (epd.width, epd.height) == (250, 122)
        epd.fill(drv.WHITE)
        epd.pixel(0, 0, drv.BLACK)
        epd.pixel(5, 3, drv.BLACK)
        n = len(bus.cmds)
        epd.show()
        ram = bus.params(0x24, n)[0]
        assert len(ram) == 16 * 250

        def black(px, py):
            return not (ram[py * 16 + px // 8] >> (7 - px % 8)) & 1
        assert black(121, 0) and black(121 - 3, 5)       # rotation 1: (x, y) -> (W-1-y, x)
        assert sum(8 - bin(b).count("1") for b in ram) == 2 + 6 * 250   # + 6 padding bits/row


def test_red_panel_writes_red_ram_and_partial_falls_back_to_full():
    with session(max_seconds=120, echo=False) as s:
        drv = load_driver()
        bus = Bus(s.rt)
        epd = drv.SSD1681(*bus.args(), red=True)
        epd.fill(drv.WHITE)
        epd.red.pixel(1, 0, drv.RED)
        n = len(bus.cmds)
        epd.show_partial()
        assert bus.params(0x22, n) == [b"\xf7"] and epd.full_refreshes == 1
        red = bus.params(0x26, n)[0]
        assert red[0] == 0x40 and not any(red[1:])
    assert "not supported on 3-colour" in s.console


def test_same_drawing_code_gives_same_pixels_in_sim_and_driver():
    def draw(mod, epd):
        epd.fill(mod.WHITE)
        epd.rect(0, 0, epd.width, epd.height, mod.BLACK)
        epd.text("Hi 42", 10, 10, mod.BLACK)
        epd.ellipse(100, 120, 30, 20, mod.BLACK, True)
        epd.show()

    with session(max_seconds=60, echo=False) as s:
        import epaper
        from machine import Pin, SPI
        sim = epaper.SSD1681(SPI(1), Pin(10, Pin.OUT), Pin(9, Pin.OUT), Pin(8, Pin.OUT), Pin(7, Pin.IN))
        draw(epaper, sim)
        frame = s.rt.frames[-1].rgb
        drv = load_driver()
        bus = Bus(s.rt)
        hw = drv.SSD1681(*bus.args())
        n = len(bus.cmds)
        draw(drv, hw)
        ram = bus.params(0x24, n)[0]
    bits = [(ram[y * 25 + x // 8] >> (7 - x % 8)) & 1 for y in range(200) for x in range(200)]
    hw_black = [b == 0 for b in bits]
    sim_black = [bool(v) for v in (frame[:, :, 0] < 128).flatten()]
    assert hw_black == sim_black and sum(hw_black) > 500


def test_api_matches_simulator_model():
    with session(max_seconds=10, echo=False):
        import epaper as simmod
        drv = load_driver()
        for name in ("SSD1680", "SSD1681", "WHITE", "BLACK", "RED", "BusyTimeout"):
            assert hasattr(simmod, name) and hasattr(drv, name), name
            if name in ("WHITE", "BLACK", "RED"):
                assert getattr(simmod, name) == getattr(drv, name)
        for cls in ("SSD1680", "SSD1681"):
            a, b = getattr(simmod, cls), getattr(drv, cls)
            assert (a.PHYS_W, a.PHYS_H, a.FULL_MS, a.PARTIAL_MS) == (b.PHYS_W, b.PHYS_H, b.FULL_MS, b.PARTIAL_MS)
            assert list(inspect.signature(a.__init__).parameters) == list(inspect.signature(b.__init__).parameters)
            for m in ("show", "display", "refresh", "show_partial", "display_partial", "partial",
                      "clear", "sleep", "init", "wait_busy", "fill", "text", "pixel", "blit"):
                assert callable(getattr(a, m)) and callable(getattr(b, m)), m
        bus = Bus(__import__("mpsim.runtime", fromlist=["current"]).current())
        hw = drv.SSD1681(*bus.args())
        from machine import Pin, SPI
        sm = simmod.SSD1681(SPI(1), Pin(10, Pin.OUT), Pin(9, Pin.OUT), Pin(8, Pin.OUT), Pin(7, Pin.IN))
        for attr in ("width", "height", "rotation", "buffer", "red", "full_refreshes",
                     "partial_refreshes", "refresh_ms_total", "full_refresh_ms",
                     "partial_refresh_ms", "busy_timeout_ms"):
            assert hasattr(hw, attr) and hasattr(sm, attr), attr
        assert len(hw.buffer) == len(sm.buffer)
        sm.rst = None
        with pytest.raises(ValueError):
            sm.sleep()                                     # simulator enforces the same rule


def test_example_firmware_runs_in_simulator():
    r = run(EXAMPLE, display="epaper", max_seconds=120, echo=False)
    assert r.stop_reason == "finished", r.error
    assert "done full=1 partial=5" in r.console
    assert len(r.frames) == 6 and r.frames[0].rgb.shape[:2] == (200, 200)
    assert r.rt.stats["epaper"]["ssd1681#0"] == {"full": 1, "partial": 5, "refresh_ms": 2000 + 5 * 260}
    assert not [w for w in r.warnings if "partial" in w or "sleep" in w]


def test_example_firmware_runs_unchanged_on_the_real_driver_over_simulated_machine():
    """Same example file, `ssd168x` = the hardware driver, machine.SPI/Pin = simulator."""
    with session(max_seconds=120, echo=False, inputs={"pins": {"7": [[0, 0]]}}) as s:
        sys.modules["ssd168x"] = load_driver()
        spec = importlib.util.spec_from_file_location("epaper_hello_hw", EXAMPLE)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.main()
        assert s.rt.frames == []                          # the real driver draws nothing here
        assert s.rt.spi_stats                              # but it did talk SPI
    assert "done full=1 partial=5" in s.console
