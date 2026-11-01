"""A small vectorised z-buffer triangle rasteriser written with numpy.

It is our own code (no third-party renderer) so the render tool carries no
GPL/LGPL obligations and runs headless without OpenGL, EGL or OSMesa.

``rasterize`` takes screen-space vertex positions and a per-vertex ``q`` value
that is linear in screen space where *larger means closer* (``1/z`` for a
perspective camera, ``-depth`` for an orthographic one). It returns per-pixel
``q``, the triangle id and screen-space barycentric weights (b1, b2).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

_BUCKETS = (2, 4, 8, 16, 32, 64)
_MAX_FRAGS = 4_000_000


@dataclass
class Raster:
    width: int
    height: int
    q: np.ndarray  # (H*W,) float64, -inf where empty
    tri: np.ndarray  # (H*W,) int32, -1 where empty
    b1: np.ndarray  # (H*W,) float32
    b2: np.ndarray  # (H*W,) float32

    @property
    def covered(self) -> np.ndarray:
        return self.tri >= 0


def _write(r: Raster, pix, q, tid, b1, b2):
    if pix.size == 0:
        return
    np.maximum.at(r.q, pix, q)
    win = q >= r.q[pix]
    pix = pix[win]
    r.tri[pix] = tid[win]
    r.b1[pix] = b1[win]
    r.b2[pix] = b2[win]


def _frags(x, y, q, ids, x0, y0, kx, ky, W, H):
    """Fragments for triangles (arrays (n,3)) over a (ky, kx) pixel window at (x0, y0)."""
    n = len(ids)
    gx = x0[:, None, None] + np.arange(kx)[None, None, :] + 0.5
    gy = y0[:, None, None] + np.arange(ky)[None, :, None] + 0.5
    gx = np.broadcast_to(gx, (n, ky, kx))
    gy = np.broadcast_to(gy, (n, ky, kx))
    ax, ay = x[:, 0, None, None], y[:, 0, None, None]
    bx, by = x[:, 1, None, None], y[:, 1, None, None]
    cx, cy = x[:, 2, None, None], y[:, 2, None, None]
    area = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
    w1 = ((gx - ax) * (cy - ay) - (cx - ax) * (gy - ay)) / area
    w2 = ((bx - ax) * (gy - ay) - (gx - ax) * (by - ay)) / area
    w0 = 1.0 - w1 - w2
    eps = -1e-7
    inside = (w0 >= eps) & (w1 >= eps) & (w2 >= eps) & (gx < W) & (gy < H) & (gx >= 0) & (gy >= 0)
    if not inside.any():
        return None
    qq = w0 * q[:, 0, None, None] + w1 * q[:, 1, None, None] + w2 * q[:, 2, None, None]
    tid = np.broadcast_to(ids[:, None, None], inside.shape)
    pix = (gy.astype(np.int64)) * W + gx.astype(np.int64)
    return pix[inside], qq[inside], tid[inside], w1[inside].astype(np.float32), w2[inside].astype(np.float32)


def rasterize(sx: np.ndarray, sy: np.ndarray, q: np.ndarray, faces: np.ndarray, W: int, H: int,
              valid: np.ndarray | None = None) -> Raster:
    """Rasterise triangles. ``valid`` (per-triangle bool) drops e.g. triangles behind the camera."""
    r = Raster(W, H, np.full(W * H, -np.inf), np.full(W * H, -1, np.int32),
               np.zeros(W * H, np.float32), np.zeros(W * H, np.float32))
    if len(faces) == 0:
        return r
    X = sx[faces]
    Y = sy[faces]
    Q = q[faces]
    ids = np.arange(len(faces), dtype=np.int32)
    area = (X[:, 1] - X[:, 0]) * (Y[:, 2] - Y[:, 0]) - (X[:, 2] - X[:, 0]) * (Y[:, 1] - Y[:, 0])
    keep = np.abs(area) > 1e-12
    if valid is not None:
        keep &= valid
    xmin = np.clip(np.floor(X.min(1)), 0, W)
    xmax = np.clip(np.ceil(X.max(1)), 0, W)
    ymin = np.clip(np.floor(Y.min(1)), 0, H)
    ymax = np.clip(np.ceil(Y.max(1)), 0, H)
    keep &= (xmax > xmin) & (ymax > ymin)
    ext = np.maximum(xmax - xmin, ymax - ymin)
    done = ~keep
    for k in _BUCKETS:
        sel = np.nonzero(~done & (ext <= k))[0]
        done[sel] = True
        chunk = max(1, _MAX_FRAGS // (k * k))
        for s in range(0, len(sel), chunk):
            t = sel[s:s + chunk]
            out = _frags(X[t], Y[t], Q[t], ids[t], xmin[t], ymin[t], k, k, W, H)
            if out is not None:
                _write(r, *out)
    # Large triangles one at a time, tiled so memory stays bounded.
    for t in np.nonzero(~done)[0]:
        x0, x1, y0, y1 = int(xmin[t]), int(xmax[t]), int(ymin[t]), int(ymax[t])
        tile = 512
        for ty in range(y0, y1, tile):
            for tx in range(x0, x1, tile):
                kx = min(tile, x1 - tx)
                ky = min(tile, y1 - ty)
                out = _frags(X[t:t + 1], Y[t:t + 1], Q[t:t + 1], ids[t:t + 1],
                             np.array([tx], float), np.array([ty], float), kx, ky, W, H)
                if out is not None:
                    _write(r, *out)
    return r
