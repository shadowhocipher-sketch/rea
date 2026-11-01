"""Place parts, pins, wires, net labels and the wire table.

Layout (left to right): left column of parts | channel | hub part | channel | right column.
The hub is the part with the most wires (normally the MCU). Every other part sits
in a column with its pins on the edge facing the hub. Wires are orthogonal:

* each wire that needs a vertical segment gets its own track (unique x) in its channel;
* side-column pins sit on whole grid steps (k * PITCH); hub pins sit on half steps,
  or on a whole step only when they connect straight across to that very pin,
  so horizontal segments of different nets never share a y inside a channel;
* a wire between parts in opposite columns runs down to its own lane below all parts;
* net labels sit just outside the box edge, above their own pin's stub, in a zone
  that only that pin's stub crosses.

``check_layout`` re-verifies these properties geometrically.
"""

from __future__ import annotations

import math
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field

from .model import Wire
from .text import TextMeasurer

PITCH = 26.0  # pin spacing
TRACK = 13.0  # spacing between vertical tracks
PIN_FONT = 12
LABEL_FONT = 11
TITLE_FONT = 13
BOX_PAD = 10.0
MARGIN = 36.0
ZONE_PAD = 8.0
LANE_GAP = 13.0
ROW_H = 21.0

POWER_COLORS = ["#D62728", "#B0141E", "#E8613C", "#C2185B"]
GROUND_COLORS = ["#111111", "#555555"]
SIGNAL_COLORS = ["#1F77B4", "#2CA02C", "#9467BD", "#FF7F0E", "#17BECF", "#8C564B", "#E377C2",
                 "#7F7F00", "#3B5BA9", "#0E8A6D", "#7B4FA0", "#A0522D", "#00838F", "#5D6D7E"]


@dataclass
class PinGeom:
    part: str
    pin: str
    side: str  # edge of the box: "L" or "R"
    x: float
    y: float
    net: str


@dataclass
class BoxGeom:
    part: str
    x: float
    y: float
    w: float
    h: float
    role: str  # hub | left | right
    pins: list[PinGeom] = field(default_factory=list)


@dataclass
class WireGeom:
    wire: Wire
    points: list[tuple[float, float]]
    color: str
    width: float


@dataclass
class LabelGeom:
    text: str
    x: float  # anchor x of the text start (left)
    y: float  # baseline
    w: float
    h: float
    color: str
    net: str
    owner: tuple[str, str, str]  # (part, pin, side) whose stub it annotates

    @property
    def bbox(self):
        return (self.x, self.y - self.h * 0.82, self.x + self.w, self.y + self.h * 0.22)


@dataclass
class TableRow:
    cells: list[str]
    color: str
    y: float


@dataclass
class Layout:
    width: float
    height: float
    title: str
    subtitle: str
    boxes: list[BoxGeom]
    wires: list[WireGeom]
    labels: list[LabelGeom]
    table_header: list[str]
    table_cols: list[float]
    table_rows: list[TableRow]
    table_top: float
    legend_y: float
    net_colors: dict[str, str]
    font_family: str
    measurer: TextMeasurer

    def pin_points(self) -> dict[tuple[str, str], list[tuple[float, float]]]:
        out: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
        for b in self.boxes:
            for p in b.pins:
                out[(p.part, p.pin)].append((p.x, p.y))
        return out


def net_colors(wires: list[Wire]) -> dict[str, str]:
    colors: dict[str, str] = {}
    counters = {"power": 0, "ground": 0, "signal": 0}
    palettes = {"power": POWER_COLORS, "ground": GROUND_COLORS, "signal": SIGNAL_COLORS}
    for w in wires:
        if w.net in colors:
            continue
        pal = palettes[w.kind]
        colors[w.net] = pal[counters[w.kind] % len(pal)]
        counters[w.kind] += 1
    return colors


def _width(kind: str) -> float:
    return 2.6 if kind in ("power", "ground") else 1.8


# ------------------------------------------------------------- placement ---

