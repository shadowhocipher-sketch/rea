"""Deferred shading on top of ``raster.py``: camera, soft shadows, sky light, floor/desk.

Everything here is plain numpy. Lighting model (deliberately simple, "studio" look):

* key light: directional, soft shadow map with Poisson PCF;
* sky light: ``n_sky`` directional shadow maps over the upper hemisphere, which
  gives soft ambient occlusion and contact shadows on the floor/desk;
* fill and rim lights without shadows;
* Blinn-Phong specular plus a gradient "environment" reflection with Schlick Fresnel;
* simple filmic tone map, sRGB output.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .mesh import TriMesh, concat
from .raster import rasterize

# ---------------------------------------------------------------- colour ----

def parse_color(value) -> np.ndarray:
    """'#RRGGBB', 'RRGGBB', (r,g,b) 0-255 or 0-1 -> sRGB floats 0..1."""
    if isinstance(value, str):
        s = value.strip().lstrip("#")
        if len(s) == 3:
            s = "".join(c * 2 for c in s)
        if len(s) != 6 or any(c not in "0123456789abcdefABCDEF" for c in s):
            raise ValueError(f"bad colour {value!r}; use #RRGGBB")
        return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0
    arr = np.asarray(value, float)
    if arr.shape != (3,):
        raise ValueError(f"bad colour {value!r}")
    return arr / 255.0 if arr.max() > 1.0 else arr


def srgb_to_linear(c):
    c = np.asarray(c, np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def tonemap(x):
    """Narkowicz ACES fit, mild."""
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)


# -------------------------------------------------------------- materials ---

MATERIALS = {
    # spec: specular strength, power: Blinn exponent, env: reflection strength, f0: Fresnel base
    "matte": dict(spec=0.10, power=12, env=0.05, f0=0.03, metal=False),
    "satin": dict(spec=0.30, power=40, env=0.18, f0=0.04, metal=False),
    "gloss": dict(spec=0.70, power=160, env=0.45, f0=0.05, metal=False),
    "rubber": dict(spec=0.05, power=6, env=0.02, f0=0.02, metal=False),
    "metal": dict(spec=0.90, power=80, env=0.85, f0=0.6, metal=True),
    "glass": dict(spec=1.00, power=300, env=0.80, f0=0.06, metal=False),  # dark screen glass
    "paper": dict(spec=0.02, power=4, env=0.0, f0=0.02, metal=False),
}


@dataclass
class SceneObject:
    mesh: TriMesh
    color: np.ndarray  # sRGB 0..1
    material: str = "satin"
    role: str = "part"  # part | prop
    name: str = ""


# ----------------------------------------------------------------- camera ---

@dataclass
class Camera:
    eye: np.ndarray
    target: np.ndarray
    width: int
    height: int
    fov_y_deg: float = 28.0
    up: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 1.0]))

    def __post_init__(self):
        self.eye = np.asarray(self.eye, float)
        self.target = np.asarray(self.target, float)
        f = self.target - self.eye
        f /= np.linalg.norm(f)
        up = np.asarray(self.up, float)
        if abs(np.dot(f, up)) > 0.995:
            up = np.array([0.0, 1.0, 0.0])
        r = np.cross(f, up)
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.f, self.r, self.u = f, r, u
        self.fpx = (self.height / 2) / np.tan(np.radians(self.fov_y_deg) / 2)

    def to_view(self, P):
        d = P - self.eye
        return d @ self.r, d @ self.u, d @ self.f

    def project(self, P):
        x, y, z = self.to_view(P)
        zs = np.where(z > 1e-6, z, 1e-6)
        sx = self.width / 2 + x / zs * self.fpx
        sy = self.height / 2 - y / zs * self.fpx
        return sx, sy, z

    def pixel_rays(self):
        """Unnormalised ray directions with unit forward component, (H*W, 3)."""
        xs = (np.arange(self.width) + 0.5 - self.width / 2) / self.fpx
        ys = (self.height / 2 - (np.arange(self.height) + 0.5)) / self.fpx
        a, b = np.meshgrid(xs, ys)
        D = self.f[None, :] + a.reshape(-1, 1) * self.r[None, :] + b.reshape(-1, 1) * self.u[None, :]
        return D.astype(np.float32)


def view_direction(az_deg: float, el_deg: float) -> np.ndarray:
    """Unit vector from target to camera. az=0 is the front (-Y), az=90 the right (+X)."""
    az, el = np.radians(az_deg), np.radians(el_deg)
    return np.array([np.sin(az) * np.cos(el), -np.cos(az) * np.cos(el), np.sin(el)])


def fit_camera(points: np.ndarray, az: float, el: float, width: int, height: int,
               fill: float = 0.8, fov_y: float = 28.0, offset=(0.0, 0.0)) -> Camera:
    """Place the camera so ``points`` fill ``fill`` of the frame; ``offset`` shifts the
    subject in the frame (fractions of half-width/half-height, +x right, +y up)."""
    center = (points.min(0) + points.max(0)) / 2
    radius = max(np.linalg.norm(points - center, axis=1).max(), 1e-3)
    vd = view_direction(az, el)
    target = center.copy()
    tan_y = np.tan(np.radians(fov_y) / 2)
    tan_x = tan_y * width / height
    dist = radius / np.sin(np.radians(fov_y) / 2)
    for _ in range(4):
        cam = Camera(target + vd * dist, target, width, height, fov_y)
        x, y, z = cam.to_view(points)
        a, b = x / z, y / z
        # recentre
        ca, cb = (a.min() + a.max()) / 2, (b.min() + b.max()) / 2
        target = target + cam.r * ca * dist + cam.u * cb * dist
        # rescale distance: half-extent in tangent space should equal fill * tan
        need = max((a.max() - a.min()) / 2 / (tan_x * fill), (b.max() - b.min()) / 2 / (tan_y * fill))
        dist = dist * need if need > 0 else dist
        dist = max(dist, radius * 1.05)
    cam = Camera(target + vd * dist, target, width, height, fov_y)
    if offset != (0.0, 0.0):
        sh = cam.r * (-offset[0] * tan_x * dist) + cam.u * (-offset[1] * tan_y * dist)
        cam = Camera(cam.eye + sh, cam.target + sh, width, height, fov_y)
    return cam


# ------------------------------------------------------------ shadow maps ---

class ShadowMap:
    """Orthographic depth map looking along ``-to_light``."""

    def __init__(self, mesh: TriMesh, to_light, res: int, margin: float = 0.02):
        L = np.asarray(to_light, float)
        L /= np.linalg.norm(L)
        f = -L
        helper = np.array([0.0, 0.0, 1.0]) if abs(f[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
        r = np.cross(f, helper)
        r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.f, self.r, self.u = f, r, u
        V = mesh.vertices
        a, b, d = V @ r, V @ u, V @ f
        span = max(a.max() - a.min(), b.max() - b.min()) * (1 + 2 * margin) + 1e-6
        self.a0 = (a.min() + a.max()) / 2 - span / 2
        self.b1 = (b.min() + b.max()) / 2 + span / 2
        self.texel = span / res
        self.res = res
        sx = (a - self.a0) / self.texel
        sy = (self.b1 - b) / self.texel
        ras = rasterize(sx, sy, -d, mesh.faces, res, res)
        depth = -ras.q  # +inf where empty
        self.depth = depth.reshape(res, res).astype(np.float32)

    def visibility(self, P: np.ndarray, N: np.ndarray, taps: np.ndarray, radius: float,
                   bias: float) -> np.ndarray:
        """Fraction of PCF taps lit. P, N: (n,3) float32; taps: (k,2) unit-disc offsets."""
        # slope-scaled bias: surfaces at grazing angles to the light need more offset
        cos_t = np.clip(-(N @ self.f.astype(np.float32)), 0.05, 1.0)
        slope = np.minimum(np.sqrt(1 - cos_t * cos_t) / cos_t, 6.0)
        Pn = P + N * (bias * 2.0)
        a = Pn @ self.r.astype(np.float32)
        b = Pn @ self.u.astype(np.float32)
        d = Pn @ self.f.astype(np.float32) - bias * slope
        res = self.res
        lit = np.zeros(len(P), np.float32)
        for ox, oy in taps:
            ix = ((a + ox * radius - self.a0) / self.texel).astype(np.int32)
            iy = ((self.b1 - (b + oy * radius)) / self.texel).astype(np.int32)
            inside = (ix >= 0) & (ix < res) & (iy >= 0) & (iy < res)
            occ = np.full(len(P), np.inf, np.float32)
            occ[inside] = self.depth[iy[inside], ix[inside]]
            lit += (d <= occ + bias).astype(np.float32)
        return lit / len(taps)


def poisson_disc(n: int, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    pts = []
    while len(pts) < n:
        p = rng.uniform(-1, 1, 2)
        if p @ p <= 1 and all(np.linalg.norm(p - q) > 0.9 / np.sqrt(n) for q in pts):
            pts.append(p)
    return np.array(pts, np.float32)


def hemisphere_dirs(n: int, min_z: float = 0.12) -> np.ndarray:
    """Fibonacci directions over the upper hemisphere (z >= min_z)."""
    i = np.arange(n) + 0.5
    z = min_z + (1 - min_z) * (1 - i / n)
    phi = i * np.pi * (3 - np.sqrt(5))
    s = np.sqrt(1 - z * z)
    return np.stack([s * np.cos(phi), s * np.sin(phi), z], axis=1)


# ------------------------------------------------------------------ scene ---

@dataclass
class Ground:
    """Floor at ``z``. kind 'studio' = seamless shadow catcher, 'desk' = finite tabletop."""

    kind: str = "studio"  # studio | desk | none
    z: float = 0.0
    color: np.ndarray | None = None  # desk albedo (sRGB)
    back_edge: float = 300.0  # desk: distance behind the subject (camera-yaw frame)
    grain_scale: float = 6.0  # desk wood grain period (mm)
    center: np.ndarray | None = None


@dataclass
class Lighting:
    key_rel_az: float = -42.0  # degrees relative to camera azimuth (negative = camera left)
    key_el: float = 52.0
    key: float = 2.0
    fill: float = 0.25
    rim: float = 0.4
    sky: float = 0.8
    exposure: float = 0.62
    sky_dirs: int = 24
    sky_res: int = 384
    key_res: int = 2048
    softness: float = 0.012  # PCF radius as fraction of scene size
    key_color: tuple = (1.0, 0.97, 0.92)
    sky_color: tuple = (0.92, 0.95, 1.0)
    ground_color: tuple = (0.55, 0.50, 0.45)


@dataclass
class Background:
    top: np.ndarray  # sRGB
    bottom: np.ndarray


def _bg_image(bg: Background, W: int, H: int) -> np.ndarray:
    t = (np.arange(H, dtype=np.float32) / max(H - 1, 1))[:, None, None]
    top = srgb_to_linear(bg.top)[None, None, :]
    bot = srgb_to_linear(bg.bottom)[None, None, :]
    img = top * (1 - t) + bot * t
    return np.broadcast_to(img, (H, W, 3)).reshape(-1, 3).astype(np.float32)


def _wood(lx, ly, scale):
    """Subtle procedural grain along the desk's local x axis."""
    g = (np.sin(2 * np.pi * (ly / scale + 0.35 * np.sin(2 * np.pi * lx / (scale * 23.0))
                             + 0.15 * np.sin(2 * np.pi * lx / (scale * 7.3) + ly / (scale * 3.1))))
         + 0.35 * np.sin(2 * np.pi * (ly / (scale * 0.61) + 0.2 * np.sin(lx / (scale * 4.0)))))
    return 1.0 + 0.03 * g.astype(np.float32)


