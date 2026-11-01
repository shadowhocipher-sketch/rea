"""Simulated SSD1680 / SSD1681 e-paper drivers (modules ``epaper``, ``ssd1680``, ``ssd1681``).

There is no single standard MicroPython e-paper driver, so this module defines a
small, explicit API that mirrors what common drivers do (FrameBuffer subclass +
full/partial refresh + deep sleep).  Real firmware that uses another driver
needs a thin adapter, or the user's driver file can be run on top of the
simulated ``machine.SPI`` (it will run, but no frames are captured).

API::

    epd = SSD1680(spi, cs, dc, rst, busy, width=122, height=250,
                  red=False, rotation=0, full_refresh_ms=None, partial_refresh_ms=None)
    epd.fill(WHITE); epd.text("hi", 0, 0, BLACK)    # FrameBuffer drawing, MONO_HLSB
    epd.red.fill_rect(...)                          # red layer (only when red=True), 1 = red
    epd.show()            # full refresh   (aliases: display(), refresh())
    epd.show_partial()    # partial refresh (aliases: display_partial(), partial())
    epd.clear()           # fill white + full refresh
    epd.sleep()           # deep sleep; init() must be called before the next refresh
    epd.full_refreshes, epd.partial_refreshes, epd.refresh_ms_total

Pixel values follow the controller RAM: in the black/white RAM 1 = white and
0 = black; in the red RAM 1 = red.  ``rotation`` 1/3 swaps the logical width
and height (landscape on a portrait panel).

Each refresh blocks for the refresh time (the BUSY pin stays high on hardware):
the simulator advances the virtual clock by that time.  Default times are NOT
datasheet values of the SSD1680/SSD1681 controller (refresh time depends on the
panel's waveform/LUT); they are panel-maker figures:

* SSD1680, 2.13" 250x122 B/W (Good Display GDEY0213B74): full 3 s, partial 0.3 s,
  25 C.  Source: https://www.good-display.com/product/391.html (manufacturer product
  page, seen via search result 2026-11-01; datasheet PDF not opened) - 待核实.
* SSD1681, 1.54" 200x200 B/W (Good Display GDEY0154D67): full 2 s, partial 0.26 s.
  Source: reseller listing https://eckstein-shop.de/Arduino_1__154_1__Arduino_1__ESP32_1__Neu_2
  (B level, 2026-11-01) - 待核实.
* Red/black/white panels: full refresh default 15 s = 估算 (no source found;
  3-colour waveforms are much longer than B/W, see forum note
  https://forum.arduino.cc/t/help-with-3-color-ssd1680-controller/944410, C level).
  Partial refresh is treated as not supported on 3-colour panels (a full
  refresh is done and a warning recorded).

Override with ``full_refresh_ms=`` / ``partial_refresh_ms=`` for your panel.

Partial refreshes leave ghosting on real panels; the simulator marks pixels that
went black -> white through a partial refresh as light grey until the next full
refresh (an illustration, not a physical model).
"""

import numpy as np

from . import mp_framebuf as framebuf
from .runtime import unsupported as _r_unsupported
from .runtime import current

WHITE = 1
BLACK = 0
RED = 1


