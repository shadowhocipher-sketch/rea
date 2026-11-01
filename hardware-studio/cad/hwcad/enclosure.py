"""从参数（YAML 读进来的 dict）拼出完整外壳。格式定义见 ``cad/README.md``。

只负责"造型"；测量、干涉、导出由 ``cad/tools/`` 和 ``cad/build_enclosure.py`` 完成。
坐标约定见 :mod:`hwcad.frames`。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from build123d import Align, Box, Location, Part, Plane

from . import battery as _battery
from . import bosses as _bosses
from . import buttons as _buttons
from . import snaps as _snaps
from . import usbc as _usbc
from . import windows as _windows
from .frames import Feature, face_plane, wall_plane
from .process import PRINTER_BEDS, ProcessRules, get_process
from .shell import ShellSpec, make_shell


@dataclass
class BuildResult:
    """拼装结果。

    Attributes:
        name: 外壳名。
        process: 工艺规则。
        shell: 外壳主体参数。
        parts: 要制造的零件（对外名 -> Part，装配位置，全局坐标）。
        envelopes: 检查用包络体（元器件、电池膨胀外形、USB 插座和插头外壳）。
        features: 所有特征（含 info）。
        warnings: 造型阶段发现的问题。
        printer_bed: 打印平台尺寸 (x, y, z) 或 None。
        ignore_pairs: 不参与干涉判定的名称对。
    """

    name: str
    process: ProcessRules
    shell: ShellSpec
    parts: dict[str, Part]
    envelopes: dict[str, Part]
    features: list[Feature]
    warnings: list[str] = field(default_factory=list)
    printer_bed: tuple[float, float, float] | None = None
    printer_name: str | None = None
    ignore_pairs: list[tuple[str, str]] = field(default_factory=list)
    fastener_info: list[dict] = field(default_factory=list)


def _shell_spec(d: dict, proc: ProcessRules) -> ShellSpec:
    size = d.get("size")
    if not size or len(size) != 3:
        raise ValueError("shell.size 必须是 [length_x, width_y, height_z]（mm）")
    lip = d.get("lip", {}) or {}
    wall = float(d.get("wall", proc.default_wall))
    return ShellSpec(
        length=float(size[0]),
        width=float(size[1]),
        height=float(size[2]),
        wall=wall,
        corner_radius=float(d.get("corner_radius", 4.0)),
        edge_radius=float(d.get("edge_radius", 1.0)),
        split_z=float(d.get("split_z", size[2] / 2)),
        lip_height=float(lip.get("height", 2.0)),
        lip_thickness=float(lip.get("thickness", round(wall * 0.4, 2))),
        lip_clearance=float(lip.get("clearance", proc.fit_clearance)),
        style=d.get("style", "top_bottom"),
    )


def _side_part(face: str, v: float, shell: ShellSpec) -> str:
    if face == "top":
        return "upper"
    if face == "bottom":
        return "lower"
    return "upper" if v > shell.split_z else "lower"


def _flip_down(shape: Part, x: float, y: float, z_top: float) -> Part:
    """把沿 +Z 建模、底面在原点的实体翻转成"倒挂"，顶面放在 z_top。"""
    return shape.moved(Location((x, y, z_top), (180, 0, 0)))


def build_enclosure(spec: dict) -> BuildResult:
    """按参数 dict 造型。

    Args:
        spec: YAML 解析出的 dict，字段见 ``cad/README.md``。

    Returns:
        :class:`BuildResult`。
    """
    proc = get_process(spec.get("process", "fdm"))
    shell = _shell_spec(spec.get("shell", {}), proc)
    warnings = [f"shell: {e}" for e in shell.validate(proc.min_wall)]
    if any("split_z" in w or "必须" in w for w in warnings):
        raise ValueError("; ".join(warnings))
    size, t, H = shell.size, shell.wall, shell.height
    halves = make_shell(shell)
    adds: dict[str, list[Part]] = {"lower": [], "upper": []}
    cuts: dict[str, list[Part]] = {"lower": [], "upper": []}
    features: list[Feature] = []
    extra_parts: dict[str, Part] = {}
    fastener_info: list[dict] = []

    def register(f: Feature) -> None:
        features.append(f)
        a = f.placed_add()
        if a is not None:
            adds[f.add_to].append(a)
        c = f.placed_cut()
        if c is not None:
            for p in f.cut_from:
                cuts[p].append(c)
        for w in f.info.get("warnings", []):
            warnings.append(f"{f.name}: {w}")

    # --- 两半壳之间的螺丝连接 ---
    for i, fs in enumerate(spec.get("fasteners", []) or []):
        x, y = float(fs["x"]), float(fs["y"])
        kind = fs.get("kind", "self_tap")
        thread = fs.get("thread", "M3")
        meet = float(fs.get("meet_z", shell.split_z))
        gap = float(fs.get("gap", 0.2))
        up_h = H - t - meet + 0.01
        if kind == "self_tap":
            b, binfo = _bosses.self_tap_boss(thread, up_h, fs.get("hole_factor", 0.8), fs.get("outer_factor", 2.0))
        elif kind == "heat_insert":
            b, binfo = _bosses.heat_insert_boss(thread, up_h, fs.get("insert_hole_d"), fs.get("insert_length"),
                                                fs.get("min_wall"))
        else:
            raise ValueError(f"fasteners[{i}].kind 必须是 self_tap 或 heat_insert")
        adds["upper"].append(_flip_down(b, x, y, H - t + 0.01))
        post_h = meet - gap - t + 0.01
        cb_depth = float(fs.get("counterbore_depth", 2.0))
        d = _bosses.thread_diameter(thread)
        head_d = float(fs.get("head_d", 2.0 * d + 0.6))
        # 沉头孔比柱子粗时，沉头孔底部一圈只剩 (wall - cb_depth) 厚；所以柱外径至少 = 沉头孔径 + 2 × 最小壁厚
        post_od = fs.get("post_outer_d", max(binfo["outer_d"], head_d + 2 * proc.min_wall if cb_depth > 0 else 0.0))
        post, pinfo = _bosses.clearance_post(thread, post_h, fs.get("clearance_d"), post_od)
        adds["lower"].append(post.moved(Location((x, y, t - 0.01))))
        cb = _bosses.counterbore_cutter(thread, cb_depth, head_d, meet + 1.0, fs.get("clearance_d"))
        cuts["lower"].append(cb.moved(Location(face_plane(size, "bottom", x, y))))
        engage = binfo.get("hole_depth", up_h) if kind == "heat_insert" else min(up_h, 2.5 * d)
        fastener_info.append({
            "name": f"fastener_{i}", "x": x, "y": y, "upper_boss": binfo, "lower_post": pinfo,
            "counterbore_depth": cb_depth,
            "screw_length_suggest": round(meet - cb_depth + min(engage, up_h) - 0.5, 1),
            "note": "建议螺丝长度 = 沉头底到分模面 + 拧入深度 - 0.5 mm（估算，向下取标准长度）",
        })

    # --- PCB 支柱等单独的柱子 ---
    for i, so in enumerate(spec.get("standoffs", []) or []):
        x, y = float(so["x"]), float(so["y"])
        part = so.get("part", "lower")
        h = float(so.get("height", 4.0))
        kind = so.get("kind", "self_tap")
        if kind == "self_tap":
            b, binfo = _bosses.self_tap_boss(so.get("thread", "M2"), h + 0.01)
        elif kind == "heat_insert":
            b, binfo = _bosses.heat_insert_boss(so.get("thread", "M3"), h + 0.01, so.get("insert_hole_d"),
                                                so.get("insert_length"), so.get("min_wall"))
        else:
            b = _bosses.boss(float(so["outer_d"]), float(so.get("hole_d", 0.0)), h + 0.01)
            binfo = {"kind": "plain", "outer_d": so["outer_d"], "hole_d": so.get("hole_d", 0.0)}
        if part == "lower":
            adds["lower"].append(b.moved(Location((x, y, t - 0.01))))
        else:
            adds["upper"].append(_flip_down(b, x, y, H - t + 0.01))
        fastener_info.append({"name": f"standoff_{i}", "x": x, "y": y, "part": part, "height": h, **binfo})

    # --- 屏幕窗 ---
    for i, w in enumerate(spec.get("screen_windows", []) or []):
        st = w.get("step") or {}
        f = _windows.screen_window(
            wall=t, shape=w.get("shape", "rect"), width=float(w["width"]), height=float(w.get("height", w["width"])),
            corner_radius=float(w.get("corner_radius", 1.0)), margin=float(w.get("margin", 0.0)),
            step_width=st.get("width"), step_height=st.get("height"), step_depth=float(st.get("depth", 0.0)),
            step_clearance=float(st.get("clearance", proc.fit_clearance)),
            step_corner_radius=float(st.get("corner_radius", 0.5)), min_wall=proc.min_wall,
            name=w.get("name", f"screen_window_{i}"),
        )
        f.plane = face_plane(size, w["face"], float(w.get("u", 0)), float(w.get("v", 0)))
        f.cut_from = (_side_part(w["face"], float(w.get("v", 0)), shell),) if w["face"] in ("top", "bottom") else ("lower", "upper")
        register(f)

    # --- 按键 ---
    for i, b in enumerate(spec.get("buttons", []) or []):
        face, u, v = b["face"], float(b.get("u", 0)), float(b.get("v", 0))
        name = b.get("name", f"button_{i}")
        part = _side_part(face, v, shell)
        if b.get("type", "hole") == "hole":
            f = _buttons.button_hole(t, float(b.get("diameter", 6.0)), float(b.get("clearance", proc.fit_clearance)),
                                     float(b.get("sleeve_length", 0.0)), float(b.get("sleeve_wall", proc.min_wall)),
                                     name=name)
            if b.get("cap", True):
                cap = _buttons.button_cap(t, float(b.get("diameter", 6.0)), float(b.get("protrusion", 1.0)),
                                          float(b.get("sleeve_length", 0.0)), flange_t=float(b.get("flange_t", proc.min_wall)),
                                          gap=float(b.get("cap_gap", 0.3)),
                                          plunger_length=float(b.get("plunger_length", 1.0)))
                extra_parts[f"cap_{name}"] = cap.moved(Location(face_plane(size, face, u, v)))
        else:
            f = _buttons.cantilever_button(
                t, float(b.get("length", 12.0)), float(b.get("width", 7.0)), float(b.get("slot", 0.8)),
                b.get("tongue_thickness"), float(b.get("nub_d", 3.0)), float(b.get("nub_height", 1.5)),
                float(b.get("travel", 0.5)), b.get("allowable_strain"), name=name,
            )
        f.plane = face_plane(size, face, u, v)
        f.add_to = part
        f.cut_from = (part,)
        register(f)

    # --- USB-C ---
    for i, uc in enumerate(spec.get("usb_c", []) or []):
        rec = uc.get("receptacle", list(_usbc.DEFAULT_RECEPTACLE))
        om = uc.get("overmold", list(_usbc.DEFAULT_OVERMOLD))
        f = _usbc.usbc_cutout(t, float(uc.get("recess", 0.5)), *map(float, rec), *map(float, om),
                              clearance=float(uc.get("clearance", proc.fit_clearance)),
                              mate_gap=float(uc.get("mate_gap", 0.0)), name=uc.get("name", f"usb_c_{i}"))
        f.plane = face_plane(size, uc["face"], float(uc.get("u", 0)), float(uc.get("v", 0)))
        register(f)

    # --- 卡扣 ---
    for i, sn in enumerate(spec.get("snaps", []) or []):
        f = _snaps.snap_fit(
            t, shell.split_z, float(sn.get("length", 10.0)), float(sn.get("thickness", 1.2)),
            float(sn.get("width", 5.0)), float(sn.get("undercut", 0.8)), float(sn.get("gap", 0.2)),
            float(sn.get("flat", 0.6)), float(sn.get("lead_angle", 30.0)), float(sn.get("clearance", 0.2)),
            float(sn.get("root_height", 3.0)), float(sn.get("q", 1.0)), sn.get("allowable_strain"),
            proc.min_wall, name=sn.get("name", f"snap_{i}"),
        )
        f.plane = wall_plane(size, sn["face"], float(sn.get("u", 0)))
        hook_lo = f.info["hook_z_range"][0]
        if hook_lo < shell.split_z + shell.lip_height + shell.lip_clearance:
            warnings.append(f"{f.name}: 卡钩低于止口让位槽顶部，卡槽会落在让位槽里，请加长卡扣")
        if f.info["hook_z_range"][1] > H - t:
            warnings.append(f"{f.name}: 卡扣顶端高过顶板内表面")
        register(f)

    # --- 电池仓 ---
    bat = spec.get("battery")
    if bat:
        cell = bat["cell"]
        f = _battery.battery_bay(
            float(cell[0]), float(cell[1]), float(cell[2]), float(bat.get("swell", 0.10)),
            float(bat.get("xy_clearance", 0.5)), float(bat.get("rib_thickness", proc.min_wall)),
            float(bat.get("rib_height", 3.0)), bat.get("wire_side", "+x"), float(bat.get("wire_slot_width", 4.0)),
            float(bat.get("top_gap", 0.3)), name=bat.get("name", "battery"),
        )
        f.plane = Plane(origin=(float(bat.get("x", 0)), float(bat.get("y", 0)), t), x_dir=(1, 0, 0), z_dir=(0, 0, 1))
        register(f)

    # --- 合成 ---
    parts: dict[str, Part] = {}
    names = shell.part_names()
    for key in ("lower", "upper"):
        p = halves[key]
        for a in adds[key]:
            p = p + a
        for c in cuts[key]:
            p = p - c
        parts[names[key]] = _as_part(p)
    parts.update(extra_parts)

    envelopes: dict[str, Part] = {}
    for f in features:
        envelopes.update(f.placed_envelopes())
    for i, c in enumerate(spec.get("components", []) or []):
        sx, sy, sz = map(float, c["size"])
        cx, cy = map(float, c.get("center", [0, 0]))
        z0 = float(c.get("z", t))
        envelopes[c.get("name", f"component_{i}")] = Box(sx, sy, sz, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((cx, cy, z0))
        )

    bed, bed_name = None, None
    pr = spec.get("printer")
    if isinstance(pr, str):
        if pr not in PRINTER_BEDS:
            raise ValueError(f"未知打印机 {pr!r}，可选 {sorted(PRINTER_BEDS)}，或写 {{bed: [x, y, z]}}")
        bed, bed_name = PRINTER_BEDS[pr]["bed"], pr
    elif isinstance(pr, dict) and "bed" in pr:
        bed, bed_name = tuple(map(float, pr["bed"])), pr.get("name", "custom")

    ignore = [tuple(p) for p in (spec.get("ignore_pairs") or [])]
    return BuildResult(spec.get("name", "enclosure"), proc, shell, parts, envelopes, features, warnings, bed,
                       bed_name, ignore, fastener_info)


def _as_part(shape) -> Part:
    if isinstance(shape, Part):
        return shape
    return Part(shape.wrapped)
