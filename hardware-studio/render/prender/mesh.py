"""Load parts (STL/OBJ/PLY/3MF via trimesh, STEP via build123d) into triangle meshes.

Units are millimetres, Z is up (build123d convention). Front view looks from -Y.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

MESH_SUFFIXES = {".stl", ".obj", ".ply", ".off", ".glb", ".gltf", ".3mf"}
STEP_SUFFIXES = {".step", ".stp"}


class MeshLoadError(RuntimeError):
    pass


@dataclass
class TriMesh:
    """Triangles with per-vertex normals (vertices are split along creases)."""

    vertices: np.ndarray  # (N, 3) float64
    faces: np.ndarray  # (M, 3) int64
    normals: np.ndarray = field(default=None)  # (N, 3) float64

    def __post_init__(self):
        self.vertices = np.asarray(self.vertices, dtype=np.float64).reshape(-1, 3)
        self.faces = np.asarray(self.faces, dtype=np.int64).reshape(-1, 3)
        if self.normals is None:
            self.normals = flat_vertex_normals(self.vertices, self.faces)

    @property
    def bounds(self) -> np.ndarray:
        return np.array([self.vertices.min(axis=0), self.vertices.max(axis=0)])

    def translated(self, offset) -> "TriMesh":
        return TriMesh(self.vertices + np.asarray(offset, float), self.faces.copy(), self.normals.copy())

    def transformed(self, rot: np.ndarray, offset) -> "TriMesh":
        return TriMesh(self.vertices @ rot.T + np.asarray(offset, float), self.faces.copy(), self.normals @ rot.T)


def flat_vertex_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """Area-weighted vertex normals (callers split vertices where creases must stay sharp)."""
    tri = vertices[faces]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    vn = np.zeros_like(vertices)
    for k in range(3):
        np.add.at(vn, faces[:, k], fn)
    norm = np.linalg.norm(vn, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    return vn / norm


def crease_split(vertices: np.ndarray, faces: np.ndarray, angle_deg: float = 30.0) -> TriMesh:
    """Smooth normals across soft edges, keep edges sharper than ``angle_deg`` crisp."""
    import trimesh

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    if len(mesh.faces) == 0:
        raise MeshLoadError("mesh has no triangles")
    try:
        smooth = trimesh.graph.smooth_shade(mesh, angle=np.radians(angle_deg), facet_minarea=None)
        return TriMesh(smooth.vertices, smooth.faces, np.asarray(smooth.vertex_normals))
    except Exception:  # pragma: no cover - fall back to faceted shading
        v = mesh.vertices[mesh.faces].reshape(-1, 3)
        f = np.arange(len(v)).reshape(-1, 3)
        return TriMesh(v, f)


def _load_step(path: Path, tolerance: float) -> tuple[np.ndarray, np.ndarray]:
    try:
        from build123d import import_step
    except ImportError as exc:  # pragma: no cover
        raise MeshLoadError("STEP needs build123d (pip install build123d)") from exc
    shape = import_step(str(path))
    bb = shape.bounding_box()
    size = max(bb.size.X, bb.size.Y, bb.size.Z, 1e-6)
    tol = tolerance if tolerance > 0 else max(size * 5e-4, 0.01)
    verts, tris = shape.tessellate(tol, angular_tolerance=0.15)
    v = np.array([[p.X, p.Y, p.Z] for p in verts], dtype=np.float64)
    f = np.array(tris, dtype=np.int64)
    return v, f


def _load_trimesh(path: Path) -> tuple[np.ndarray, np.ndarray]:
    import trimesh

    loaded = trimesh.load(str(path), force="mesh")
    return np.asarray(loaded.vertices), np.asarray(loaded.faces)


def load_part(path: str | Path, tolerance: float = 0.0, crease_deg: float = 30.0) -> TriMesh:
    path = Path(path)
    if not path.exists():
        raise MeshLoadError(f"part file not found: {path}")
    suffix = path.suffix.lower()
    if suffix in STEP_SUFFIXES:
        v, f = _load_step(path, tolerance)
    elif suffix in MESH_SUFFIXES:
        v, f = _load_trimesh(path)
    else:
        raise MeshLoadError(f"unsupported part format {suffix!r} ({path}); use STL/OBJ/PLY/3MF/STEP")
    if len(f) == 0:
        raise MeshLoadError(f"no triangles in {path}")
    return crease_split(v, f, crease_deg)


def concat(meshes: list[TriMesh]) -> tuple[TriMesh, np.ndarray]:
    """Merge meshes; returns the merged mesh and the source index of each triangle."""
    verts, faces, norms, owner = [], [], [], []
    base = 0
    for i, m in enumerate(meshes):
        verts.append(m.vertices)
        faces.append(m.faces + base)
        norms.append(m.normals)
        owner.append(np.full(len(m.faces), i, dtype=np.int32))
        base += len(m.vertices)
    merged = TriMesh(np.concatenate(verts), np.concatenate(faces), np.concatenate(norms))
    return merged, np.concatenate(owner)


# --- simple primitives (props) -------------------------------------------------

def box(size, center=(0, 0, 0)) -> TriMesh:
    """Axis-aligned box with flat (split) normals."""
    sx, sy, sz = (np.asarray(size, float) / 2)
    cx, cy, cz = center
    quads = []
    for axis in range(3):
        for sign in (-1, 1):
            n = np.zeros(3)
            n[axis] = sign
            u = np.zeros(3)
            u[(axis + 1) % 3] = 1
            w = np.cross(n, u)
            half = np.array([sx, sy, sz])
            c = n * half
            du = u * half
            dw = w * half
            quads.append((c - du - dw, c + du - dw, c + du + dw, c - du + dw, n))
    verts, faces, norms = [], [], []
    for q in quads:
        b = len(verts)
        verts.extend(q[:4])
        norms.extend([q[4]] * 4)
        faces.extend([(b, b + 1, b + 2), (b, b + 2, b + 3)])
    v = np.array(verts) + np.array([cx, cy, cz])
    return TriMesh(v, np.array(faces), np.array(norms))


def prism(radius: float, length: float, sides: int = 6, cap_cone: float = 0.0) -> TriMesh:
    """Prism along +X starting at x=0; optional cone tip of length ``cap_cone``."""
    ang = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    ring = np.stack([np.zeros(sides), np.cos(ang) * radius, np.sin(ang) * radius], axis=1)
    verts, faces, norms = [], [], []
    for i in range(sides):
        j = (i + 1) % sides
        a0, a1 = ring[i], ring[j]
        n = (a0 + a1) / 2
        n = n / np.linalg.norm(n)
        b = len(verts)
        verts += [a0, a1, a1 + [length, 0, 0], a0 + [length, 0, 0]]
        norms += [n] * 4
        faces += [(b, b + 1, b + 2), (b, b + 2, b + 3)]
    # back cap
    b = len(verts)
    verts += [np.zeros(3)] + list(ring)
    norms += [np.array([-1.0, 0, 0])] * (sides + 1)
    faces += [(b, b + 1 + (i + 1) % sides, b + 1 + i) for i in range(sides)]
    if cap_cone > 0:
        tip = np.array([length + cap_cone, 0, 0])
        for i in range(sides):
            j = (i + 1) % sides
            a0 = ring[i] + [length, 0, 0]
            a1 = ring[j] + [length, 0, 0]
            n = np.cross(a1 - a0, tip - a0)
            n = n / np.linalg.norm(n)
            if np.dot(n, (a0 + a1) / 2 - [length, 0, 0]) < 0:
                n = -n
            b = len(verts)
            verts += [a0, a1, tip]
            norms += [n] * 3
            faces.append((b, b + 1, b + 2))
    return TriMesh(np.array(verts), np.array(faces), np.array(norms))
