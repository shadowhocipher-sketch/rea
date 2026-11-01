import copy
import json
from pathlib import Path

import pytest
import yaml

import build_enclosure as be
from hwcad.enclosure import build_enclosure
from tools.measure import interference_matrix

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "generic_box.yaml"


@pytest.fixture(scope="module")
def spec():
    return yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))


def test_example_cli_outputs_and_passes(tmp_path, spec):
    out = tmp_path / "out"
    code = be.main([str(EXAMPLE), "--out", str(out), "--no-slice", "--wall-samples", "400"])
    rep = json.loads((out / "check_report.json").read_text())
    assert code == 0, rep["checks"]
    for n in ("bottom", "top", "cap_btn_a"):
        assert (out / f"{n}.step").stat().st_size > 0 and (out / f"{n}.stl").stat().st_size > 0
    for n in ("assembly.step", "envelopes.step", "preview_assembly.png", "preview_exploded.png", "check_report.md"):
        assert (out / n).exists()
    assert rep["checks"]["interference_zero"] and rep["checks"]["usb_plug_fully_inserts"]
    assert rep["checks"]["fits_printer_bed"]


def test_detects_interference_when_component_too_tall(spec):
    s = copy.deepcopy(spec)
    s["components"][0]["size"][2] = 20.0      # PCB 包络改成 20 mm 高，必然顶到上壳
    res = build_enclosure(s)
    m = interference_matrix({**res.parts, **res.envelopes})
    assert not m["ok"]
    assert any("pcb" in (p["a"], p["b"]) for p in m["pairs"])


def test_front_back_naming_and_param_change(spec):
    s = copy.deepcopy(spec)
    s["shell"]["style"] = "front_back"
    s["shell"]["size"] = [100, 60, 30]
    res = build_enclosure(s)
    assert {"front", "back"} <= set(res.parts)
    assert res.parts["back"].bounding_box().size.X == pytest.approx(100)


def test_bad_spec_exit_code(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("shell: {size: [10, 10]}\n", encoding="utf-8")
    assert be.main([str(bad), "--out", str(tmp_path / "o"), "--no-slice"]) == 2


def test_usb_check_not_applicable_without_ports(tmp_path, spec):
    """没有 USB 口的外壳：插头检查是"不适用"（None），不能报成通过，也不阻断总结论。"""
    s = copy.deepcopy(spec)
    s["usb_c"] = []
    y = tmp_path / "no_usb.yaml"
    y.write_text(yaml.safe_dump(s, allow_unicode=True), encoding="utf-8")
    out = tmp_path / "out"
    code = be.main([str(y), "--out", str(out), "--no-slice", "--no-preview", "--wall-samples", "200"])
    rep = json.loads((out / "check_report.json").read_text())
    assert rep["checks"]["usb_plug_fully_inserts"] is None
    assert "不适用" in (out / "check_report.md").read_text(encoding="utf-8")
    assert code == 0, rep["checks"]
