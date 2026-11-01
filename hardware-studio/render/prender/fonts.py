"""Locate a font that can draw Chinese labels ("渲染图", net notes, ...).

No font file is bundled with the library. The lookup order is:

1. the ``HS_CJK_FONT`` environment variable (``/path/font.ttc`` or ``/path/font.ttc#2``);
2. ``fc-list :lang=zh`` (fontconfig, Linux/macOS with fontconfig);
3. a few well-known system locations (Noto Sans CJK, Source Han Sans, WenQuanYi,
   PingFang, Microsoft YaHei).

Install on Debian/Ubuntu: ``sudo apt-get install fonts-noto-cjk`` (SIL OFL 1.1).
If nothing is found, callers fall back to English-only labels and say so.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from functools import lru_cache

_PROBE = "渲染图接线"

_KNOWN = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/source-han-sans/SourceHanSans-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]


@dataclass(frozen=True)
class FontRef:
    path: str
    index: int = 0

    def pil(self, size: int):
        from PIL import ImageFont

        return ImageFont.truetype(self.path, size=size, index=self.index)


def _covers(path: str, index: int) -> bool:
    try:
        from PIL import ImageFont

        font = ImageFont.truetype(path, size=24, index=index)
    except OSError:
        return False
    # A font without the glyphs renders tofu boxes that all share one bitmap.
    masks = [font.getmask(ch).getbbox() for ch in _PROBE]
    return all(m is not None for m in masks)


def _best_index(path: str) -> int | None:
    """Pick the Simplified Chinese face inside a .ttc when there is one."""
    from PIL import ImageFont

    candidates: list[tuple[int, int]] = []
    for index in range(12):
        try:
            font = ImageFont.truetype(path, size=12, index=index)
        except OSError:
            break
        family = " ".join(font.getname())
        score = 0 if (" SC" in family or "GB" in family or "Hei" in family) else 1
        candidates.append((score, index))
    for _, index in sorted(candidates):
        if _covers(path, index):
            return index
    return None


def _fc_list() -> list[str]:
    if not shutil.which("fc-list"):
        return []
    try:
        out = subprocess.run(
            ["fc-list", ":lang=zh", "file"], capture_output=True, text=True, timeout=10
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    files = [line.split(":")[0].strip() for line in out.splitlines() if line.strip()]
    # Prefer sans faces.
    return sorted(set(files), key=lambda p: (("Sans" not in p and "Hei" not in p), "Bold" in p, p))


@lru_cache(maxsize=1)
def find_cjk_font() -> FontRef | None:
    env = os.environ.get("HS_CJK_FONT")
    if env:
        path, _, idx = env.partition("#")
        if os.path.exists(path):
            return FontRef(path, int(idx) if idx else (_best_index(path) or 0))
    for path in _KNOWN + _fc_list():
        if not os.path.exists(path):
            continue
        index = _best_index(path)
        if index is not None:
            return FontRef(path, index)
    return None


def find_latin_font() -> FontRef | None:
    """DejaVu Sans ships with matplotlib, so this practically always succeeds."""
    try:
        import matplotlib

        path = os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans.ttf")
        if os.path.exists(path):
            return FontRef(path, 0)
    except ImportError:
        pass
    return None
