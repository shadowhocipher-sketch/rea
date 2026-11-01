"""Public API: describe a render job (parts, views, scene) and write labelled PNGs."""

from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from PIL.PngImagePlugin import PngInfo

from . import engine as E
from .label import DEFAULT_LABEL, LabelInfo, draw_label
from .mesh import TriMesh, box, load_part, prism

VIEW_PRESETS = {
    "front": (0.0, 10.0),
    "back": (180.0, 10.0),
    "right": (90.0, 10.0),
    "side": (90.0, 10.0),
    "left": (-90.0, 10.0),
    "top": (0.0, 88.0),
    "iso": (45.0, 30.0),  # 45° three-quarter view from front-right
    "iso-left": (-45.0, 30.0),
    "iso-back": (225.0, 30.0),
    "hero": (28.0, 18.0),
}
_CUSTOM_VIEW = re.compile(r"^az(-?\d+(?:\.\d+)?)el(-?\d+(?:\.\d+)?)$")

SCENES = ("studio", "desk", "plain")
PROPS = ("book", "pencil")

QUALITY = {
    "draft": dict(supersample=1, sky_dirs=10, sky_res=256, key_res=1024),
    "final": dict(supersample=2, sky_dirs=24, sky_res=384, key_res=2048),
}


class RenderConfigError(ValueError):
    pass


@dataclass
class PartSpec:
    path: str
    color: str = "#D9D4CC"
    material: str = "satin"
    explode: tuple[float, float, float] = (0.0, 0.0, 0.0)
    name: str = ""

    @classmethod
    def parse(cls, spec: str) -> "PartSpec":
        """``PATH[:COLOR[:MATERIAL[:DX,DY,DZ]]]``, e.g. ``lid.step:#C9A27C:matte:0,0,25``."""
        fields = spec.split(":")
        # Allow Windows drive letters (C:\...) by re-joining a 1-letter first field.
        if len(fields) > 1 and len(fields[0]) == 1 and fields[1].startswith(("\\", "/")):
            fields = [fields[0] + ":" + fields[1]] + fields[2:]
        part = cls(path=fields[0])
        if len(fields) > 1 and fields[1]:
            part.color = fields[1]
        if len(fields) > 2 and fields[2]:
            part.material = fields[2]
        if len(fields) > 3 and fields[3]:
            part.explode = _vec3(fields[3])
        if len(fields) > 4:
            raise RenderConfigError(f"too many ':' fields in part spec {spec!r}")
        part.validate()
        return part

    def validate(self):
        try:
            E.parse_color(self.color)
        except ValueError as exc:
            raise RenderConfigError(str(exc)) from None
        if self.material not in E.MATERIALS:
            raise RenderConfigError(
                f"unknown material {self.material!r}; choose from {', '.join(E.MATERIALS)}")
        self.explode = tuple(float(v) for v in self.explode)
        if len(self.explode) != 3:
            raise RenderConfigError("explode needs 3 numbers (dx, dy, dz in mm)")
        if not self.name:
            self.name = Path(self.path).stem


def _vec3(text) -> tuple[float, float, float]:
    vals = [float(v) for v in str(text).replace(" ", "").split(",")]
    if len(vals) != 3:
        raise RenderConfigError(f"need dx,dy,dz, got {text!r}")
    return tuple(vals)


@dataclass
class RenderJob:
    parts: list[PartSpec]
    out: str = "render_out"
    name: str = "product"
    views: list[str] = field(default_factory=lambda: ["front", "side", "back", "iso"])
    scene: str = "studio"
    props: list[str] = field(default_factory=list)
    size: tuple[int, int] = (1600, 1200)
    quality: str = "final"
    supersample: int | None = None
    exploded: bool = False
    exploded_views: list[str] | None = None  # default: same as views
    explode_factor: float = 1.0
    label: str = DEFAULT_LABEL
    label_corner: str = "bottom-right"
    sheet: bool = True
    desk_color: str = "#B98B5E"
    background: tuple[str, str] | None = None
    fill: float | None = None

    def validate(self):
        if not self.parts:
            raise RenderConfigError("at least one part is required")
        for p in self.parts:
            p.validate()
        if self.scene not in SCENES:
            raise RenderConfigError(f"scene must be one of {SCENES}")
        for v in self.views + (self.exploded_views or []):
            view_angles(v)
        for p in self.props:
            if p not in PROPS:
                raise RenderConfigError(f"unknown prop {p!r}; choose from {PROPS}")
        if self.quality not in QUALITY:
            raise RenderConfigError(f"quality must be one of {tuple(QUALITY)}")
        w, h = self.size
        if not (64 <= w <= 8000 and 64 <= h <= 8000):
            raise RenderConfigError("size must be between 64 and 8000 px per side")
        if not self.label.strip():
            raise RenderConfigError("label must not be empty: renders are always marked")
        self.name = re.sub(r"[^A-Za-z0-9_-]+", "-", self.name).strip("-") or "product"


