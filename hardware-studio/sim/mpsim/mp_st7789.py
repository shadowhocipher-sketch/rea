"""Simulated ST7789 colour LCD driver (module names ``st7789`` and ``st7789py``).

Two usage styles are supported:

1. ``ST7789`` - direct-draw API of the widely used pure-Python driver
   st7789py_mpy by Russ Hughes (MIT):
   https://github.com/russhughes/st7789py_mpy/blob/master/lib/st7789py.py
   Constructor ``ST7789(spi, width, height, reset=None, dc=None, cs=None,
   backlight=None, rotation=0, color_order=BGR, custom_init=None,
   custom_rotations=None)``; methods fill, pixel, hline, vline, line, rect,
   fill_rect, blit_buffer, text(font, ...), polygon, rotation, sleep_mode,
   inversion_mode, hard_reset, soft_reset, init, vscrdef, vscsad; ``color565``
   and the colour constants.  The C-module variant (st7789_mpy) needs an extra
   ``init()`` call; that is accepted too.
   Direct-draw panels have no ``show()``; the simulator records a frame
   whenever the firmware sleeps (or the run ends) after drawing something.

2. ``ST7789_FB`` - "framebuf RGB565 + show()" style: a FrameBuffer subclass
   (RGB565) whose ``show()`` records a frame.  This mirrors drivers that keep a
   full RGB565 framebuffer in RAM and push it in one go.  The simulator assumes
   such a driver performs any byte swapping itself, i.e. ``fb.pixel(x, y, c)``
   with c = color565(...) shows colour c.

Byte order: ``blit_buffer()`` interprets the buffer as the panel does over SPI,
big-endian RGB565 (st7789py packs pixels with ">H").  A MicroPython
``framebuf.RGB565`` buffer is little-endian on ESP32, so blitting it raw shows
byte-swapped colours on hardware - and in this simulator.  Pre-swap colours
(e.g. ``((c & 0xFF) << 8) | (c >> 8)``) as you would on hardware.

Unsupported (raise SimUnsupported): bitmap, pbitmap, write, write_width (they
need converted font/bitmap modules).  Hardware scrolling (vscrdef/vscsad) is
recorded but not rendered.
"""

import numpy as np

from . import mp_framebuf as framebuf
from .runtime import unsupported as _r_unsupported
from .runtime import current

BLACK = 0x0000
BLUE = 0x001F
RED = 0xF800
GREEN = 0x07E0
CYAN = 0x07FF
MAGENTA = 0xF81F
YELLOW = 0xFFE0
WHITE = 0xFFFF
RGB = 0x00
BGR = 0x08

# sizes st7789py ships rotation tables for; other sizes are accepted with a warning
_KNOWN_SIZES = ((320, 240), (240, 320), (240, 240), (135, 240), (128, 128), (170, 320), (172, 320))


def color565(red, green=0, blue=0):
    if isinstance(red, (tuple, list)):
        red, green, blue = red[:3]
    return (red & 0xF8) << 8 | (green & 0xFC) << 3 | blue >> 3


def rgb565_to_rgb(arr):
    """uint16 RGB565 values (any shape) -> uint8 RGB array (..., 3)."""
    a = np.asarray(arr, dtype=np.uint32)
    r = ((a >> 11) & 0x1F) * 255 // 31
    g = ((a >> 5) & 0x3F) * 255 // 63
    b = (a & 0x1F) * 255 // 31
    return np.stack([r, g, b], axis=-1).astype(np.uint8)


def _backlight_level(rt, backlight):
    """0..1 brightness from a backlight Pin (on/off) or a PWM on that pin."""
    if backlight is None:
        return 1.0
    pid = getattr(backlight, "_id", None)
    if pid in rt.pwm:
        return rt.pwm[pid]["duty_u16"] / 65535.0
    st = rt.pins.get(pid)
    if st is None:
        return 1.0
    return 1.0 if st.get("out") else 0.0