@dataclass
class RenderResult:
    image: np.ndarray  # (H, W, 3) linear float32 (before tone map)
    depth: np.ndarray  # (H, W) view depth, inf for background
    subject_mask: np.ndarray  # (H, W) bool, pixels showing parts


def render(objects: list[SceneObject], cam: Camera, ground: Ground, bg: Background,
           light: Lighting = Lighting()) -> RenderResult:
    W, H = cam.width, cam.height
    mesh, owner = concat([o.mesh for o in objects])
    n_tri = len(mesh.faces)
    V = mesh.vertices
    scene_lo, scene_hi = V.min(0), V.max(0)
    parts_v = np.concatenate([o.mesh.vertices for o in objects if o.role == "part"])
    size = float(np.linalg.norm(parts_v.max(0) - parts_v.min(0)))

    # --- primary visibility
    sx, sy, z = cam.project(V)
    valid = (z[mesh.faces] > size * 1e-3).all(axis=1)
    ras = rasterize(sx, sy, 1.0 / np.maximum(z, 1e-9), mesh.faces, W, H, valid)

    rays = cam.pixel_rays()
    obj_t = np.where(ras.covered, 1.0 / np.where(ras.covered, ras.q, 1.0), np.inf).astype(np.float32)

    # --- ground hit (analytic plane)
    gnd_t = np.full(W * H, np.inf, np.float32)
    if ground.kind != "none":
        dz = rays[:, 2]
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (ground.z - cam.eye[2]) / dz
        hit = (t > 0) & np.isfinite(t)
        if ground.kind == "desk":
            P = cam.eye[None, :] + rays * t[:, None]
            fh = np.array([cam.f[0], cam.f[1], 0.0])
            fh /= max(np.linalg.norm(fh), 1e-9)
            c = ground.center if ground.center is not None else cam.target
            ly = (P - c) @ fh
            hit &= ly < ground.back_edge
        gnd_t[hit] = t[hit]

    is_obj = ras.covered & (obj_t <= gnd_t)
    is_gnd = np.isfinite(gnd_t) & ~is_obj
    depth = np.where(is_obj, obj_t, gnd_t)

    img = _bg_image(bg, W, H)

    # --- lights (camera relative so every view is lit pleasantly)
    cam_az = np.degrees(np.arctan2(cam.eye[0] - cam.target[0], -(cam.eye[1] - cam.target[1])))
    key_dir = view_direction(cam_az + light.key_rel_az, light.key_el)
    fill_dir = view_direction(cam_az + 70.0, 18.0)
    rim_dir = view_direction(cam_az + 160.0, 35.0)

    key_map = ShadowMap(mesh, key_dir, light.key_res)
    sky_dirs = hemisphere_dirs(light.sky_dirs)
    sky_maps = [ShadowMap(mesh, d, light.sky_res) for d in sky_dirs]
    taps = poisson_disc(12)
    soft = light.softness * max(size, 1e-3)
    key_bias = key_map.texel * 1.5
    keyc = np.array(light.key_color, np.float32)
    skyc = np.array(light.sky_color, np.float32)
    gndc = np.array(light.ground_color, np.float32)

    def sky_vis(P, N):
        acc = np.zeros(len(P), np.float32)
        wsum = np.zeros(len(P), np.float32)
        for d, m in zip(sky_dirs, sky_maps):
            w = np.maximum(N @ d.astype(np.float32), 0.0)
            on = w > 0
            if not on.any():
                continue
            v = np.ones(len(P), np.float32)
            v[on] = m.visibility(P[on], N[on], taps[:1], 0.0, m.texel * 2.0)
            acc += w * v
            wsum += w
        return np.where(wsum > 0, acc / np.maximum(wsum, 1e-6), 1.0), wsum / (0.5 * len(sky_dirs))

    # --- shade objects
    idx = np.nonzero(is_obj)[0]
    if idx.size:
        tid = ras.tri[idx]
        f = mesh.faces[tid]
        b1 = ras.b1[idx]
        b2 = ras.b2[idx]
        b0 = 1 - b1 - b2
        # perspective-correct weights
        iz = 1.0 / np.maximum(z[f], 1e-9)
        w0, w1, w2 = b0 * iz[:, 0], b1 * iz[:, 1], b2 * iz[:, 2]
        ws = w0 + w1 + w2
        w0, w1, w2 = w0 / ws, w1 / ws, w2 / ws
        P = (V[f[:, 0]] * w0[:, None] + V[f[:, 1]] * w1[:, None] + V[f[:, 2]] * w2[:, None]).astype(np.float32)
        Nn = (mesh.normals[f[:, 0]] * w0[:, None] + mesh.normals[f[:, 1]] * w1[:, None]
              + mesh.normals[f[:, 2]] * w2[:, None]).astype(np.float32)
        Nn /= np.maximum(np.linalg.norm(Nn, axis=1, keepdims=True), 1e-9)
        Vd = (cam.eye[None, :] - P).astype(np.float32)
        Vd /= np.linalg.norm(Vd, axis=1, keepdims=True)
        flip = np.sum(Nn * Vd, axis=1) < 0
        Nn[flip] *= -1

        obj = owner[tid]
        albedo = np.stack([srgb_to_linear(o.color) for o in objects]).astype(np.float32)[obj]
        mats = [MATERIALS.get(o.material, MATERIALS["satin"]) for o in objects]
        spec = np.array([m["spec"] for m in mats], np.float32)[obj]
        power = np.array([m["power"] for m in mats], np.float32)[obj]
        envk = np.array([m["env"] for m in mats], np.float32)[obj]
        f0 = np.array([m["f0"] for m in mats], np.float32)[obj]
        metal = np.array([m["metal"] for m in mats], bool)[obj]

        kd = key_dir.astype(np.float32)
        ndl = np.maximum(Nn @ kd, 0)
        shadow = key_map.visibility(P, Nn, taps, soft, key_bias)
        sv, _ = sky_vis(P, Nn)
        nz = Nn[:, 2]
        hemi = skyc[None, :] * (0.5 + 0.5 * nz)[:, None] + gndc[None, :] * (0.5 - 0.5 * nz)[:, None] * 0.6
        ndf = np.maximum(Nn @ fill_dir.astype(np.float32), 0)
        ndr = np.maximum(Nn @ rim_dir.astype(np.float32), 0)
        ndv = np.clip(np.sum(Nn * Vd, axis=1), 0, 1)

        diffuse = (keyc[None, :] * (light.key * ndl * shadow)[:, None]
                   + hemi * (light.sky * sv)[:, None]
                   + (light.fill * ndf)[:, None]
                   + (light.rim * ndr * (1 - ndv) ** 1.5)[:, None])
        Hh = kd[None, :] + Vd
        Hh /= np.maximum(np.linalg.norm(Hh, axis=1, keepdims=True), 1e-9)
        ndh = np.maximum(np.sum(Nn * Hh, axis=1), 0)
        fres = f0 + (1 - f0) * (1 - ndv) ** 5
        spec_term = spec * ndh ** power * (power + 8) / 50.0 * shadow * ndl * light.key
        R = 2 * ndv[:, None] * Nn - Vd
        env = (skyc[None, :] * np.clip(0.4 + 0.8 * R[:, 2:3], 0, 1.2)
               + gndc[None, :] * np.clip(-R[:, 2:3], 0, 1) * 0.5)
        env_term = env * (envk * fres * (0.35 + 0.65 * sv))[:, None]
        spec_col = np.where(metal[:, None], albedo, 1.0)
        diff_col = np.where(metal[:, None], albedo * 0.15, albedo)
        img[idx] = (diff_col * diffuse + spec_col * (spec_term[:, None] * keyc[None, :] + env_term)) * light.exposure

    # --- shade ground
    gidx = np.nonzero(is_gnd)[0]
    if gidx.size:
        P = (cam.eye[None, :] + rays[gidx] * gnd_t[gidx, None]).astype(np.float32)
        N = np.broadcast_to(np.array([0, 0, 1], np.float32), P.shape).copy()
        # only points near the scene can be shadowed; skip the rest for speed
        pad = size * 1.5
        near = ((P[:, 0] > scene_lo[0] - pad) & (P[:, 0] < scene_hi[0] + pad)
                & (P[:, 1] > scene_lo[1] - pad) & (P[:, 1] < scene_hi[1] + pad))
        shadow = np.ones(len(P), np.float32)
        sv = np.ones(len(P), np.float32)
        if near.any():
            shadow[near] = key_map.visibility(P[near], N[near], taps, soft * 1.6, key_bias)
            sv[near] = sky_vis(P[near], N[near])[0]
        ndl = max(key_dir[2], 0.0)
        lit_full = light.key * ndl + light.sky
        lit = light.key * ndl * shadow + light.sky * sv
        if ground.kind == "studio":
            # shadow catcher: unoccluded floor equals the background colour exactly
            img[gidx] = img[gidx] * (lit / lit_full)[:, None] ** 1.5
        else:
            fh = np.array([cam.f[0], cam.f[1], 0.0])
            fh /= max(np.linalg.norm(fh), 1e-9)
            rh = np.array([fh[1], -fh[0], 0.0])
            c = ground.center if ground.center is not None else cam.target
            lx = (P - c) @ rh.astype(np.float32)
            ly = (P - c) @ fh.astype(np.float32)
            alb = srgb_to_linear(ground.color)[None, :] * _wood(lx, ly, ground.grain_scale)[:, None]
            col = alb * (keyc[None, :] * (light.key * ndl * shadow)[:, None]
                         + skyc[None, :] * (light.sky * sv)[:, None])
            # gentle sheen toward the back of the desk
            Vd = cam.eye[None, :] - P
            Vd /= np.linalg.norm(Vd, axis=1, keepdims=True)
            fres = 0.03 + 0.97 * (1 - np.clip(Vd[:, 2], 0, 1)) ** 5
            col = col + (skyc[None, :] * (0.35 * fres * sv)[:, None])
            img[gidx] = col * light.exposure

    subject = is_obj.copy()
    if idx.size:
        roles = np.array([o.role == "part" for o in objects])
        subject[idx] = roles[owner[ras.tri[idx]]]
    return RenderResult(img.reshape(H, W, 3), depth.reshape(H, W), subject.reshape(H, W))