def view_angles(view: str) -> tuple[float, float]:
    if view in VIEW_PRESETS:
        return VIEW_PRESETS[view]
    m = _CUSTOM_VIEW.match(view)
    if m:
        return float(m.group(1)), float(m.group(2))
    raise RenderConfigError(
        f"unknown view {view!r}; use {', '.join(VIEW_PRESETS)} or azXXelYY (degrees)")


# ------------------------------------------------------------------ props ---

def _book() -> list[tuple[TriMesh, str, str]]:
    """An A5 paperback lying flat (148 x 210 x 16 mm), local origin at its centre bottom."""
    w, d, t, c = 148.0, 210.0, 16.0, 1.2
    return [
        (box((w, d, c), (0, 0, c / 2)), "#2F5D62", "satin"),
        (box((w, d, c), (0, 0, t - c / 2)), "#2F5D62", "satin"),
        (box((c, d, t), (-w / 2 + c / 2, 0, t / 2)), "#264C50", "satin"),
        (box((w - c - 2.0, d - 4.0, t - 2 * c), (c / 2 - 1.0, 0, t / 2)), "#F1ECE1", "paper"),
    ]


def _pencil() -> list[tuple[TriMesh, str, str]]:
    body = prism(3.6, 160.0, sides=6, cap_cone=0.0)
    tip = prism(3.6, 0.01, sides=6, cap_cone=15.0).translated((160.0, 0, 0))
    return [(body.translated((-87.5, 0, 3.6 * 0.866)), "#E8B63A", "satin"),
            (tip.translated((-87.5, 0, 3.6 * 0.866)), "#D9BE98", "matte")]


def _rot_z(deg: float) -> np.ndarray:
    a = np.radians(deg)
    return np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])


def place_props(names: list[str], parts_lo, parts_hi, cam_az: float, floor_z: float):
    """Props are placed relative to the camera so they appear in every view."""
    center = (parts_lo + parts_hi) / 2
    rp = float(np.linalg.norm((parts_hi - parts_lo)[:2]) / 2)
    gap = 0.25 * rp + 8.0
    rh = np.array([np.cos(np.radians(cam_az)), np.sin(np.radians(cam_az)), 0.0])
    fh = np.array([-np.sin(np.radians(cam_az)), np.cos(np.radians(cam_az)), 0.0])
    out = []
    for name in names:
        if name == "book":
            yaw = -14.0
            pos = center - rh * (rp + gap + 95.0) + fh * (rp * 0.8 + 75.0)
            pieces = _book()
        elif name == "pencil":
            yaw = 62.0
            pos = center + rh * (rp + gap + 20.0) - fh * (rp * 0.2)
            pieces = _pencil()
        else:
            continue
        rot = _rot_z(cam_az + yaw)
        pos = np.array([pos[0], pos[1], floor_z])
        for mesh, color, mat in pieces:
            out.append(E.SceneObject(mesh.transformed(rot, pos), E.parse_color(color), mat, "prop", name))
    return out


# ----------------------------------------------------------------- render ---

@dataclass
class RenderedImage:
    path: str
    view: str
    scene: str
    exploded: bool
    size: tuple[int, int]
    label: LabelInfo
    seconds: float

    def as_dict(self):
        d = asdict(self)
        return d


def _load_parts(job: RenderJob, cache: dict) -> list[tuple[PartSpec, TriMesh]]:
    out = []
    for p in job.parts:
        key = str(Path(p.path).resolve())
        if key not in cache:
            cache[key] = load_part(p.path)
        out.append((p, cache[key]))
    return out


