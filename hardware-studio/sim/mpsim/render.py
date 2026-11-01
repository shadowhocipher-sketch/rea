"""Turn captured frames into PNG / GIF images.

Every output carries a footer strip with the label "模拟 / Simulated" in the
corner (CONVENTIONS.md section 6) and, for GIF/sheet frames, the virtual time.

Styles:
* oled   - black panel, pixel grid gaps, optional glow, panel colour
           (white / blue / yellow / yellow-blue two-colour module), contrast.
* lcd    - plain upscaled RGB with a dark bezel.
* epaper - off-white paper texture, dark ink, red ink, light-grey ghosting.
"""

import os
import glob

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

LABEL = "模拟 / Simulated"
LABEL_ASCII = "SIMULATED"

OLED_COLORS = {
    "white": (225, 238, 255),
    "blue": (80, 170, 255),
    "yellow": (255, 214, 70),
}

_FONT_CACHE = {}


def find_cjk_font():
    """Path of a font that can draw Chinese, or None."""
    if "cjk" in _FONT_CACHE:
        return _FONT_CACHE["cjk"]
    patterns = [
        "/usr/share/fonts/**/NotoSansCJK*.tt[cf]", "/usr/share/fonts/**/NotoSansSC*.[ot]tf",
        "/usr/share/fonts/**/wqy*.tt[cf]", "/usr/share/fonts/**/SourceHanSans*.[ot]t[cf]",
        "/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti*.ttc",
        "/Library/Fonts/Arial Unicode.ttf", "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
    ]
    found = None
    for pat in patterns:
        hits = sorted(glob.glob(pat, recursive=True))
        hits = [h for h in hits if "Bold" not in os.path.basename(h)] or hits
        if hits:
            found = hits[0]
            break
    _FONT_CACHE["cjk"] = found
    return found