class ST7789:
    _sim_kind = "lcd"

    def __init__(self, spi, width, height, reset=None, dc=None, cs=None, backlight=None,
                 rotation=0, color_order=BGR, custom_init=None, custom_rotations=None, **kw):
        rt = current()
        rt.check()
        if dc is None:
            raise ValueError("dc pin is required.")
        if (width, height) not in _KNOWN_SIZES:
            rt.warn("ST7789 %dx%d is not one of st7789py's built-in sizes; the real driver "
                    "raises ValueError unless custom_rotations is given" % (width, height))
        self.physical_width = width
        self.physical_height = height
        self.spi = spi
        self.reset = reset
        self.dc = dc
        self.cs = cs
        self.backlight = backlight
        self.color_order = color_order
        self._phys = np.zeros((height, width), dtype=np.uint16)
        self._sleeping = False
        self._inv = True       # st7789py's init sequence turns inversion ON (INVON)
        self._dirty = False
        self._scroll_warned = False
        self._sim_id = "st7789#%d" % len(rt.displays)
        rt.register_display(self)
        rt.add_idle_hook(self._sim_idle)
        self.hard_reset()
        self.rotation(rotation)
        self.fill(0)
        if backlight is not None:
            backlight.value(1)

    # ------------------------------------------------------------ control
    def init(self, *args, **kw):
        current().record("st7789_init", id=self._sim_id)

    def hard_reset(self):
        current().record("st7789_hard_reset", id=self._sim_id)

    def soft_reset(self):
        current().record("st7789_soft_reset", id=self._sim_id)

    def sleep_mode(self, value):
        self._sleeping = bool(value)
        self._dirty = True

    def inversion_mode(self, value):
        self._inv = bool(value)
        self._dirty = True

    def rotation(self, rotation):
        self._rotation = int(rotation) % 4
        self._view = np.rot90(self._phys, k=-self._rotation)
        self.height, self.width = self._view.shape
        self._dirty = True

    def vscrdef(self, tfa, vsa, bfa):
        current().warn("ST7789 hardware scrolling (vscrdef/vscsad) is recorded but not rendered")

    def vscsad(self, vssa):
        current().record("st7789_vscsad", value=vssa)

    # ------------------------------------------------------------ drawing
    def fill_rect(self, x, y, width, height, color):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1 = min(self.width, int(x) + int(width))
        y1 = min(self.height, int(y) + int(height))
        if x1 > x0 and y1 > y0:
            self._view[y0:y1, x0:x1] = int(color) & 0xFFFF
            self._dirty = True

    def fill(self, color):
        self._view[:, :] = int(color) & 0xFFFF
        self._dirty = True

    def pixel(self, x, y, color):
        x, y = int(x), int(y)
        if 0 <= x < self.width and 0 <= y < self.height:
            self._view[y, x] = int(color) & 0xFFFF
            self._dirty = True

    def hline(self, x, y, length, color):
        self.fill_rect(x, y, length, 1, color)

    def vline(self, x, y, length, color):
        self.fill_rect(x, y, 1, length, color)

    def rect(self, x, y, w, h, color):
        self.hline(x, y, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)
        self.hline(x, y + h - 1, w, color)

    def line(self, x0, y0, x1, y1, color):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0, x1, y1 = y0, x0, y1, x1
        if x0 > x1:
            x0, x1, y0, y1 = x1, x0, y1, y0
        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx // 2
        ystep = 1 if y0 < y1 else -1
        while x0 <= x1:
            if steep:
                self.pixel(y0, x0, color)
            else:
                self.pixel(x0, y0, color)
            err -= dy
            if err < 0:
                y0 += ystep
                err += dx
            x0 += 1

    def blit_buffer(self, buffer, x, y, width, height):
        data = np.frombuffer(bytes(buffer), dtype=">u2")
        n = int(width) * int(height)
        if len(data) < n:
            data = np.concatenate([data, np.zeros(n - len(data), ">u2")])
        img = data[:n].reshape(int(height), int(width)).astype(np.uint16)
        x, y = int(x), int(y)
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.width, x + int(width)), min(self.height, y + int(height))
        if x1 > x0 and y1 > y0:
            self._view[y0:y1, x0:x1] = img[y0 - y:y1 - y, x0 - x:x1 - x]
            self._dirty = True

    def text(self, font, text, x0, y0, color=WHITE, background=BLACK):
        fw, fh = font.WIDTH, font.HEIGHT
        bpr = (fw + 7) // 8
        glyph_bytes = bpr * fh
        data = font.FONT
        x = int(x0)
        for ch in str(text):
            c = ord(ch)
            if font.FIRST <= c < font.LAST:
                base = (c - font.FIRST) * glyph_bytes
                cell = np.full((fh, fw), int(background) & 0xFFFF, np.uint16)
                for row in range(fh):
                    for b in range(bpr):
                        byte = data[base + row * bpr + b]
                        for bit in range(8):
                            col = b * 8 + bit
                            if col < fw and byte & (0x80 >> bit):
                                cell[row, col] = int(color) & 0xFFFF
                xs0, ys0 = max(0, x), max(0, int(y0))
                xs1, ys1 = min(self.width, x + fw), min(self.height, int(y0) + fh)
                if xs1 > xs0 and ys1 > ys0:
                    self._view[ys0:ys1, xs0:xs1] = cell[ys0 - int(y0):ys1 - int(y0), xs0 - x:xs1 - x]
                    self._dirty = True
                x += fw

    def polygon(self, points, x, y, color, angle=0, center_x=0, center_y=0):
        import math
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        rot = [(int(center_x + (px - center_x) * cos_a - (py - center_y) * sin_a + x),
                int(center_y + (px - center_x) * sin_a + (py - center_y) * cos_a + y))
               for px, py in points]
        for i in range(1, len(rot)):
            self.line(rot[i - 1][0], rot[i - 1][1], rot[i][0], rot[i][1], color)

    # ------------------------------------------------------------ sim
    def _sim_rgb(self):
        rgb = rgb565_to_rgb(self._view)
        if not self._inv:
            rgb = 255 - rgb
        level = _backlight_level(current(), self.backlight)
        if self._sleeping:
            level = 0.0
        if level < 1.0:
            rgb = (rgb.astype(np.float32) * level).astype(np.uint8)
        return rgb

    def _sim_idle(self):
        if self._dirty:
            self._dirty = False
            current().record_frame(self._sim_id, "lcd", self._sim_rgb(), {"event": "idle"})

    def __getattr__(self, name):
        raise _r_unsupported("st7789.ST7789", name)


class ST7789_FB(framebuf.FrameBuffer):
    """RGB565 framebuffer + show() style driver (see module docstring)."""
    _sim_kind = "lcd"

    def __init__(self, spi=None, width=240, height=240, reset=None, dc=None, cs=None,
                 backlight=None, rotation=0, **kw):
        rt = current()
        rt.check()
        if rotation % 2:
            width, height = height, width
        self.width = width
        self.height = height
        self.backlight = backlight
        self.buffer = bytearray(width * height * 2)
        super().__init__(self.buffer, width, height, framebuf.RGB565)
        self._sim_id = "st7789fb#%d" % len(rt.displays)
        rt.register_display(self)
        if backlight is not None:
            backlight.value(1)

    def show(self):
        rt = current()
        rgb = rgb565_to_rgb(self._sim_pixels())
        level = _backlight_level(rt, self.backlight)
        if level < 1.0:
            rgb = (rgb.astype(np.float32) * level).astype(np.uint8)
        rt.record_frame(self._sim_id, "lcd", rgb, {"event": "show"})


def __getattr__(name):
    raise _r_unsupported("st7789", name)
