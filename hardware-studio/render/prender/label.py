"""Corner badge "渲染图 / Render" so renders are never mistaken for photographs."""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageDraw

from .fonts import find_cjk_font, find_latin_font

DEFAULT_LABEL = "渲染图 / Render"
FALLBACK_LABEL = "Render"


@dataclass
class LabelInfo:
    text: str
    box: tuple[int, int, int, int]  # x0, y0, x1, y1 in output pixels
    corner: str
    font: str | None
    cjk: bool


def draw_label(img: Image.Image, text: str = DEFAULT_LABEL, corner: str = "bottom-right") -> LabelInfo:
    W, H = img.size
    size = max(12, int(round(min(W, H) * 0.028)))
    needs_cjk = any(ord(ch) > 0x2E7F for ch in text)
    font_ref = find_cjk_font() if needs_cjk else (find_cjk_font() or find_latin_font())
    cjk = font_ref is not None and needs_cjk
    if needs_cjk and font_ref is None:
        # No CJK font on this machine: keep only the ASCII part, never draw tofu.
        text = "".join(ch for ch in text if ord(ch) < 0x2E80).strip(" /") or FALLBACK_LABEL
        font_ref = find_latin_font()
    font = font_ref.pil(size) if font_ref else None
    draw = ImageDraw.Draw(img, "RGBA")
    if font is not None:
        x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=font)
    else:  # pragma: no cover - PIL default bitmap font
        x0, y0, x1, y1 = draw.textbbox((0, 0), text)
    tw, th = x1 - x0, y1 - y0
    pad = int(size * 0.55)
    margin = int(size * 0.8)
    bw, bh = tw + 2 * pad, th + 2 * pad
    bx = W - margin - bw if "right" in corner else margin
    by = H - margin - bh if "bottom" in corner else margin
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(size * 0.4),
                           fill=(20, 22, 26, 170))
    draw.text((bx + pad - x0, by + pad - y0), text, font=font, fill=(255, 255, 255, 245))
    return LabelInfo(text, (bx, by, bx + bw, by + bh), corner,
                     font_ref.path if font_ref else None, cjk)
