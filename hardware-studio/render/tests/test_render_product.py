import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from prender import (MeshLoadError, PartSpec, RenderConfigError, RenderJob, load_job, load_part,
                     render_product)
from prender import label as label_mod

RENDER_PY = Path(__file__).resolve().parents[1] / "render.py"
SIZE = (320, 240)


def _parts(m):
    return [PartSpec(str(m["body"]), "#EFE9DF", "satin"),
            PartSpec(str(m["screen"]), "#1E2228", "glass", (0, -15, 0)),
            PartSpec(str(m["knob_step"]), "#C9A27C", "matte", (0, 0, 20))]


@pytest.fixture(scope="module")
def desk_run(test_model, tmp_path_factory):
    out = tmp_path_factory.mktemp("desk")
    job = RenderJob(parts=_parts(test_model), out=str(out), name="t", views=["front", "side", "back", "iso"],
                    scene="desk", props=["book", "pencil"], size=SIZE, quality="draft",
                    exploded=True, exploded_views=["iso"])
    return render_product(job, log=None)


def _assert_labelled(path, info):
    img = Image.open(path)
    assert img.size == SIZE or info.box[2] <= img.size[0]
    assert "Render" in img.text["Label"]
    x0, y0, x1, y1 = info.box
    W, H = img.size
    assert x1 > W * 0.6 and y1 > H * 0.6  # bottom-right corner
    a = np.asarray(img.convert("L"), np.float32)[y0:y1, x0:x1]
    assert a.mean() < 120  # dark badge
    assert (a > 200).sum() > 10  # light text on it


def test_files_names_sizes_and_labels(desk_run):
    names = [Path(r.path).name for r in desk_run]
    assert names == ["render_t_desk_front.png", "render_t_desk_side.png", "render_t_desk_back.png",
                     "render_t_desk_iso.png", "render_t_desk_iso-exploded.png", "render_t_desk_sheet.png"]
    for r in desk_run:
        assert Path(r.path).exists() and Path(r.path).name.startswith("render_")
        if r.view != "sheet":
            assert Image.open(r.path).size == SIZE
        _assert_labelled(r.path, r.label)


def test_label_is_bilingual_when_cjk_font_present(desk_run):
    from prender.fonts import find_cjk_font

    if find_cjk_font() is None:
        pytest.skip("no CJK font installed (fonts-noto-cjk)")
    for r in desk_run:
        assert r.label.text == "渲染图 / Render" and r.label.cjk
        assert Image.open(r.path).text["Label"] == "渲染图 / Render"


def test_views_differ_and_show_subject(desk_run):
    imgs = {r.view + ("-x" if r.exploded else ""): np.asarray(Image.open(r.path), np.float32)
            for r in desk_run if r.view != "sheet"}
    assert np.abs(imgs["front"] - imgs["back"]).mean() > 2
    assert np.abs(imgs["iso"] - imgs["iso-x"]).mean() > 1
    for a in imgs.values():
        assert a.std() > 10  # not a blank frame


def test_studio_subject_centred(test_model, tmp_path):
    job = RenderJob(parts=_parts(test_model)[:1], out=str(tmp_path), name="s", views=["iso"],
                    size=SIZE, quality="draft", sheet=False)
    (r,) = render_product(job, log=None)
    a = np.asarray(Image.open(r.path).convert("L"), np.float32)
    bg = np.median(a[:5, :])
    ys, xs = np.nonzero(np.abs(a - bg) > 25)
    # subject (ignoring the label badge) stays off the frame edges
    keep = ~((xs > r.label.box[0] - 2) & (ys > r.label.box[1] - 2))
    xs, ys = xs[keep], ys[keep]
    assert xs.min() > 5 and xs.max() < SIZE[0] - 5 and ys.min() > 5


def test_step_and_stl_load(test_model):
    step = load_part(test_model["knob_step"])
    stl = load_part(test_model["knob"])
    assert np.allclose(step.bounds, stl.bounds, atol=0.3)


def test_yaml_job_and_cli_json(test_model, tmp_path):
    cfg = tmp_path / "scene.yaml"
    cfg.write_text(
        "name: yml\nscene: studio\nviews: [front]\nsize: 200x150\nquality: draft\nsheet: false\n"
        f"out: out\nparts:\n  - path: {test_model['body']}\n    color: '#EFE9DF'\n"
        f"  - {test_model['knob']}:#C9A27C:matte:0,0,20\n", encoding="utf-8")
    job = load_job(cfg)
    assert job.parts[1].explode == (0, 0, 20) and Path(job.out) == tmp_path / "out"
    r = subprocess.run([sys.executable, str(RENDER_PY), "--config", str(cfg), "--views", "front,iso",
                        "--json"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert [Path(d["path"]).name for d in data] == ["render_yml_studio_front.png", "render_yml_studio_iso.png"]
    assert all(tuple(d["size"]) == (200, 150) for d in data)


def test_cli_part_specs(test_model, tmp_path):
    r = subprocess.run([sys.executable, str(RENDER_PY), "--part", f"{test_model['body']}:#EFE9DF",
                        "--part", f"{test_model['knob_step']}:#C9A27C:matte", "--views", "iso",
                        "--scene", "plain", "--size", "160x120", "--quality", "draft", "--out", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "render_product_plain_iso.png").exists()


@pytest.mark.parametrize("args,msg", [
    (["--part", "missing.stl"], "not found"),
    (["--part", "x.stl:#zzz"], "colour"),
    (["--part", "x.stl:#ffffff:velvet"], "material"),
    (["--part", "x.stl", "--views", "diagonal"], "view"),
])
def test_cli_errors(args, msg, tmp_path):
    r = subprocess.run([sys.executable, str(RENDER_PY), *args, "--out", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 2 and msg in r.stderr


def test_empty_label_rejected(test_model):
    with pytest.raises(RenderConfigError):
        RenderJob(parts=_parts(test_model), label="  ").validate()


def test_exploded_needs_offsets(test_model, tmp_path):
    job = RenderJob(parts=_parts(test_model)[:1], out=str(tmp_path), exploded=True, size=SIZE, quality="draft")
    with pytest.raises(RenderConfigError, match="explode"):
        render_product(job, log=None)


def test_missing_mesh_raises(tmp_path):
    with pytest.raises(MeshLoadError):
        load_part(tmp_path / "nope.stl")


def test_label_fallback_without_cjk_font(monkeypatch):
    monkeypatch.setattr(label_mod, "find_cjk_font", lambda: None)
    img = Image.new("RGB", (300, 200), (240, 240, 240))
    info = label_mod.draw_label(img)
    assert info.text == "Render" and not info.cjk
    x0, y0, x1, y1 = info.box
    assert np.asarray(img.convert("L"))[y0:y1, x0:x1].mean() < 120
