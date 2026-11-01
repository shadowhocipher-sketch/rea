"""Write a ``Layout`` as SVG (with machine-checkable data-* attributes) and as PNG.

Both outputs are drawn from the same Layout object, so they show the same wires.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw

from .layout import LABEL_FONT, PIN_FONT, ROW_H, TITLE_FONT, Layout

INK = "#1D2430"
BOX_FILL = "#F7F5F0"
HUB_FILL = "#EEF2F7"
BOX_STROKE = "#3A4250"
MUTED = "#5C6370"


def _a(v: str) -> str:
    return escape(str(v), {'"': "&quot;"})


def _f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def to_svg(lay: Layout) -> str:
    out: list[str] = []
    W, H = lay.width, lay.height
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{_f(W)}" height="{_f(H)}" '
               f'viewBox="0 0 {_f(W)} {_f(H)}" data-generator="hardware-studio/diagrams wiring" '
               f'font-family="{_a(lay.font_family)}">')
    out.append(f'<rect x="0" y="0" width="{_f(W)}" height="{_f(H)}" fill="#FFFFFF"/>')
    out.append(f'<text x="36" y="44" font-size="16" font-weight="bold" fill="{INK}">{escape(lay.title)}</text>')
    if lay.subtitle:
        out.append(f'<text x="36" y="66" font-size="{LABEL_FONT}" fill="{MUTED}">{escape(lay.subtitle)}</text>')

    out.append('<g id="wires" fill="none" stroke-linejoin="round" stroke-linecap="round">')
    for wg in lay.wires:
        w = wg.wire
        pts = " ".join(f"{_f(x)},{_f(y)}" for x, y in wg.points)
        out.append(
            f'<polyline class="wire" data-row="{w.row}" data-from="{_a(w.from_part)}.{_a(w.from_pin)}" '
            f'data-to="{_a(w.to_part)}.{_a(w.to_pin)}" data-from-part="{_a(w.from_part)}" '
            f'data-from-pin="{_a(w.from_pin)}" data-to-part="{_a(w.to_part)}" data-to-pin="{_a(w.to_pin)}" '
            f'data-net="{_a(w.net)}" data-kind="{_a(w.kind)}" stroke="{wg.color}" '
            f'stroke-width="{_f(wg.width)}" points="{pts}"><title>{escape(f"#{w.row} {w.net}: {w.from_part}.{w.from_pin} → {w.to_part}.{w.to_pin} {w.note}".strip())}</title></polyline>')
    out.append("</g>")

    out.append('<g id="parts">')
    for b in lay.boxes:
        fill = HUB_FILL if b.role == "hub" else BOX_FILL
        out.append(f'<g class="part" data-part="{_a(b.part)}">')
        out.append(f'<rect x="{_f(b.x)}" y="{_f(b.y)}" width="{_f(b.w)}" height="{_f(b.h)}" rx="6" '
                   f'fill="{fill}" stroke="{BOX_STROKE}" stroke-width="1.4"/>')
        out.append(f'<text x="{_f(b.x + b.w / 2)}" y="{_f(b.y + 19)}" font-size="{TITLE_FONT}" '
                   f'font-weight="bold" text-anchor="middle" fill="{INK}">{escape(b.part)}</text>')
        for p in b.pins:
            tx = p.x - 9 if p.side == "R" else p.x + 9
            anchor = "end" if p.side == "R" else "start"
            color = lay.net_colors[p.net]
            out.append(f'<g class="pin" data-part="{_a(p.part)}" data-pin="{_a(p.pin)}" data-side="{p.side}" '
                       f'data-net="{_a(p.net)}">'
                       f'<circle cx="{_f(p.x)}" cy="{_f(p.y)}" r="3.6" fill="{color}" stroke="#FFFFFF" stroke-width="1"/>'
                       f'<text x="{_f(tx)}" y="{_f(p.y + 4)}" font-size="{PIN_FONT}" text-anchor="{anchor}" '
                       f'fill="{INK}">{escape(p.pin)}</text></g>')
        out.append("</g>")
    out.append("</g>")

    out.append('<g id="net-labels">')
    for la in lay.labels:
        out.append(f'<text class="net-label" data-net="{_a(la.net)}" x="{_f(la.x)}" y="{_f(la.y)}" '
                   f'font-size="{LABEL_FONT}" fill="{la.color}">{escape(la.text)}</text>')
    out.append("</g>")

    ly = lay.legend_y
    out.append(f'<g id="legend" font-size="{LABEL_FONT}">')
    out.append(f'<text x="36" y="{_f(ly + 4)}" fill="{INK}">图例 Legend:</text>')
    x = 36 + lay.measurer.width("图例 Legend:", LABEL_FONT) + 12
    for text, color in (("电源 Power", "#D62728"), ("地 Ground", "#111111"),
                        ("信号 Signal（按网络着色 coloured per net）", "#1F77B4")):
        out.append(f'<line x1="{_f(x)}" y1="{_f(ly)}" x2="{_f(x + 22)}" y2="{_f(ly)}" stroke="{color}" stroke-width="2.6"/>')
        out.append(f'<text x="{_f(x + 28)}" y="{_f(ly + 4)}" fill="{INK}">{escape(text)}</text>')
        x += 28 + lay.measurer.width(text, LABEL_FONT) + 18
    out.append("</g>")

    out.append(f'<g id="wire-table" font-size="{LABEL_FONT}">')
    top = lay.table_top
    right = lay.table_cols[-1] + 260
    for c, head in zip(lay.table_cols, lay.table_header):
        out.append(f'<text x="{_f(c + (22 if c == lay.table_cols[0] else 0))}" y="{_f(top + 14)}" '
                   f'font-weight="bold" fill="{INK}">{escape(head)}</text>')
    out.append(f'<line x1="{_f(lay.table_cols[0])}" y1="{_f(top + ROW_H - 2)}" x2="{_f(right)}" '
               f'y2="{_f(top + ROW_H - 2)}" stroke="#C8CCD2"/>')
    for r in lay.table_rows:
        y = r.y
        c0 = lay.table_cols[0]
        out.append(f'<g class="wire-row" data-row="{_a(r.cells[0])}">'
                   f'<line x1="{_f(c0)}" y1="{_f(y + 10)}" x2="{_f(c0 + 16)}" y2="{_f(y + 10)}" '
                   f'stroke="{r.color}" stroke-width="3"/>')
        for i, (c, cell) in enumerate(zip(lay.table_cols, r.cells)):
            cx = c + (22 if i == 0 else 0)
            out.append(f'<text x="{_f(cx)}" y="{_f(y + 14)}" fill="{INK}">{escape(cell)}</text>')
        out.append("</g>")
    out.append("</g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def _hex(c: str):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def to_png(lay: Layout, path: str | Path, scale: float = 2.0, oversample: int = 2) -> tuple[int, int]:
    """Draw with Pillow at ``scale * oversample`` and downsample (anti-aliasing)."""
    k = scale * oversample
    W, H = int(round(lay.width * k)), int(round(lay.height * k))
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    m = lay.measurer

    def font(size, bold=False):
        return m.pil_font(size * k, bold)

    def text(x, y_base, s, size, color, bold=False, anchor="ls"):
        d.text((x * k, y_base * k), s, font=font(size, bold), fill=_hex(color), anchor=anchor)

    text(36, 44, lay.title, 16, INK, bold=True)
    if lay.subtitle:
        text(36, 66, lay.subtitle, LABEL_FONT, MUTED)
    for wg in lay.wires:
        pts = [(x * k, y * k) for x, y in wg.points]
        d.line(pts, fill=_hex(wg.color), width=max(1, int(round(wg.width * k))), joint="curve")
    for b in lay.boxes:
        fill = HUB_FILL if b.role == "hub" else BOX_FILL
        d.rounded_rectangle([b.x * k, b.y * k, (b.x + b.w) * k, (b.y + b.h) * k], radius=6 * k,
                            fill=_hex(fill), outline=_hex(BOX_STROKE), width=max(1, int(1.4 * k)))
        text(b.x + b.w / 2, b.y + 19, b.part, TITLE_FONT, INK, bold=True, anchor="ms")
        for p in b.pins:
            r = 3.6 * k
            d.ellipse([p.x * k - r, p.y * k - r, p.x * k + r, p.y * k + r], fill=_hex(lay.net_colors[p.net]),
                      outline=(255, 255, 255), width=max(1, int(k)))
            if p.side == "R":
                text(p.x - 9, p.y + 4, p.pin, PIN_FONT, INK, anchor="rs")
            else:
                text(p.x + 9, p.y + 4, p.pin, PIN_FONT, INK, anchor="ls")
    for la in lay.labels:
        text(la.x, la.y, la.text, LABEL_FONT, la.color)
    ly = lay.legend_y
    text(36, ly + 4, "图例 Legend:", LABEL_FONT, INK)
    x = 36 + m.width("图例 Legend:", LABEL_FONT) + 12
    for s, color in (("电源 Power", "#D62728"), ("地 Ground", "#111111"),
                     ("信号 Signal（按网络着色 coloured per net）", "#1F77B4")):
        d.line([(x * k, ly * k), ((x + 22) * k, ly * k)], fill=_hex(color), width=int(2.6 * k))
        text(x + 28, ly + 4, s, LABEL_FONT, INK)
        x += 28 + m.width(s, LABEL_FONT) + 18
    top = lay.table_top
    for i, (c, head) in enumerate(zip(lay.table_cols, lay.table_header)):
        text(c + (22 if i == 0 else 0), top + 14, head, LABEL_FONT, INK, bold=True)
    right = lay.table_cols[-1] + 260
    d.line([(lay.table_cols[0] * k, (top + ROW_H - 2) * k), (right * k, (top + ROW_H - 2) * k)],
           fill=_hex("#C8CCD2"), width=max(1, int(k)))
    for r in lay.table_rows:
        c0 = lay.table_cols[0]
        d.line([(c0 * k, (r.y + 10) * k), ((c0 + 16) * k, (r.y + 10) * k)], fill=_hex(r.color), width=int(3 * k))
        for i, (c, cell) in enumerate(zip(lay.table_cols, r.cells)):
            text(c + (22 if i == 0 else 0), r.y + 14, cell, LABEL_FONT, INK)
    if oversample > 1:
        img = img.resize((int(round(lay.width * scale)), int(round(lay.height * scale))), Image.LANCZOS)
    img.save(path, pnginfo=_png_meta(lay))
    return img.size


def _png_meta(lay: Layout):
    from PIL.PngImagePlugin import PngInfo

    meta = PngInfo()
    meta.add_itxt("Title", lay.title)
    meta.add_itxt("Software", "hardware-studio/diagrams wiring")
    meta.add_itxt("Wires", str(len(lay.wires)))
    return meta