def _choose_hub(wires: list[Wire], parts: list[str]) -> str:
    deg = defaultdict(int)
    for w in wires:
        deg[w.from_part] += 1
        deg[w.to_part] += 1
    return max(parts, key=lambda p: (deg[p], -parts.index(p)))


def _assign_sides(wires, parts, hub, pin_count) -> dict[str, str]:
    # groups = connected components of non-hub parts (ignoring the hub)
    parent = {p: p for p in parts if p != hub}

    def find(p):
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    for w in wires:
        a, b = w.from_part, w.to_part
        if a != hub and b != hub and a != b:
            parent[find(a)] = find(b)
    groups: OrderedDict[str, list[str]] = OrderedDict()
    for p in parts:
        if p != hub:
            groups.setdefault(find(p), []).append(p)
    load = {"right": 0.0, "left": 0.0}
    side: dict[str, str] = {}
    for members in sorted(groups.values(), key=lambda g: -sum(pin_count[m] + 1.5 for m in g)):
        s = "right" if load["right"] <= load["left"] else "left"
        for m in members:
            side[m] = s
        load[s] += sum(pin_count[m] + 1.5 for m in members)
    return side


@dataclass
class _ChanWire:
    wire: Wire
    stubs: list[tuple[float, str]]  # (y, "L"|"R")
    lo: float
    hi: float


def _order_tracks(items: list[_ChanWire]) -> list[_ChanWire]:
    """Linear ordering that minimises stub/vertical crossings (greedy + local moves)."""
    n = len(items)
    if n <= 1:
        return items

    def inside(y, it):
        return it.lo + 1e-6 < y < it.hi - 1e-6

    cost = [[0] * n for _ in range(n)]  # cost[i][j]: crossings if i is left of j
    for i, a in enumerate(items):
        for j, b in enumerate(items):
            if i == j:
                continue
            c = sum(1 for y, s in b.stubs if s == "L" and inside(y, a))
            c += sum(1 for y, s in a.stubs if s == "R" and inside(y, b))
            cost[i][j] = c

    order = sorted(range(n), key=lambda i: ((items[i].lo + items[i].hi) / 2, items[i].lo))

    def total(o):
        return sum(cost[o[x]][o[y]] for x in range(n) for y in range(x + 1, n))

    best = total(order)
    improved = True
    passes = 0
    while improved and passes < 20:
        improved = False
        passes += 1
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                cand = order[:]
                item = cand.pop(i)
                cand.insert(j, item)
                c = total(cand)
                if c < best:
                    order, best, improved = cand, c, True
    return [items[i] for i in order]


