"""f02: product render is labelled, named and sized correctly, and the part is visible (line F)."""
import numpy as np

from common import weighted

META = {"id": "f02", "line": "F", "title": "渲染图标注、命名、尺寸、可见", "kind": "capability"}
W, H = 480, 360


def produce(ctx):
    import trimesh
    from PIL import Image
    stl = ctx.work / "box.stl"
    trimesh.creation.box(extents=(40, 30, 20),
                         transform=trimesh.transformations.translation_matrix((0, 0, 10))).export(stl)
    out = ctx.work / "r"
    r = ctx.py("render/render.py", "--part", f"{stl}:#C0392B:matte", "--views", "iso", "--size", f"{W}x{H}",
               "--quality", "draft", "--name", "f02", "--out", out, timeout=300)
    ans = {"exit": r.returncode, "file": None}
    p = out / "render_f02_studio_iso.png"
    if not p.exists():
        return ans
    im = Image.open(p)
    ans["file"], ans["size"], ans["label"] = p.name, list(im.size), im.info.get("Label", "")
    a = np.asarray(im.convert("RGB")).astype(int)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    ans["red_fraction"] = float(((R > G + 50) & (R > B + 50)).mean())
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    h, w = lum.shape
    gray_dark = (lum < 120) & (np.abs(R - G) < 30) & (np.abs(G - B) < 30)     # label box, not the red part
    br = gray_dark[int(h * 0.85):, int(w * 0.6):]
    tl = gray_dark[:h - int(h * 0.85), :w - int(w * 0.6)]
    ans["dark_br"], ans["dark_tl"] = float(br.mean()), float(tl.mean())
    return ans


def score(ans):
    lab = ans.get("label") or ""
    return weighted([
        (0.2, ans.get("exit") == 0, f"退出码 {ans.get('exit')}"),
        (0.2, ans.get("file") == "render_f02_studio_iso.png" and ans.get("size") == [W, H],
         f"文件 {ans.get('file')} 尺寸 {ans.get('size')}"),
        (0.2, "渲染图" in lab and "Render" in lab, f"元数据 Label={lab!r}"),
        (0.2, (ans.get("red_fraction") or 0) >= 0.01, f"红色物体像素占比 {ans.get('red_fraction')}"),
        (0.2, (ans.get("dark_br") or 0) >= 0.005 and (ans.get("dark_tl") or 0) < 0.005,
         f"右下角标注深色像素 {ans.get('dark_br')}，左上角 {ans.get('dark_tl')}"),
    ])
