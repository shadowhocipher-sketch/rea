"""Simulated MicroPython ``framebuf`` module, written from the public API docs.

API and pixel semantics follow https://docs.micropython.org/en/latest/library/framebuf.html.
Where the docs are silent (clipping, line/ellipse/polygon rasterisation, pixel
packing of each format, scroll footprint, blit palette/key order) this
implementation reproduces the behaviour of MicroPython's extmod/modframebuf.c
(MIT licence) so that drawing is pixel-identical, with one known exception:

* ``text()`` uses the public-domain font8x8 glyphs (see font8x8.py) instead of
  MicroPython's font_petme128_8x8, so glyph shapes differ; cell size (8x8),
  origin, clipping and the "bytes outside 32..127 -> glyph 127" rule match.

Buffers keep the exact byte layout of a little-endian MCU (ESP32): RGB565 is
stored as native little-endian uint16, exactly like ``fbuf.pixel(x, y, c)`` on
the board, so a firmware that sends the raw buffer to a display sees the same
bytes as on hardware.

Like the real module, FrameBuffer objects do NOT expose ``width``/``height``
attributes (drivers such as ssd1306 set their own).
"""

import numpy as np

from . import font8x8
from .runtime import current

MONO_VLSB = 0
MVLSB = 0
RGB565 = 1
GS4_HMSB = 2
MONO_HLSB = 3
MONO_HMSB = 4
GS2_HMSB = 5
GS8 = 6

_FORMATS = (MONO_VLSB, RGB565, GS4_HMSB, MONO_HLSB, MONO_HMSB, GS2_HMSB, GS8)