def _backgrounds(job: RenderJob) -> E.Background:
    if job.background:
        return E.Background(E.parse_color(job.background[0]), E.parse_color(job.background[1]))
    if job.scene == "desk":
        return E.Background(E.parse_color("#E7E1D8"), E.parse_color("#CFC6BA"))
    if job.scene == "plain":
        return E.Background(E.parse_color("#F4F4F2"), E.parse_color("#F4F4F2"))
    return E.Background(E.parse_color("#F3F2EF"), E.parse_color("#DCDAD5"))


def _save(img: Image.Image, path: Path, label: LabelInfo, job: RenderJob, view: str, exploded: bool):
    meta = PngInfo()
    meta.add_itxt("Label", label.text)
    meta.add_itxt("Description", "Computer rendering, not a photograph / 渲染图，非实拍")
    meta.add_itxt("Software", "hardware-studio render (prender, numpy rasteriser)")
    meta.add_itxt("View", f"{view}{' exploded' if exploded else ''}; scene={job.scene}")
    img.save(path, pnginfo=meta)


def render_view(job: RenderJob, parts: list[tuple[PartSpec, TriMesh]], view: str,
                exploded: bool = False) -> tuple[Image.Image, LabelInfo]:
    q = QUALITY[job.quality]
    ss = int(job.supersample or q["supersample"])
    W, H = job.size
    az, el = view_angles(view)
    objects = []
    for spec, mesh in parts:
        m = mesh.translated(np.array(spec.explode) * job.explode_factor) if exploded else mesh
        objects.append(E.SceneObject(m, E.parse_color(spec.color), spec.material, "part", spec.name))
    pv = np.concatenate([o.mesh.vertices for o in objects])
    lo, hi = pv.min(0), pv.max(0)
    floor_z = float(lo[2])
    fill = job.fill or {"studio": 0.72, "desk": 0.5, "plain": 0.78}[job.scene]
    offset = (0.12, -0.05) if job.scene == "desk" and job.props else (0.0, 0.0)
    cam = E.fit_camera(pv, az, el, W * ss, H * ss, fill=fill, offset=offset)
    if job.scene == "desk":
        objects += place_props(job.props, lo, hi, az, floor_z)
    ground = E.Ground(kind={"studio": "studio", "desk": "desk", "plain": "none"}[job.scene], z=floor_z,
                      color=E.parse_color(job.desk_color),
                      back_edge=max(4.0 * float(np.linalg.norm(hi - lo)), 260.0),
                      center=np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, floor_z]))
    light = E.Lighting(sky_dirs=q["sky_dirs"], sky_res=q["sky_res"], key_res=q["key_res"])
    res = E.render(objects, cam, ground, _backgrounds(job), light)
    rgb = E.linear_to_srgb(E.tonemap(res.image * 1.0))
    img = Image.fromarray((rgb * 255 + 0.5).astype(np.uint8), "RGB")
    if ss > 1:
        img = img.resize((W, H), Image.LANCZOS)
    if job.scene == "desk":
        img = _depth_of_field(img, res.depth[::ss, ::ss], float(np.linalg.norm(cam.eye - cam.target)))
    label = draw_label(img, job.label, job.label_corner)
    return img, label


def _depth_of_field(img: Image.Image, depth: np.ndarray, focus: float) -> Image.Image:
    W, H = img.size
    depth = depth[:H, :W]
    blurred = img.filter(ImageFilter.GaussianBlur(radius=max(1.0, W * 0.004)))
    t = np.clip((depth - focus * 1.15) / (focus * 1.2), 0, 1)
    t = np.where(np.isfinite(depth), t, 1.0)
    t = t * t * (3 - 2 * t)
    a = np.asarray(img, np.float32)
    b = np.asarray(blurred, np.float32)
    out = a * (1 - t[..., None]) + b * t[..., None]
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8), "RGB")