def build_layout(wires: list[Wire], title: str = "", subtitle: str = "",
                 measurer: TextMeasurer | None = None) -> Layout:
    m = measurer or TextMeasurer()
    colors = net_colors(wires)

    parts: list[str] = []
    pins: dict[str, list[str]] = defaultdict(list)
    pin_net: dict[tuple[str, str], str] = {}
    for w in wires:
        for part, pin in w.ends:
            if part not in parts:
                parts.append(part)
            if pin not in pins[part]:
                pins[part].append(pin)
            pin_net[(part, pin)] = w.net
    hub = _choose_hub(wires, parts)
    side = _assign_sides(wires, parts, hub, {p: len(pins[p]) for p in parts})
    side[hub] = "hub"

    # which edge(s) each hub pin appears on
    def peer_side(w: Wire, end_idx: int) -> str:
        other = w.ends[1 - end_idx][0]
        s = side[other]
        return "L" if s in ("left", "hub") else "R"

    hub_pin_sides: dict[str, list[str]] = defaultdict(list)
    for w in wires:
        for k, (part, pin) in enumerate(w.ends):
            if part == hub:
                s = peer_side(w, k)
                if s not in hub_pin_sides[pin]:
                    hub_pin_sides[pin].append(s)

    # ---- side columns (y positions on whole grid steps)
    top0 = MARGIN + 64.0  # leave room for title
    top0 = math.ceil(top0 / PITCH) * PITCH
    columns = {"left": [p for p in parts if side[p] == "left"], "right": [p for p in parts if side[p] == "right"]}
    pin_y: dict[tuple[str, str], float] = {}
    box_y: dict[str, tuple[float, float]] = {}
    for col, plist in columns.items():
        y = top0
        for p in plist:
            n = len(pins[p])
            for i, pin in enumerate(pins[p]):
                pin_y[(p, pin)] = y + PITCH * (1 + i)
            bottom = y + PITCH * (n + 0.6)
            box_y[p] = (y - PITCH * 0.45, bottom)
            y = math.ceil((bottom + PITCH * 1.2) / PITCH) * PITCH

    # ---- hub pins per edge: half steps, or a whole step aligned to its own peer
    hub_y: dict[tuple[str, str], float] = {}
    for edge in ("L", "R"):
        entries = []
        for pin in pins[hub]:
            if edge not in hub_pin_sides[pin]:
                continue
            peers = []
            for w in wires:
                for k, (part, pn) in enumerate(w.ends):
                    if part == hub and pn == pin and peer_side(w, k) == edge:
                        op, opin = w.ends[1 - k]
                        if op != hub:
                            peers.append(pin_y[(op, opin)])
            target = sum(peers) / len(peers) if peers else None
            entries.append((pin, target, set(peers)))
        # pins with targets sorted by target; target-less (hub-hub loops) go last
        entries.sort(key=lambda e: (e[1] is None, e[1] if e[1] is not None else 0))
        prev = top0 + PITCH * 0.5 - PITCH
        for pin, target, peer_ys in entries:
            lo = prev + PITCH
            want = max(target if target is not None else lo, lo)
            odd = (math.ceil(want / PITCH - 0.5) + 0.5) * PITCH
            cands = [odd] + [py for py in peer_ys if py >= want - 1e-6]
            if len(peer_ys) == 1:
                (py,) = peer_ys
                if py >= lo - 1e-6:
                    cands.append(py)
            y = min(cands)
            hub_y[(pin, edge)] = y
            prev = y
    hub_ys = list(hub_y.values()) or [top0 + PITCH]
    hub_top = min(top0 - PITCH * 0.45, min(hub_ys) - PITCH * 1.45)
    hub_bottom = max(hub_ys) + PITCH * 0.6

    # ---- widths
    def box_width(p: str, two_sided: bool) -> float:
        tw = m.width(p, TITLE_FONT, bold=True) + 2 * BOX_PAD
        if two_sided:
            lw = max([m.width(pin, PIN_FONT) for pin in pins[p] if "L" in hub_pin_sides[pin]] or [0])
            rw = max([m.width(pin, PIN_FONT) for pin in pins[p] if "R" in hub_pin_sides[pin]] or [0])
            pw = lw + rw + 3 * BOX_PAD + 16
        else:
            pw = max(m.width(pin, PIN_FONT) for pin in pins[p]) + 2 * BOX_PAD + 8
        return max(tw, pw, 96.0)

    lw_col = max([box_width(p, False) for p in columns["left"]] or [0])
    rw_col = max([box_width(p, False) for p in columns["right"]] or [0])
    hub_w = box_width(hub, True)

    def label_zone(pairs) -> float:
        ws = [m.width(pin_net[pp], LABEL_FONT) for pp in pairs]
        return (max(ws) + 2 * ZONE_PAD) if ws else 0.0

    zone_left_outer = label_zone([(p, pin) for p in columns["left"] for pin in pins[p]])
    zone_left_hub = label_zone([(hub, pin) for pin in pins[hub] if "L" in hub_pin_sides[pin]])
    zone_right_hub = label_zone([(hub, pin) for pin in pins[hub] if "R" in hub_pin_sides[pin]])
    zone_right_outer = label_zone([(p, pin) for p in columns["right"] for pin in pins[p]])

    # ---- channel membership
    def end_geom(part: str, pin: str, toward: str):
        """(x placeholder key, y, column) for an end; toward = edge used on the hub."""
        if part == hub:
            return ("hub", hub_y[(pin, toward)])
        return (side[part], pin_y[(part, pin)])

    chan_items: dict[str, list[_ChanWire]] = {"L": [], "R": []}
    cross: list[Wire] = []
    straight: list[Wire] = []
    wire_route: dict[int, dict] = {}
    for w in wires:
        (pa, pna), (pb, pnb) = w.ends
        sa, sb = side[pa], side[pb]
        if {sa, sb} == {"left", "right"}:
            cross.append(w)
            continue
        if sa == "hub" and sb == "hub":
            chan = "L"
        elif "left" in (sa, sb):
            chan = "L"
        else:
            chan = "R"
        ys = []
        stubs = []
        for part, pin in w.ends:
            if part == hub:
                y = hub_y[(pin, chan)]
                stubs.append((y, "R" if chan == "L" else "L"))
            else:
                y = pin_y[(part, pin)]
                stubs.append((y, "L" if chan == "L" else "R"))
            ys.append(y)
        wire_route[w.row] = {"chan": chan, "ys": ys}
        if abs(ys[0] - ys[1]) < 1e-6 and stubs[0][1] != stubs[1][1]:
            straight.append(w)
            continue
        chan_items[chan].append(_ChanWire(w, stubs, min(ys), max(ys)))

    all_bottom = max([b for _, b in box_y.values()] + [hub_bottom])
    lanes: dict[int, float] = {}
    for i, w in enumerate(cross):
        lanes[w.row] = all_bottom + PITCH * 0.8 + i * LANE_GAP
    for w in cross:
        (pa, pna), (pb, pnb) = w.ends
        ya = pin_y[(pa, pna)]
        yb = pin_y[(pb, pnb)]
        yl, yr = (ya, yb) if side[pa] == "left" else (yb, ya)
        lane = lanes[w.row]
        chan_items["L"].append(_ChanWire(w, [(yl, "L"), (lane, "R")], yl, lane))
        chan_items["R"].append(_ChanWire(w, [(lane, "L"), (yr, "R")], yr, lane))

    order = {c: _order_tracks(items) for c, items in chan_items.items()}

    # ---- x positions
    x = MARGIN
    left_col_x = x
    if columns["left"]:
        x += lw_col
    left_edge_x = x  # right edge of left boxes (pins)
    x += zone_left_outer
    track_l0 = x + (ZONE_PAD if columns["left"] else 0)
    n_l = len(order["L"])
    x = track_l0 + max(n_l - 1, 0) * TRACK + (ZONE_PAD if n_l else 0)
    x += zone_left_hub
    if not columns["left"] and n_l == 0:
        x = MARGIN
    hub_x = x
    x += hub_w
    hub_right_x = x
    x += zone_right_hub
    track_r0 = x + ZONE_PAD
    n_r = len(order["R"])
    x = track_r0 + max(n_r - 1, 0) * TRACK + ZONE_PAD
    x += zone_right_outer
    right_col_x = x
    if columns["right"]:
        x += rw_col
    diagram_right = x

    track_x = {"L": {}, "R": {}}
    for c, t0 in (("L", track_l0), ("R", track_r0)):
        for k, it in enumerate(order[c]):
            track_x[c].setdefault(it.wire.row, t0 + k * TRACK)

    # ---- boxes & pins
    boxes: list[BoxGeom] = []
    hub_box = BoxGeom(hub, hub_x, hub_top, hub_w, hub_bottom - hub_top, "hub")
    for pin in pins[hub]:
        for edge in hub_pin_sides[pin]:
            px = hub_x if edge == "L" else hub_right_x
            hub_box.pins.append(PinGeom(hub, pin, edge, px, hub_y[(pin, edge)], pin_net[(hub, pin)]))
    boxes.append(hub_box)
    for col in ("left", "right"):
        for p in columns[col]:
            y0, y1 = box_y[p]
            if col == "left":
                bx, edge, px = left_col_x + (lw_col - box_width(p, False)), "R", left_edge_x
                bw = box_width(p, False)
            else:
                bx, edge, px = right_col_x, "L", right_col_x
                bw = box_width(p, False)
            b = BoxGeom(p, bx, y0, bw, y1 - y0, col)
            for pin in pins[p]:
                b.pins.append(PinGeom(p, pin, edge, px, pin_y[(p, pin)], pin_net[(p, pin)]))
            boxes.append(b)
    if columns["left"]:
        # right-align left boxes to the shared pin edge
        for b in boxes:
            if b.role == "left":
                b.x = left_edge_x - b.w

    pin_xy: dict[tuple[str, str, str], tuple[float, float]] = {}
    for b in boxes:
        for p in b.pins:
            pin_xy[(p.part, p.pin, p.side)] = (p.x, p.y)

    def end_xy(part, pin, chan):
        if part == hub:
            return pin_xy[(part, pin, chan)]
        s = "R" if side[part] == "left" else "L"
        return pin_xy[(part, pin, s)]

    # ---- wire polylines
    wire_geoms: list[WireGeom] = []
    for w in wires:
        (pa, pna), (pb, pnb) = w.ends
        if w in cross:
            if side[pa] == "left":
                a = end_xy(pa, pna, "L")
                b = end_xy(pb, pnb, "R")
            else:
                a = end_xy(pa, pna, "R")
                b = end_xy(pb, pnb, "L")
            tl, tr = track_x["L"][w.row], track_x["R"][w.row]
            lane = lanes[w.row]
            if side[pa] == "left":
                pts = [a, (tl, a[1]), (tl, lane), (tr, lane), (tr, b[1]), b]
            else:
                pts = [a, (tr, a[1]), (tr, lane), (tl, lane), (tl, b[1]), b]
        else:
            chan = wire_route[w.row]["chan"]
            a = end_xy(pa, pna, chan)
            b = end_xy(pb, pnb, chan)
            if w in straight:
                pts = [a, b]
            else:
                t = track_x[chan][w.row]
                pts = [a, (t, a[1]), (t, b[1]), b]
        wire_geoms.append(WireGeom(w, [(float(px), float(py)) for px, py in pts], colors[w.net], _width(w.kind)))

    # ---- labels (one per pin instance that has a stub)
    labels: list[LabelGeom] = []
    for b in boxes:
        for p in b.pins:
            text = p.net
            tw = m.width(text, LABEL_FONT)
            lx = p.x + ZONE_PAD if p.side == "R" else p.x - ZONE_PAD - tw
            labels.append(LabelGeom(text, lx, p.y - 4.0, tw, LABEL_FONT, colors[p.net], p.net,
                                    (p.part, p.pin, p.side)))

    # ---- table & legend
    lane_bottom = max(lanes.values()) if lanes else all_bottom
    legend_y = lane_bottom + PITCH * 1.4
    table_top = legend_y + PITCH * 1.1
    header = ["#", "从 From", "到 To", "网络 Net", "类型 Kind", "备注 Note"]
    kind_cn = {"power": "电源 power", "ground": "地 ground", "signal": "信号 signal"}
    rows_text = [[str(w.row), f"{w.from_part}.{w.from_pin}", f"{w.to_part}.{w.to_pin}", w.net,
                  kind_cn[w.kind], w.note] for w in wires]
    col_w = []
    for c in range(len(header)):
        cw = max([m.width(header[c], LABEL_FONT, bold=True)] + [m.width(r[c], LABEL_FONT) for r in rows_text])
        col_w.append(cw + 18)
    col_w[0] += 22  # swatch
    cols = [MARGIN]
    for cw in col_w[:-1]:
        cols.append(cols[-1] + cw)
    table_right = cols[-1] + col_w[-1]
    table_rows = [TableRow(r, colors[w.net], table_top + ROW_H * (i + 1)) for i, (r, w) in enumerate(zip(rows_text, wires))]
    height = table_top + ROW_H * (len(rows_text) + 1) + MARGIN
    title_w = max(m.width(title, 16, bold=True), m.width(subtitle, LABEL_FONT)) + 2 * MARGIN
    legend_w = m.width("图例 Legend:  电源 Power  地 Ground  信号 Signal（按网络着色 coloured per net）", LABEL_FONT) + 120
    width = max(diagram_right, table_right, title_w, legend_w + MARGIN) + MARGIN
    return Layout(width, height, title, subtitle, boxes, wire_geoms, labels, header, cols, table_rows,
                  table_top, legend_y, colors, m.family, m)


