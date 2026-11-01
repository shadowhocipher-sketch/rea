"""Pixel-level tests of the simulated framebuf (semantics of MicroPython's modframebuf.c)."""
import os
import random
import sys
from array import array

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from mpsim import mp_framebuf as fb  # noqa: E402
from mpsim import font8x8  # noqa: E402

FORMATS = {
    "MONO_VLSB": (fb.MONO_VLSB, 1), "MONO_HLSB": (fb.MONO_HLSB, 1), "MONO_HMSB": (fb.MONO_HMSB, 1),
    "RGB565": (fb.RGB565, 0xFFFF), "GS8": (fb.GS8, 0xFF), "GS4_HMSB": (fb.GS4_HMSB, 0xF),
    "GS2_HMSB": (fb.GS2_HMSB, 0x3),
}


def make(fmt, w=16, h=12):
    bpp = {fb.MONO_VLSB: 1, fb.MONO_HLSB: 1, fb.MONO_HMSB: 1, fb.RGB565: 16, fb.GS8: 8,
           fb.GS4_HMSB: 4, fb.GS2_HMSB: 2}[fmt]
    if fmt == fb.MONO_VLSB:
        n = w * ((h + 7) // 8)
    else:
        n = ((w * bpp + 7) // 8) * h
    buf = bytearray(n)
    return buf, fb.FrameBuffer(buf, w, h, fmt)


def lit(f, w, h):
    return {(x, y) for y in range(h) for x in range(w) if f.pixel(x, y)}


# ------------------------------------------------------------------ byte layout
def test_mono_vlsb_layout():
    buf, f = make(fb.MONO_VLSB, 8, 16)
    f.pixel(3, 10, 1)            # page 1, bit 2
    assert buf[1 * 8 + 3] == 0b100
    assert f.pixel(3, 10) == 1 and f.pixel(3, 9) == 0


def test_mono_hlsb_and_hmsb_bit_order():
    buf, f = make(fb.MONO_HLSB, 16, 2)
    f.pixel(0, 0, 1)
    f.pixel(9, 1, 1)
    assert buf[0] == 0x80 and buf[3] == 0x40    # bit 7 is leftmost
    buf, f = make(fb.MONO_HMSB, 16, 2)
    f.pixel(0, 0, 1)
    f.pixel(9, 1, 1)
    assert buf[0] == 0x01 and buf[3] == 0x02    # bit 0 is leftmost


def test_rgb565_little_endian_like_esp32():
    buf, f = make(fb.RGB565, 4, 1)
    f.pixel(1, 0, 0xF800)
    assert buf[2:4] == b"\x00\xf8"
    assert f.pixel(1, 0) == 0xF800


def test_gs4_and_gs2_nibble_order():
    buf, f = make(fb.GS4_HMSB, 4, 1)
    f.pixel(0, 0, 0xA)
    f.pixel(1, 0, 0x5)
    assert buf[0] == 0xA5
    buf, f = make(fb.GS2_HMSB, 4, 1)
    f.pixel(0, 0, 1)
    f.pixel(3, 0, 2)
    assert buf[0] == 0b10000001                 # pixel 0 in the low bits


def test_constructor_validation():
    with pytest.raises(ValueError):
        fb.FrameBuffer(bytearray(10), 16, 8, fb.MONO_VLSB)   # needs 16 bytes
    with pytest.raises(ValueError):
        fb.FrameBuffer(bytearray(100), 4, 4, 99)
    with pytest.raises(ValueError):
        fb.FrameBuffer(bytearray(100), 4, 4, fb.GS8, 2)      # stride < width


# ------------------------------------------------------------------ primitives
@pytest.mark.parametrize("name", list(FORMATS))
def test_fill_rect_fast_path_matches_pixel_reference(name):
    fmt, cmax = FORMATS[name]
    rng = random.Random(name)
    w, h = 21, 19
    _, f = make(fmt, w, h)
    ref = np.zeros((h, w), np.int64)
    for _ in range(60):
        x, y = rng.randint(-5, w), rng.randint(-5, h)
        rw, rh = rng.randint(-2, 12), rng.randint(-2, 12)
        c = rng.randint(0, cmax)
        f.fill_rect(x, y, rw, rh, c)
        cc = (1 if c else 0) if cmax == 1 else c
        if rw > 0 and rh > 0:
            ref[max(0, y):max(0, min(h, y + rh)), max(0, x):max(0, min(w, x + rw))] = cc
    got = np.array([[f.pixel(x, y) for x in range(w)] for y in range(h)])
    assert (got == ref).all()


def test_hline_vline_rect_and_clipping():
    _, f = make(fb.MONO_VLSB, 10, 10)
    f.rect(-2, -2, 6, 6, 1)               # clipped outline: only right/bottom edges remain
    assert lit(f, 10, 10) == {(3, y) for y in range(4)} | {(x, 3) for x in range(4)}
    f.fill(0)
    f.hline(8, 5, 10, 1)
    f.vline(1, 8, 5, 1)
    assert lit(f, 10, 10) == {(8, 5), (9, 5), (1, 8), (1, 9)}


def test_line_matches_micropython_algorithm():
    _, f = make(fb.MONO_VLSB, 8, 8)
    f.line(0, 0, 4, 2, 1)
    assert lit(f, 8, 8) == {(0, 0), (1, 1), (2, 1), (3, 2), (4, 2)}
    f.fill(0)
    f.line(2, 6, 2, 1, 1)                 # vertical, drawn upwards, both ends included
    assert lit(f, 8, 8) == {(2, y) for y in range(1, 7)}


def test_ellipse_outline_fill_and_quadrants():
    _, f = make(fb.MONO_VLSB, 16, 16)
    f.ellipse(8, 8, 0, 0, 1)
    assert lit(f, 16, 16) == {(8, 8)}
    f.fill(0)
    f.ellipse(8, 8, 4, 4, 1)
    px = lit(f, 16, 16)
    assert {(12, 8), (4, 8), (8, 4), (8, 12)} <= px and (8, 8) not in px
    assert px == {(16 - x, y) for x, y in px}       # left-right symmetric
    f.fill(0)
    f.ellipse(8, 8, 4, 3, 1, True)
    px = lit(f, 16, 16)
    assert (8, 8) in px and (12, 8) in px and (13, 8) not in px
    f.fill(0)
    f.ellipse(8, 8, 4, 4, 1, True, 0b0001)          # Q1 only: top-right
    assert all(x >= 8 and y <= 8 for x, y in lit(f, 16, 16))


def test_poly_outline_and_fill():
    _, f = make(fb.MONO_VLSB, 16, 16)
    tri = array("h", [0, 0, 10, 0, 0, 10])
    f.poly(2, 2, tri, 1)
    px = lit(f, 16, 16)
    assert {(2, 2), (12, 2), (2, 12)} <= px and (4, 4) not in px
    f.fill(0)
    f.poly(2, 2, tri, 1, True)
    px = lit(f, 16, 16)
    assert (4, 4) in px and (3, 10) in px and (12, 12) not in px


def test_text_glyph_cells_and_clipping():
    _, f = make(fb.MONO_VLSB, 24, 8)
    f.text("A", 0, 0, 1)
    rows = font8x8.glyph(ord("A"))
    expect = {(x, y) for y in range(8) for x in range(8) if (rows[y] >> x) & 1}
    assert lit(f, 24, 8) == expect
    f.fill(0)
    f.text("A", -4, 0, 1)                            # partially off-screen
    assert lit(f, 24, 8) == {(x - 4, y) for x, y in expect if x >= 4}
    f.fill(0)
    f.text("é", 0, 0, 1)                         # 2 UTF-8 bytes -> 2 fallback glyph cells
    xs = {x for x, _ in lit(f, 24, 8)}
    assert min(xs) < 8 <= max(xs) < 16


def test_scroll_keeps_footprint():
    _, f = make(fb.GS8, 4, 1)
    for x, c in enumerate([1, 2, 3, 4]):
        f.pixel(x, 0, c)
    f.scroll(1, 0)
    assert [f.pixel(x, 0) for x in range(4)] == [1, 1, 2, 3]
    f.scroll(-2, 0)
    assert [f.pixel(x, 0) for x in range(4)] == [2, 3, 2, 3]


def test_blit_key_and_palette():
    sbuf, src = make(fb.MONO_HLSB, 8, 2)
    src.fill(0)
    src.pixel(1, 0, 1)
    dbuf, dst = make(fb.RGB565, 8, 2)
    dst.fill(0x1234)
    pbuf = bytearray(4)
    pal = fb.FrameBuffer(pbuf, 2, 1, fb.RGB565)
    pal.pixel(0, 0, 0x0000)
    pal.pixel(1, 0, 0xF800)
    dst.blit(src, 0, 0, 0x0000, pal)                  # key compares the palette colour
    assert dst.pixel(1, 0) == 0xF800 and dst.pixel(0, 0) == 0x1234
    dst.blit((sbuf, 8, 2, fb.MONO_HLSB), -1, 1)        # tuple source, clipped
    assert dst.pixel(0, 1) == 1 and dst.pixel(1, 1) == 0
