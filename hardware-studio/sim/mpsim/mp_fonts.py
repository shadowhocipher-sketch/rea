"""Fallback font modules for the st7789py ``text(font, ...)`` API.

st7789py ships converted PC-BIOS fonts as separate modules (``vga1_8x8``,
``vga1_8x16``, ``vga1_bold_16x32`` ...) that live on the device.  When the
firmware folder does not contain such a module, the simulator provides one
with the same attributes (WIDTH, HEIGHT, FIRST, LAST, FONT; rows MSB-left)
built from the public-domain font8x8 glyphs, scaled up for larger sizes.
Glyph shapes therefore differ from the real fonts; metrics are the same.
"""

import types

from . import font8x8

# module name -> (width, height)
FONT_SIZES = {
    "vga1_8x8": (8, 8), "vga2_8x8": (8, 8),
    "vga1_8x16": (8, 16), "vga2_8x16": (8, 16),
    "vga1_16x16": (16, 16), "vga2_16x16": (16, 16),
    "vga1_bold_16x16": (16, 16), "vga2_bold_16x16": (16, 16),
    "vga1_16x32": (16, 32), "vga2_16x32": (16, 32),
    "vga1_bold_16x32": (16, 32), "vga2_bold_16x32": (16, 32),
}


def _rev8(b):
    return int("{:08b}".format(b)[::-1], 2)


def make_font_module(name):
    w, h = FONT_SIZES[name]
    sx, sy = w // 8, h // 8
    data = bytearray()
    first, last = 0x20, 0x7F
    for code in range(first, last):
        rows = font8x8.glyph(code)
        for r in range(8):
            bits = _rev8(rows[r])  # -> MSB = leftmost
            if sx == 1:
                rowbytes = [bits]
            else:  # scale x2: each source bit becomes two bits
                v = 0
                for i in range(8):
                    if bits & (0x80 >> i):
                        v |= 0b11 << (14 - 2 * i)
                rowbytes = [v >> 8, v & 0xFF]
            for _ in range(sy):
                data.extend(rowbytes)
    m = types.ModuleType(name)
    m.__doc__ = "mpsim fallback font (font8x8, public domain, scaled)"
    m.WIDTH, m.HEIGHT, m.FIRST, m.LAST = w, h, first, last
    m.FONT = bytes(data)
    return m