def _sheet(images: list[tuple[str, Image.Image]], job: RenderJob) -> tuple[Image.Image, LabelInfo]:
    from .fonts import find_cjk_font, find_latin_font

    cols = 2 if len(images) <= 4 else 3
    rows = (len(images) + cols - 1) // cols
    W, H = job.size
    tw, th = W // 2, H // 2
    cap = max(18, th // 14)
    sheet = Image.new("RGB", (cols * tw, rows * (th + cap)), (250, 250, 248))
    font_ref = find_cjk_font() or find_latin_font()
    font = font_ref.pil(int(cap * 0.6)) if font_ref else None
    d = ImageDraw.Draw(sheet)
    for i, (title, im) in enumerate(images):
        x, y = (i % cols) * tw, (i // cols) * (th + cap)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + cap))
        d.text((x + 10, y + cap * 0.18), title, fill=(40, 40, 40), font=font)
    label = draw_label(sheet, job.label, job.label_corner)
    return sheet, label


def render_product(job: RenderJob, log=print) -> list[RenderedImage]:
    """Render every requested view (and exploded views) and write ``render_*.png``."""
    job.validate()
    out = Path(job.out)
    out.mkdir(parents=True, exist_ok=True)
    cache: dict = {}
    parts = _load_parts(job, cache)
    results: list[RenderedImage] = []
    tasks = [(v, False) for v in job.views]
    if job.exploded:
        if not any(any(p.explode) for p in job.parts):
            raise RenderConfigError("exploded views need an explode offset on at least one part")
        tasks += [(v, True) for v in (job.exploded_views or job.views)]
    thumbs = []
    for view, exploded in tasks:
        t0 = time.perf_counter()
        img, label = render_view(job, parts, view, exploded)
        tag = f"{view}-exploded" if exploded else view
        path = out / f"render_{job.name}_{job.scene}_{tag}.png"
        _save(img, path, label, job, view, exploded)
        dt = time.perf_counter() - t0
        results.append(RenderedImage(str(path), view, job.scene, exploded, img.size, label, round(dt, 2)))
        thumbs.append((tag, img))
        if log:
            log(f"wrote {path} ({img.size[0]}x{img.size[1]}, {dt:.1f}s)")
    if job.sheet and len(thumbs) > 1:
        sheet, label = _sheet(thumbs, job)
        path = out / f"render_{job.name}_{job.scene}_sheet.png"
        _save(sheet, path, label, job, "sheet", False)
        results.append(RenderedImage(str(path), "sheet", job.scene, False, sheet.size, label, 0.0))
        if log:
            log(f"wrote {path} (contact sheet)")
    return results


# ------------------------------------------------------------------- YAML ---

def job_from_dict(data: dict, base_dir: Path | None = None) -> RenderJob:
    base_dir = Path(base_dir or ".")
    parts = []
    for p in data.get("parts") or []:
        if isinstance(p, str):
            spec = PartSpec.parse(p)
        else:
            spec = PartSpec(path=str(p["path"]), color=str(p.get("color", "#D9D4CC")),
                            material=str(p.get("material", "satin")),
                            explode=tuple(p.get("explode", (0, 0, 0))), name=str(p.get("name", "")))
        if not Path(spec.path).is_absolute():
            spec.path = str((base_dir / spec.path).resolve())
        spec.validate()
        parts.append(spec)
    kw = {}
    for key in ("name", "scene", "quality", "label", "label_corner", "sheet", "desk_color",
                "explode_factor", "supersample", "fill", "exploded"):
        if key in data:
            kw[key] = data[key]
    if "out" in data:
        out = Path(data["out"])
        kw["out"] = str(out if out.is_absolute() else (base_dir / out).resolve())
    if "views" in data:
        kw["views"] = _as_list(data["views"])
    if "props" in data:
        kw["props"] = _as_list(data["props"])
    if "size" in data:
        kw["size"] = _size(data["size"])
    if "background" in data:
        kw["background"] = tuple(data["background"])
    if "exploded_views" in data:
        kw["exploded_views"] = _as_list(data["exploded_views"])
        kw.setdefault("exploded", True)
    job = RenderJob(parts=parts, **kw)
    return job


def load_job(path: str | Path) -> RenderJob:
    import yaml

    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise RenderConfigError(f"{path}: top level must be a mapping")
    return job_from_dict(data, path.parent)


def _as_list(v) -> list[str]:
    if isinstance(v, str):
        return [s.strip() for s in v.split(",") if s.strip()]
    return [str(s) for s in v]


def _size(v) -> tuple[int, int]:
    if isinstance(v, str):
        m = re.match(r"^(\d+)[xX*](\d+)$", v.strip())
        if not m:
            raise RenderConfigError(f"size must look like 1600x1200, got {v!r}")
        return int(m.group(1)), int(m.group(2))
    w, h = v
    return int(w), int(h)
