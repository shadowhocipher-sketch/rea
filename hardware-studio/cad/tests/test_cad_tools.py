import json
from pathlib import Path

import pytest
from build123d import Align, Box, Location, import_step

from hwcad.shell import hollow_box
from tools import export as ex
from tools import measure as me
from tools import preview as pv
from tools import slice_check as sc


def _box(x=0.0, s=10.0):
    return Box(s, s, s, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((x, 0, 0)))


def test_bbox_volume_interference():
    a, b, c = _box(0), _box(5), _box(10)
    assert me.bbox(a)["size"] == [10, 10, 10]
    assert me.volume(a) == pytest.approx(1000)
    assert me.interference_volume(a, b) == pytest.approx(500)
    assert me.interference_volume(a, c) == 0.0           # 只接触
    m = me.interference_matrix({"a": a, "b": b, "c": c})
    assert not m["ok"] and m["total"] == pytest.approx(1000)
    m2 = me.interference_matrix({"a": a, "b": b, "c": c}, ignore=[("a", "b"), ("b", "c")])
    assert m2["ok"]


def test_wall_sampling_finds_wall_and_thin_spot():
    shell = hollow_box(40, 30, 20, wall=2.0, corner_radius=4, edge_radius=0)
    r = me.min_wall_report(shell, min_wall=1.2, samples=800)
    assert r["median"] == pytest.approx(2.0, abs=0.02)
    assert r["fraction_below"] < 0.02
    thin = me.min_wall_report(hollow_box(40, 30, 20, wall=0.8, corner_radius=4, edge_radius=0), 1.2, samples=400)
    assert thin["fraction_below"] > 0.9


def test_fits_bed():
    assert me.fits_bed(_box(s=100), (250, 210, 220))["ok"]
    assert not me.fits_bed(_box(s=230), (250, 210, 220))["ok"]


def test_export_roundtrip_and_cli(tmp_path):
    files = ex.export_parts({"a": _box(0), "b": _box(20)}, tmp_path)
    for name in ("a", "b"):
        for f in files[name]:
            assert Path(f).stat().st_size > 0
    assert (tmp_path / "assembly.step").exists()
    back = import_step(str(tmp_path / "a.step"))
    assert me.volume(back) == pytest.approx(1000, rel=1e-6)
    out = tmp_path / "m.json"
    assert me.main([str(tmp_path / "a.step"), str(tmp_path / "b.step"), "--min-wall", "1", "--samples", "200",
                    "--json", str(out)]) == 0
    data = json.loads(out.read_text())
    assert data["interference"]["ok"] and data["parts"]["a"]["volume"] == pytest.approx(1000)
    assert me.main([str(tmp_path / "a.stl"), "--min-wall", "1", "--samples", "100"]) == 0


def test_preview_png(tmp_path):
    p = pv.preview_png({"a": _box(0), "b": _box(20)}, tmp_path / "p.png", views=("iso", "top"), explode=5,
                       explode_names=("b",))
    from PIL import Image

    im = Image.open(p)
    assert im.size[0] > 300 and im.size[1] > 200


def test_slice_check_missing_slicer_is_clear(tmp_path):
    r = sc.slice_check(tmp_path / "none.stl", slicer="/nonexistent/prusa-slicer")
    assert r["available"] is False and "prusa-slicer" in r["error"]


def test_parse_gcode_summary():
    txt = "; filament used [mm] = 779.82\n; filament used [cm3] = 1.88\n; estimated printing time (normal mode) = 1h 2m 3s\n"
    s = sc.parse_gcode_summary(txt)
    assert s["filament_mm"] == pytest.approx(779.82) and s["time_s"] == 3723


@pytest.mark.skipif(sc.find_slicer() is None, reason="未安装 PrusaSlicer 命令行")
def test_slice_real(tmp_path):
    ex.export_part(_box(s=20), tmp_path / "c.stl")
    r = sc.slice_check(tmp_path / "c.stl")
    assert r["ok"] and r["filament_mm"] > 0 and r["time_s"] > 0 and r["filament_g_est"] > 0