def _font(size):
    key = ("f", size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    path = find_cjk_font()
    font = None
    if path:
        try:
            font = ImageFont.truetype(path, size)
        except OSError:
            font = None
    if font is None:
        font = ImageFont.load_default(size=size)
    _FONT_CACHE[key] = font
    return font


def label_text():
    return LABEL if find_cjk_font() else LABEL_ASCII


# --------------------------------------------------------------------------- styling
def _upscale(arr, s):
    return np.repeat(np.repeat(arr, s, axis=0), s, axis=1)


def style_oled(rgb, meta, scale=4, color="white", glow=True):
    lit = rgb[:, :, 0] > 127
    h, w = lit.shape
    bright = 0.35 + 0.65 * (meta.get("contrast", 255) / 255.0)
    if color == "yellow-blue":  # common two-colour 0.96" module: top 16 rows yellow
        col = np.zeros((h, w, 3), np.float32)
        col[:, :] = OLED_COLORS["blue"]
        col[: min(16, h), :] = OLED_COLORS["yellow"]
    else:
        col = np.zeros((h, w, 3), np.float32)
        col[:, :] = OLED_COLORS.get(color, OLED_COLORS["white"])
    px = np.where(lit[:, :, None], col * bright, 0.0)
    big = _upscale(px, scale)
    if scale >= 3:  # pixel grid: darken last row/col of every pixel cell
        gap = np.ones((scale, scale, 1), np.float32)
        gap[-1, :, :] = 0.25
        gap[:, -1, :] = 0.25
        big = big * np.tile(gap, (h, w, 1))
    img = Image.fromarray(np.clip(big, 0, 255).astype(np.uint8))
    if glow and lit.any():
        blur = img.filter(ImageFilter.GaussianBlur(radius=scale * 1.3))
        arr = np.asarray(img, np.float32) + 0.8 * np.asarray(blur, np.float32)
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    bg = np.asarray(img, np.float32)
    panel = np.array([6, 8, 12], np.float32)
    img = Image.fromarray(np.clip(np.maximum(bg, panel), 0, 255).astype(np.uint8))
    return _bezel(img, scale * 4, (22, 24, 28))


def style_lcd(rgb, meta, scale=2):
    img = Image.fromarray(_upscale(rgb, scale))
    return _bezel(img, max(8, scale * 6), (18, 18, 20))


_PAPER = np.array([234, 232, 224], np.float32)
_INK = np.array([38, 38, 44], np.float32)
_RED_INK = np.array([176, 42, 36], np.float32)
_GHOST = np.array([206, 204, 196], np.float32)


def style_epaper(rgb, meta, scale=3, seed=1):
    h, w, _ = rgb.shape
    out = np.empty((h, w, 3), np.float32)
    out[:] = _PAPER
    black = (rgb[:, :, 0] < 60) & (rgb[:, :, 1] < 60)
    red = (rgb[:, :, 0] > 200) & (rgb[:, :, 1] < 60)
    ghost = (rgb[:, :, 0] > 150) & (rgb[:, :, 0] < 230) & (rgb[:, :, 1] > 150)
    out[ghost] = _GHOST
    out[black] = _INK
    out[red] = _RED_INK
    big = _upscale(out, scale)
    rng = np.random.default_rng(seed)
    # paper grain at 2x2-pixel blocks: looks like paper, compresses much better
    gh, gw = (big.shape[0] + 1) // 2, (big.shape[1] + 1) // 2
    noise = _upscale(rng.normal(0.0, 2.5, (gh, gw)), 2)[: big.shape[0], : big.shape[1], None]
    big = np.clip(big + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(big).filter(ImageFilter.GaussianBlur(radius=0.35 * scale / 3))
    return _bezel(img, max(10, scale * 6), (214, 212, 204))


def _bezel(img, m, color):
    out = Image.new("RGB", (img.width + 2 * m, img.height + 2 * m), color)
    out.paste(img, (m, m))
    return out


def style_frame(frame, opts=None):
    opts = opts or {}
    if frame.kind == "oled":
        return style_oled(frame.rgb, frame.meta, scale=opts.get("scale") or 4,
                          color=opts.get("oled_color", "white"), glow=opts.get("glow", True))
    if frame.kind == "epaper":
        return style_epaper(frame.rgb, frame.meta, scale=opts.get("scale") or 3)
    w = frame.rgb.shape[1]
    return style_lcd(frame.rgb, frame.meta, scale=opts.get("scale") or (2 if w <= 240 else 1))


def add_footer(img, caption=""):
    """Footer strip with optional caption (left) and the Simulated label (right corner)."""
    fs = max(12, min(22, img.width // 28))
    pad = fs // 2
    bar_h = fs + 2 * pad
    out = Image.new("RGB", (img.width, img.height + bar_h), (30, 30, 34))
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    font = _font(fs)
    lab = label_text()
    lw = d.textlength(lab, font=font)
    d.text((img.width - lw - pad, img.height + pad - 1), lab, fill=(255, 196, 64), font=font)
    if caption:
        d.text((pad, img.height + pad - 1), caption, fill=(220, 220, 220), font=font)
    return out


def _caption(frame, t0_us=0):
    t = (frame.t_us - t0_us) / 1_000_000
    extra = ""
    if frame.kind == "epaper" and frame.meta.get("refresh"):
        extra = "  %s refresh %d ms" % (frame.meta["refresh"], frame.meta.get("duration_ms", 0))
    return "t=%.2f s%s" % (t, extra)


# --------------------------------------------------------------------------- outputs
def save_png(frames, path, opts=None, mode="sheet", max_tiles=12, cols=None):
    """Single frame (mode='last' / 'first') or a contact sheet (mode='sheet')."""
    if not frames:
        raise ValueError("no frames to render")
    if mode in ("last", "first") or len(frames) == 1:
        fr = frames[-1] if mode != "first" else frames[0]
        img = add_footer(style_frame(fr, opts), _caption(fr))
        img.save(path)
        return path
    n = min(max_tiles, len(frames))
    idx = sorted(set(int(round(i * (len(frames) - 1) / max(1, n - 1))) for i in range(n)))
    tiles = [add_footer(style_frame(frames[i], opts), _caption(frames[i])) for i in idx]
    cols = cols or min(4 if tiles[0].width < 700 else 2, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    tw, th = tiles[0].width, tiles[0].height
    gap = 8
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * gap, rows * th + (rows + 1) * gap), (48, 48, 52))
    for k, t in enumerate(tiles):
        r, c = divmod(k, cols)
        sheet.paste(t, (gap + c * (tw + gap), gap + r * (th + gap)))
    sheet = add_footer(sheet, "%d frames, %d shown" % (len(frames), len(tiles)))
    sheet.save(path)
    return path


def gif_timeline(frames, end_us, speed=1.0, min_ms=20, epaper_flash=True, last_ms=None):
    """[(frame_or_effect, duration_ms)] honouring virtual time between frames."""
    items = []
    for i, fr in enumerate(frames):
        nxt = frames[i + 1].t_us if i + 1 < len(frames) else None
        if nxt is None:
            d = last_ms if last_ms is not None else min(2000, max(400, (end_us - fr.t_us) / 1000))
        else:
            d = (nxt - fr.t_us) / 1000.0
        d = d / speed
        if fr.kind == "epaper" and epaper_flash and fr.meta.get("refresh") == "full" and d >= 3 * min_ms:
            fd = min(d / 3, fr.meta.get("duration_ms", 1000) / speed / 3)
            items.append((("flash", "black", fr), fd))
            items.append((("flash", "white", fr), fd))
            d -= 2 * fd
        items.append((("frame", None, fr), d))
    # merge too-short items into the previous one, and identical consecutive frames
    out = []
    for item, d in items:
        if out and item[0] == "frame" and out[-1][0][0] == "frame" and \
                np.array_equal(out[-1][0][2].rgb, item[2].rgb) and \
                out[-1][0][2].meta.get("refresh") == item[2].meta.get("refresh"):
            out[-1] = (out[-1][0], out[-1][1] + d)
            continue
        if out and d < min_ms:
            out[-1] = (out[-1][0], out[-1][1] + d)
            continue
        out.append((item, d))
    return out


def _flash_image(kind, frame, opts):
    from .runtime import Frame
    h, w, _ = frame.rgb.shape
    val = 0 if kind == "black" else 255
    rgb = np.full((h, w, 3), val, np.uint8)
    return style_frame(Frame(frame.t_us, frame.display_id, frame.kind, rgb, {}), opts)


def save_gif(frames, path, end_us, opts=None, speed=1.0, max_gif_frames=1500):
    if not frames:
        raise ValueError("no frames to render")
    opts = opts or {}
    timeline = gif_timeline(frames, end_us, speed=speed, epaper_flash=opts.get("epaper_flash", True))
    if len(timeline) > max_gif_frames:
        # keep it bounded: drop every k-th frame by merging durations
        k = (len(timeline) + max_gif_frames - 1) // max_gif_frames
        merged = []
        for i in range(0, len(timeline), k):
            chunk = timeline[i:i + k]
            merged.append((chunk[-1][0], sum(d for _, d in chunk)))
        timeline = merged
    images, durations = [], []
    cache = {}
    for (typ, sub, fr), d in timeline:
        if typ == "flash":
            img = _flash_image(sub, fr, opts)
            cap = _caption(fr) + "  (refresh flash, illustrative)"
        else:
            key = id(fr)
            img = cache.get(key) or style_frame(fr, opts)
            cache[key] = img
            cap = _caption(fr)
        images.append(add_footer(img, cap))
        durations.append(max(20, int(round(d / 10.0)) * 10))
    # one global palette from a sample of frames -> stable colours, small file
    sample_idx = sorted(set(np.linspace(0, len(images) - 1, min(12, len(images))).astype(int)))
    w, h = images[0].size
    mosaic = Image.new("RGB", (w, h * len(sample_idx)))
    for k, i in enumerate(sample_idx):
        mosaic.paste(images[i], (0, k * h))
    pal = mosaic.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    pframes = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in images]
    pframes[0].save(path, save_all=True, append_images=pframes[1:], duration=durations,
                    loop=0, optimize=False, disposal=1)
    return path