def _cdiv(a, b):
    """C integer division (truncates toward zero)."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


def _as_bytes_view(buf):
    mv = memoryview(buf)
    if mv.format != "B" or mv.ndim != 1:
        mv = mv.cast("B")
    return mv


class FrameBuffer:
    def __init__(self, buffer, width, height, format, stride=None):
        width = int(width)
        height = int(height)
        format = int(format)
        stride = width if stride is None else int(stride)
        if width < 1 or height < 1 or width > 0xFFFF or height > 0xFFFF or stride > 0xFFFF or stride < width:
            raise ValueError()
        bpp = 1
        height_required = height
        width_required = width
        strides_required = height - 1
        if format == MONO_VLSB:
            height_required = (height + 7) & ~7
            strides_required = height_required - 8
        elif format in (MONO_HLSB, MONO_HMSB):
            stride = (stride + 7) & ~7
            width_required = (width + 7) & ~7
        elif format == GS2_HMSB:
            stride = (stride + 3) & ~3
            width_required = (width + 3) & ~3
            bpp = 2
        elif format == GS4_HMSB:
            stride = (stride + 1) & ~1
            width_required = (width + 1) & ~1
            bpp = 4
        elif format == GS8:
            bpp = 8
        elif format == RGB565:
            bpp = 16
        else:
            raise ValueError("invalid format")
        mv = _as_bytes_view(buffer)
        need = (strides_required * stride + (height_required - strides_required) * width_required) * bpp // 8
        if need > len(mv):
            raise ValueError()
        self._fb_buf = buffer
        self._fb_mv = mv
        self._fb_arr = np.frombuffer(mv, dtype=np.uint8)
        self._fb_w = width
        self._fb_h = height
        self._fb_fmt = format
        self._fb_stride = stride

    # ------------------------------------------------------------ pixel access
    def _setpixel(self, x, y, c):
        f = self._fb_fmt
        mv = self._fb_mv
        if f == MONO_VLSB:
            i = (y >> 3) * self._fb_stride + x
            o = y & 7
            mv[i] = (mv[i] & (0xFF ^ (1 << o))) | ((c != 0) << o)
        elif f == MONO_HLSB or f == MONO_HMSB:
            i = (x + y * self._fb_stride) >> 3
            o = (x & 7) if f == MONO_HMSB else 7 - (x & 7)
            mv[i] = (mv[i] & (0xFF ^ (1 << o))) | ((c != 0) << o)
        elif f == RGB565:
            i = (x + y * self._fb_stride) * 2
            c &= 0xFFFF
            mv[i] = c & 0xFF
            mv[i + 1] = c >> 8
        elif f == GS8:
            mv[x + y * self._fb_stride] = c & 0xFF
        elif f == GS4_HMSB:
            i = (x + y * self._fb_stride) >> 1
            if x % 2:
                mv[i] = (c & 0x0F) | (mv[i] & 0xF0)
            else:
                mv[i] = ((c << 4) & 0xFF) | (mv[i] & 0x0F)
        elif f == GS2_HMSB:
            i = (x + y * self._fb_stride) >> 2
            sh = (x & 3) << 1
            mv[i] = ((c & 3) << sh) | (mv[i] & (0xFF ^ (3 << sh)))

    def _getpixel(self, x, y):
        f = self._fb_fmt
        mv = self._fb_mv
        if f == MONO_VLSB:
            return (mv[(y >> 3) * self._fb_stride + x] >> (y & 7)) & 1
        if f == MONO_HLSB or f == MONO_HMSB:
            o = (x & 7) if f == MONO_HMSB else 7 - (x & 7)
            return (mv[(x + y * self._fb_stride) >> 3] >> o) & 1
        if f == RGB565:
            i = (x + y * self._fb_stride) * 2
            return mv[i] | (mv[i + 1] << 8)
        if f == GS8:
            return mv[x + y * self._fb_stride]
        if f == GS4_HMSB:
            b = mv[(x + y * self._fb_stride) >> 1]
            return b & 0x0F if x % 2 else b >> 4
        if f == GS2_HMSB:
            return (mv[(x + y * self._fb_stride) >> 2] >> ((x & 3) << 1)) & 3
        return 0

    def _fill_rect_clipped(self, x, y, w, h, c):
        f = self._fb_fmt
        arr = self._fb_arr
        st = self._fb_stride
        if f == MONO_VLSB:
            yy = y
            yend = y + h
            while yy < yend:
                page = yy >> 3
                last = min(yend, (page + 1) * 8)
                mask = 0
                for b in range(yy & 7, ((last - 1) & 7) + 1):
                    mask |= 1 << b
                seg = arr[page * st + x: page * st + x + w]
                if c:
                    np.bitwise_or(seg, mask, out=seg)
                else:
                    np.bitwise_and(seg, 0xFF ^ mask, out=seg)
                yy = last
        elif f == MONO_HLSB or f == MONO_HMSB:
            adv = st >> 3
            for xx in range(x, x + w):
                o = (xx & 7) if f == MONO_HMSB else 7 - (xx & 7)
                start = (xx >> 3) + y * adv
                seg = arr[start: start + h * adv: adv]
                if c:
                    np.bitwise_or(seg, 1 << o, out=seg)
                else:
                    np.bitwise_and(seg, 0xFF ^ (1 << o), out=seg)
        elif f == RGB565 or f == GS8:
            bpp = 2 if f == RGB565 else 1
            nfull = (len(arr) // (st * bpp))
            view = arr[: nfull * st * bpp]
            if f == RGB565:
                view = view.view("<u2")
                cv = c & 0xFFFF
            else:
                cv = c & 0xFF
            view = view.reshape(nfull, st)
            if y + h <= nfull:
                view[y:y + h, x:x + w] = cv
            else:  # last row is shorter than stride
                for yy in range(y, y + h):
                    for xx in range(x, x + w):
                        self._setpixel(xx, yy, c)
        else:
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    self._setpixel(xx, yy, c)

    def _fill_rect(self, x, y, w, h, c):
        if h < 1 or w < 1 or x + w <= 0 or y + h <= 0 or y >= self._fb_h or x >= self._fb_w:
            return
        xend = min(self._fb_w, x + w)
        yend = min(self._fb_h, y + h)
        x = max(x, 0)
        y = max(y, 0)
        self._fill_rect_clipped(x, y, xend - x, yend - y, c)

    def _setpixel_checked(self, x, y, c, mask=1):
        if mask and 0 <= x < self._fb_w and 0 <= y < self._fb_h:
            self._setpixel(x, y, c)

    # ------------------------------------------------------------ whole-buffer codec
    def _full_shape(self):
        if self._fb_fmt == MONO_VLSB:
            return ((self._fb_h + 7) & ~7, self._fb_stride)
        return (self._fb_h, self._fb_stride)

    def _decode_full(self):
        """All pixels (including stride padding) as a 2-D int array."""
        f = self._fb_fmt
        st = self._fb_stride
        arr = self._fb_arr
        H, _ = self._full_shape()
        if f == MONO_VLSB:
            pages = H // 8
            raw = np.zeros(pages * st, np.uint8)
            n = min(len(arr), pages * st)
            raw[:n] = arr[:n]
            raw = raw.reshape(pages, st)
            bits = (raw[:, None, :] >> np.arange(8, dtype=np.uint8)[None, :, None]) & 1
            return bits.reshape(H, st).astype(np.int64)
        if f in (MONO_HLSB, MONO_HMSB):
            nb = H * st // 8
            raw = np.zeros(nb, np.uint8)
            n = min(len(arr), nb)
            raw[:n] = arr[:n]
            bits = np.unpackbits(raw.reshape(H, st // 8), axis=1,
                                 bitorder="big" if f == MONO_HLSB else "little")
            return bits.astype(np.int64)
        if f == RGB565:
            raw = np.zeros(H * st * 2, np.uint8)
            n = min(len(arr), len(raw))
            raw[:n] = arr[:n]
            return raw.view("<u2").reshape(H, st).astype(np.int64)
        if f == GS8:
            raw = np.zeros(H * st, np.uint8)
            n = min(len(arr), len(raw))
            raw[:n] = arr[:n]
            return raw.reshape(H, st).astype(np.int64)
        if f == GS4_HMSB:
            raw = np.zeros(H * st // 2, np.uint8)
            n = min(len(arr), len(raw))
            raw[:n] = arr[:n]
            raw = raw.reshape(H, st // 2)
            out = np.empty((H, st), np.int64)
            out[:, 0::2] = raw >> 4
            out[:, 1::2] = raw & 0x0F
            return out
        # GS2_HMSB
        raw = np.zeros(H * st // 4, np.uint8)
        n = min(len(arr), len(raw))
        raw[:n] = arr[:n]
        raw = raw.reshape(H, st // 4)
        out = np.empty((H, st), np.int64)
        for k in range(4):
            out[:, k::4] = (raw >> (2 * k)) & 3
        return out

    def _encode_full(self, pix):
        f = self._fb_fmt
        st = self._fb_stride
        H, _ = self._full_shape()
        if f == MONO_VLSB:
            bits = (pix != 0).astype(np.uint8).reshape(H // 8, 8, st)
            raw = np.zeros((H // 8, st), np.uint8)
            for k in range(8):
                raw |= bits[:, k, :] << k
            raw = raw.ravel()
        elif f in (MONO_HLSB, MONO_HMSB):
            raw = np.packbits((pix != 0).astype(np.uint8), axis=1,
                              bitorder="big" if f == MONO_HLSB else "little").ravel()
        elif f == RGB565:
            raw = (pix & 0xFFFF).astype("<u2").ravel().view(np.uint8)
        elif f == GS8:
            raw = (pix & 0xFF).astype(np.uint8).ravel()
        elif f == GS4_HMSB:
            p = (pix & 0x0F).astype(np.uint8)
            raw = ((p[:, 0::2] << 4) | p[:, 1::2]).ravel()
        else:
            p = (pix & 3).astype(np.uint8)
            raw = (p[:, 0::4] | (p[:, 1::4] << 2) | (p[:, 2::4] << 4) | (p[:, 3::4] << 6)).ravel()
        n = min(len(self._fb_arr), len(raw))
        self._fb_arr[:n] = raw[:n]

    def _sim_pixels(self):
        """Sim helper: logical pixels (H, W) as raw colour values (numpy int64)."""
        return self._decode_full()[: self._fb_h, : self._fb_w]

    # ------------------------------------------------------------ public API
    def fill(self, c):
        self._fill_rect_clipped(0, 0, self._fb_w, self._fb_h, int(c))

    def fill_rect(self, x, y, w, h, c):
        self._fill_rect(int(x), int(y), int(w), int(h), int(c))

    def pixel(self, x, y, c=None):
        x = int(x)
        y = int(y)
        if 0 <= x < self._fb_w and 0 <= y < self._fb_h:
            if c is None:
                return self._getpixel(x, y)
            self._setpixel(x, y, int(c))
        return None

    def hline(self, x, y, w, c):
        self._fill_rect(int(x), int(y), int(w), 1, int(c))

    def vline(self, x, y, h, c):
        self._fill_rect(int(x), int(y), 1, int(h), int(c))

    def rect(self, x, y, w, h, c, f=False):
        x, y, w, h, c = int(x), int(y), int(w), int(h), int(c)
        if f:
            self._fill_rect(x, y, w, h, c)
        else:
            self._fill_rect(x, y, w, 1, c)
            self._fill_rect(x, y + h - 1, w, 1, c)
            self._fill_rect(x, y, 1, h, c)
            self._fill_rect(x + w - 1, y, 1, h, c)

    def _line(self, x1, y1, x2, y2, col):
        dx = x2 - x1
        if dx > 0:
            sx = 1
        else:
            dx = -dx
            sx = -1
        dy = y2 - y1
        if dy > 0:
            sy = 1
        else:
            dy = -dy
            sy = -1
        steep = dy > dx
        if steep:
            x1, y1 = y1, x1
            dx, dy = dy, dx
            sx, sy = sy, sx
        e = 2 * dy - dx
        W, H = self._fb_w, self._fb_h
        for _ in range(dx):
            if steep:
                if 0 <= y1 < W and 0 <= x1 < H:
                    self._setpixel(y1, x1, col)
            else:
                if 0 <= x1 < W and 0 <= y1 < H:
                    self._setpixel(x1, y1, col)
            while e >= 0:
                y1 += sy
                e -= 2 * dx
            x1 += sx
            e += 2 * dy
        self._setpixel_checked(x2, y2, col)

    def line(self, x1, y1, x2, y2, c):
        self._line(int(x1), int(y1), int(x2), int(y2), int(c))

    def _ellipse_points(self, cx, cy, x, y, col, mask):
        if mask & 0x10:
            if mask & 1:
                self._fill_rect(cx, cy - y, x + 1, 1, col)
            if mask & 2:
                self._fill_rect(cx - x, cy - y, x + 1, 1, col)
            if mask & 4:
                self._fill_rect(cx - x, cy + y, x + 1, 1, col)
            if mask & 8:
                self._fill_rect(cx, cy + y, x + 1, 1, col)
        else:
            self._setpixel_checked(cx + x, cy - y, col, mask & 1)
            self._setpixel_checked(cx - x, cy - y, col, mask & 2)
            self._setpixel_checked(cx - x, cy + y, col, mask & 4)
            self._setpixel_checked(cx + x, cy + y, col, mask & 8)

    def ellipse(self, x, y, xr, yr, c, f=False, m=None):
        cx, cy, a, b, col = int(x), int(y), int(xr), int(yr), int(c)
        mask = 0x10 if f else 0
        mask |= (int(m) & 0x0F) if m is not None else 0x0F
        if a == 0 and b == 0:
            self._setpixel_checked(cx, cy, col, mask & 0x0F)
            return
        two_a2 = 2 * a * a
        two_b2 = 2 * b * b
        px = a
        py = 0
        xchange = b * b * (1 - 2 * a)
        ychange = a * a
        err = 0
        stopx = two_b2 * a
        stopy = 0
        while stopx >= stopy:
            self._ellipse_points(cx, cy, px, py, col, mask)
            py += 1
            stopy += two_a2
            err += ychange
            ychange += two_a2
            if 2 * err + xchange > 0:
                px -= 1
                stopx -= two_b2
                err += xchange
                xchange += two_b2
        px = 0
        py = b
        xchange = b * b
        ychange = a * a * (1 - 2 * b)
        err = 0
        stopx = 0
        stopy = two_a2 * b
        while stopx <= stopy:
            self._ellipse_points(cx, cy, px, py, col, mask)
            px += 1
            stopx += two_b2
            err += xchange
            xchange += two_b2
            if 2 * err + ychange > 0:
                py -= 1
                stopy -= two_a2
                err += ychange
                ychange += two_a2

    def poly(self, x, y, coords, c, f=False):
        x, y, col = int(x), int(y), int(c)
        vals = [int(v) for v in coords]
        n = len(vals) // 2
        if n == 0:
            return
        if f:
            ys = vals[1::2][:n]
            y_min, y_max = min(ys), max(ys)
            for row in range(y_min, y_max + 1):
                nodes = []
                px1, py1 = vals[0], vals[1]
                i = n * 2 - 1
                while True:
                    py2 = vals[i]
                    i -= 1
                    px2 = vals[i]
                    i -= 1
                    if py1 != py2 and ((py1 > row >= py2) or (py1 <= row < py2)):
                        node = _cdiv(32 * px1 + _cdiv(32 * (px2 - px1) * (row - py1), (py2 - py1)) + 16, 32)
                        nodes.append(node)
                    elif row == max(py1, py2):
                        if py1 < py2:
                            self._setpixel_checked(x + px2, y + py2, col)
                        elif py2 < py1:
                            self._setpixel_checked(x + px1, y + py1, col)
                        else:
                            self._line(x + px1, y + py1, x + px2, y + py2, col)
                    px1, py1 = px2, py2
                    if i < 0:
                        break
                if not nodes:
                    continue
                nodes.sort()
                for k in range(0, len(nodes) - 1, 2):
                    self._fill_rect(x + nodes[k], y + row, nodes[k + 1] - nodes[k] + 1, 1, col)
        else:
            px1, py1 = vals[0], vals[1]
            i = n * 2 - 1
            while True:
                py2 = vals[i]
                i -= 1
                px2 = vals[i]
                i -= 1
                self._line(x + px1, y + py1, x + px2, y + py2, col)
                px1, py1 = px2, py2
                if i < 0:
                    break

    def text(self, s, x, y, c=1):
        x0, y0, col = int(x), int(y), int(c)
        W, H = self._fb_w, self._fb_h
        for ch in str(s).encode("utf-8"):
            rows = font8x8.glyph(ch)
            for i in range(8):
                xx = x0 + i
                if 0 <= xx < W:
                    for j in range(8):
                        if (rows[j] >> i) & 1:
                            yy = y0 + j
                            if 0 <= yy < H:
                                self._setpixel(xx, yy, col)
            x0 += 8

    def scroll(self, xstep, ystep):
        xstep, ystep = int(xstep), int(ystep)
        W, H = self._fb_w, self._fb_h
        if xstep >= W or -xstep >= W or ystep >= H or -ystep >= H:
            return
        full = self._decode_full()
        old = full[:H, :W].copy()
        new = full[:H, :W]
        xs = slice(xstep, W) if xstep >= 0 else slice(0, W + xstep)
        xsrc = slice(0, W - xstep) if xstep >= 0 else slice(-xstep, W)
        ys = slice(ystep, H) if ystep >= 0 else slice(0, H + ystep)
        ysrc = slice(0, H - ystep) if ystep >= 0 else slice(-ystep, H)
        new[ys, xs] = old[ysrc, xsrc]
        self._encode_full(full)

    def blit(self, fbuf, x, y, key=-1, palette=None):
        src = fbuf if isinstance(fbuf, FrameBuffer) else FrameBuffer(*fbuf)
        x, y, key = int(x), int(y), int(key)
        pal = None
        if palette is not None:
            pal = palette if isinstance(palette, FrameBuffer) else FrameBuffer(*palette)
        W, H = self._fb_w, self._fb_h
        if x >= W or y >= H or -x >= src._fb_w or -y >= src._fb_h:
            return
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = max(0, -x), max(0, -y)
        x0end = min(W, x + src._fb_w)
        y0end = min(H, y + src._fb_h)
        sp = src._sim_pixels()[y1:y1 + (y0end - y0), x1:x1 + (x0end - x0)]
        if pal is not None:
            prow = pal._decode_full()[0]
            sp = prow[np.clip(sp, 0, len(prow) - 1)]
            # out-of-range palette index reads beyond the palette row (undefined
            # on hardware); we clamp instead.
        full = self._decode_full()
        region = full[y0:y0end, x0:x0end]
        mask = sp != (key & 0xFFFFFFFF)  # C compares against (uint32_t)key; -1 = no key
        region[mask] = sp[mask]
        self._encode_full(full)


def FrameBuffer1(buffer, width, height, stride=None):
    """Legacy constructor: MONO_VLSB FrameBuffer."""
    return FrameBuffer(buffer, width, height, MONO_VLSB, stride)


def __getattr__(name):
    raise current().unsupported_api("framebuf", name)
