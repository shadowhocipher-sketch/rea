"""b01: enclosure with USB-C + battery bay: zero interference, plug inserts, independent probes (line B)."""
import json
from pathlib import Path

import numpy as np

from common import task_dir, weighted

META = {"id": "b01", "line": "B", "title": "USB-C + 电池仓外壳：干涉 0、插头插到底", "kind": "capability"}
HERE = task_dir(__file__)

# Answer key, derived by hand from enclosure.yaml (not from the tool):
SIZE = (70.0, 45.0, 22.0)
WALL = 2.7
USB_V = 13.93                    # receptacle centre height
PLUG_SHELL = (8.3, 2.5)          # USB-C plug metal shell cross-section W x H (mm), probe size
BATTERY = {"x": 4.0, "y": 0.0, "cell": (40.0, 30.0, 6.0), "swell": 0.10}


def _grid(lo, hi, n):
    axes = [np.linspace(a, b, k) for a, b, k in zip(lo, hi, n)]
    return np.array(np.meshgrid(*axes, indexing="ij")).reshape(3, -1).T


def produce(ctx):
    import trimesh
    out = ctx.work / "b01"
    r = ctx.py("cad/build_enclosure.py", HERE / "enclosure.yaml", "--out", out, "--no-slice", "--no-preview")
    ans = {"exit": r.returncode, "checks": {}, "ok": False}
    rep = out / "check_report.json"
    if not rep.exists():
        ans["stderr"] = r.stderr[-500:]
        return ans
    d = json.loads(rep.read_text(encoding="utf-8"))
    ans["ok"], ans["checks"] = d.get("ok"), d.get("checks", {})
    meshes = [trimesh.load(out / f, force="mesh") for f in ("bottom.stl", "top.stl") if (out / f).exists()]
    if len(meshes) != 2:
        return ans
    allv = np.vstack([m.vertices for m in meshes])
    ans["bbox_size"] = (allv.max(0) - allv.min(0)).round(3).tolist()

    def inside(pts):
        return np.any([m.contains(pts) for m in meshes], axis=0)

    x0 = -SIZE[0] / 2
    w, h = PLUG_SHELL
    usb_pts = _grid((x0 + 0.2, -w / 2, USB_V - h / 2), (x0 + WALL - 0.2, w / 2, USB_V + h / 2), (4, 7, 4))
    ans["usb_probe_blocked"] = int(inside(usb_pts).sum())
    ans["usb_probe_n"] = len(usb_pts)
    ctrl = np.array([[x0 + WALL / 2, 15.0, 6.0], [x0 + WALL / 2, -15.0, 6.0]])
    ans["control_inside"] = bool(inside(ctrl).all())
    L, W, T = BATTERY["cell"]
    t = T * (1 + BATTERY["swell"])
    bx, by = BATTERY["x"], BATTERY["y"]
    bat_pts = _grid((bx - L / 2 + 0.1, by - W / 2 + 0.1, WALL + 0.05), (bx + L / 2 - 0.1, by + W / 2 - 0.1, WALL + t - 0.05),
                    (9, 7, 4))
    ans["battery_probe_blocked"] = int(inside(bat_pts).sum())
    ans["battery_probe_n"] = len(bat_pts)
    return ans


def score(ans):
    c = ans.get("checks") or {}
    size = ans.get("bbox_size")
    size_ok = bool(size) and all(abs(a - b) <= 0.1 for a, b in zip(size, SIZE))
    return weighted([
        (0.3, ans.get("exit") == 0 and bool(ans.get("ok")) and c.get("interference_zero") is True
         and c.get("usb_plug_fully_inserts") is True, f"退出码 {ans.get('exit')}，ok={ans.get('ok')}，"
         f"干涉为 0={c.get('interference_zero')}，插头插到底={c.get('usb_plug_fully_inserts')}"),
        (0.2, size_ok, f"外形 {size}，应为 {list(SIZE)}"),
        (0.2, ans.get("usb_probe_n", 0) > 0 and ans.get("usb_probe_blocked", 1) == 0,
         f"USB 开孔探针被挡 {ans.get('usb_probe_blocked')}/{ans.get('usb_probe_n')}"),
        (0.1, ans.get("control_inside") is True, "对照点在侧壁实体内（探针有效）"),
        (0.2, ans.get("battery_probe_n", 0) > 0 and ans.get("battery_probe_blocked", 1) == 0,
         f"电池仓探针被挡 {ans.get('battery_probe_blocked')}/{ans.get('battery_probe_n')}"),
    ])