# ---------------------------------------------------------- verification ---

def _seg_overlap(s1, s2) -> bool:
    """True if two axis-parallel segments overlap collinearly with positive length."""
    (x1, y1), (x2, y2) = s1
    (x3, y3), (x4, y4) = s2
    if abs(y1 - y2) < 1e-6 and abs(y3 - y4) < 1e-6 and abs(y1 - y3) < 1e-6:
        a0, a1 = sorted((x1, x2))
        b0, b1 = sorted((x3, x4))
        return min(a1, b1) - max(a0, b0) > 1e-6
    if abs(x1 - x2) < 1e-6 and abs(x3 - x4) < 1e-6 and abs(x1 - x3) < 1e-6:
        a0, a1 = sorted((y1, y2))
        b0, b1 = sorted((y3, y4))
        return min(a1, b1) - max(a0, b0) > 1e-6
    return False


def _rect_overlap(a, b, pad=0.0) -> bool:
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad


def _seg_hits_rect(seg, r) -> bool:
    (x1, y1), (x2, y2) = seg
    xa, xb = sorted((x1, x2))
    ya, yb = sorted((y1, y2))
    return xa < r[2] and xb > r[0] and ya < r[3] and yb > r[1]


def check_layout(lay: Layout) -> list[str]:
    """Geometric overlap check; returns a list of problems (empty = clean)."""
    problems: list[str] = []
    rects = [(b.part, (b.x, b.y, b.x + b.w, b.y + b.h)) for b in lay.boxes]
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if _rect_overlap(rects[i][1], rects[j][1], pad=6):
                problems.append(f"boxes overlap: {rects[i][0]} / {rects[j][0]}")
    segs = []
    for wg in lay.wires:
        for a, b in zip(wg.points, wg.points[1:]):
            if a[0] != b[0] and a[1] != b[1]:
                problems.append(f"row {wg.wire.row}: non-orthogonal segment {a}->{b}")
            segs.append((wg.wire, (a, b)))
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            wi, si = segs[i]
            wj, sj = segs[j]
            if wi.net != wj.net and _seg_overlap(si, sj):
                problems.append(f"wires overlap: row {wi.row} ({wi.net}) / row {wj.row} ({wj.net})")
    for w, s in segs:
        for name, r in rects:
            inner = (r[0] + 0.5, r[1] + 0.5, r[2] - 0.5, r[3] - 0.5)
            if _seg_hits_rect(s, inner):
                problems.append(f"row {w.row}: wire passes through box {name}")
    for i, la in enumerate(lay.labels):
        for lb in lay.labels[i + 1:]:
            if _rect_overlap(la.bbox, lb.bbox):
                problems.append(f"labels overlap: {la.owner} / {lb.owner}")
        for name, r in rects:
            if _rect_overlap(la.bbox, r):
                problems.append(f"label {la.text!r} of {la.owner} overlaps box {name}")
        for w, s in segs:
            if w.net != la.net and _seg_hits_rect(s, la.bbox):
                problems.append(f"label {la.text!r} of {la.owner} crossed by row {w.row} ({w.net})")
    diagram_bottom = max([b.y + b.h for b in lay.boxes] + [p[1] for wg in lay.wires for p in wg.points])
    if diagram_bottom > lay.legend_y - 8:
        problems.append("legend overlaps the diagram")
    if any(b.x < 0 or b.x + b.w > lay.width for b in lay.boxes):
        problems.append("box outside canvas")
    return problems