class _EPD(framebuf.FrameBuffer):
    _sim_kind = "epaper"
    PHYS_W = 122
    PHYS_H = 250
    FULL_MS = 3000
    PARTIAL_MS = 300
    RED_FULL_MS = 15000
    CHIP = "ssd168x"

    def __init__(self, spi=None, cs=None, dc=None, rst=None, busy=None, width=None, height=None,
                 *, red=False, rotation=0, full_refresh_ms=None, partial_refresh_ms=None):
        rt = current()
        rt.check()
        pw = width or self.PHYS_W
        ph = height or self.PHYS_H
        self.rotation = int(rotation) % 4
        if self.rotation % 2:
            pw, ph = ph, pw
        self.width, self.height = pw, ph
        self.spi, self.cs, self.dc, self.rst, self.busy = spi, cs, dc, rst, busy
        self.has_red = bool(red)
        nbytes = ((self.width + 7) // 8) * self.height
        self.buffer = bytearray(b"\xff" * nbytes)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.red_buffer = bytearray(nbytes) if red else None
        self.red = framebuf.FrameBuffer(self.red_buffer, self.width, self.height,
                                        framebuf.MONO_HLSB) if red else None
        if full_refresh_ms is None:
            full_refresh_ms = self.RED_FULL_MS if red else self.FULL_MS
        self.full_refresh_ms = full_refresh_ms
        self.partial_refresh_ms = self.PARTIAL_MS if partial_refresh_ms is None else partial_refresh_ms
        self.full_refreshes = 0
        self.partial_refreshes = 0
        self.refresh_ms_total = 0
        self._asleep = True
        self._shown = None          # last displayed black mask
        self._ghost = None
        self._sim_id = "%s#%d" % (self.CHIP, len(rt.displays))
        rt.register_display(self)
        self.init()

    def init(self):
        rt = current()
        rt.check()
        if self.rst is not None:
            self.rst.value(0)
            rt.advance(10_000)
            self.rst.value(1)
            rt.advance(10_000)
        self._asleep = False
        rt.record("epaper_init", id=self._sim_id)

    def sleep(self):
        rt = current()
        rt.check()
        self._asleep = True
        rt.record("epaper_sleep", id=self._sim_id)

    def _refresh(self, partial):
        rt = current()
        rt.check()
        if self._asleep:
            rt.warn("%s: refresh after sleep() without init(); a real panel ignores commands "
                    "in deep sleep until reset. Simulator re-initialised it." % self._sim_id,
                    key=self._sim_id + "sleep")
            self.init()
        if partial and self.has_red:
            rt.warn("%s: partial refresh requested on a 3-colour panel; doing a full refresh"
                    % self._sim_id, key=self._sim_id + "redpartial")
            partial = False
        black = self._sim_pixels() == 0
        red = (self.red._sim_pixels() != 0) if self.has_red else np.zeros_like(black)
        if partial:
            self.partial_refreshes += 1
            dur = self.partial_refresh_ms
            if self._shown is not None:
                went_white = self._shown & ~black
                self._ghost = went_white if self._ghost is None else (self._ghost | went_white)
                self._ghost &= ~black
        else:
            self.full_refreshes += 1
            dur = self.full_refresh_ms
            self._ghost = None
        self._shown = black.copy()
        self.refresh_ms_total += dur
        rgb = np.full(black.shape + (3,), 255, np.uint8)
        if self._ghost is not None:
            rgb[self._ghost] = (200, 200, 200)
        rgb[black] = (0, 0, 0)
        rgb[red] = (255, 0, 0)
        st = rt.stats.setdefault("epaper", {})
        s = st.setdefault(self._sim_id, {"full": 0, "partial": 0, "refresh_ms": 0})
        s["full"], s["partial"], s["refresh_ms"] = self.full_refreshes, self.partial_refreshes, self.refresh_ms_total
        rt.record("epaper_refresh", id=self._sim_id, mode="partial" if partial else "full", ms=dur)
        rt.record_frame(self._sim_id, "epaper", rgb,
                        {"event": "refresh", "refresh": "partial" if partial else "full",
                         "duration_ms": dur, "count_full": self.full_refreshes,
                         "count_partial": self.partial_refreshes})
        rt.advance(int(dur * 1000))   # BUSY is high while the panel refreshes

    def show(self, full=True):
        self._refresh(partial=not full)

    display = show
    refresh = show

    def show_partial(self):
        self._refresh(partial=True)

    display_partial = show_partial
    partial = show_partial

    def clear(self, color=WHITE):
        self.fill(color)
        if self.has_red:
            self.red.fill(0)
        self._refresh(partial=False)


class SSD1680(_EPD):
    """2.13" class panels, 122x250 (portrait) by default."""
    PHYS_W, PHYS_H = 122, 250
    FULL_MS, PARTIAL_MS = 3000, 300
    CHIP = "ssd1680"


class SSD1681(_EPD):
    """1.54" class panels, 200x200 by default."""
    PHYS_W, PHYS_H = 200, 200
    FULL_MS, PARTIAL_MS = 2000, 260
    CHIP = "ssd1681"


def __getattr__(name):
    raise _r_unsupported("epaper", name)
