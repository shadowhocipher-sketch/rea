"""Text measurement with the same font the PNG is drawn with.

The CJK font lookup is owned by ``render/prender/fonts.py``; this module reuses it.
"""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

_RENDER_DIR = Path(__file__).resolve().parents[2] / "render"
if str(_RENDER_DIR) not in sys.path:
    sys.path.insert(0, str(_RENDER_DIR))

from prender.fonts import FontRef, find_cjk_font, find_latin_font  # noqa: E402

SVG_FONT_FAMILY = ("'Noto Sans CJK SC','Source Han Sans SC','PingFang SC','Microsoft YaHei',"
                   "'WenQuanYi Micro Hei','DejaVu Sans',sans-serif")


class TextMeasurer:
    def __init__(self, font: FontRef | None = None, bold_font: FontRef | None = None):
        self.font = font or find_cjk_font() or find_latin_font()
        self.cjk = font is not None or find_cjk_font() is not None
        bold = None
        if self.font and "Regular" in self.font.path:
            cand = self.font.path.replace("Regular", "Bold")
            if Path(cand).exists():
                bold = FontRef(cand, self.font.index)
        self.bold = bold_font or bold or self.font
        self.family = SVG_FONT_FAMILY

    @lru_cache(maxsize=4096)
    def _pil(self, size: int, bold: bool):
        ref = self.bold if bold else self.font
        return ref.pil(size) if ref else None

    def pil_font(self, size: float, bold: bool = False):
        return self._pil(int(round(size)), bold)

    def width(self, text: str, size: float, bold: bool = False) -> float:
        if not text:
            return 0.0
        f = self.pil_font(size, bold)
        if f is None:  # pragma: no cover
            return len(text) * size * 0.62
        # +6% margin: browsers may pick a slightly wider fallback for the SVG
        return float(f.getlength(text)) * 1.06
