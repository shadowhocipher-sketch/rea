import re
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from gen import random_netlist
from wirediag import (PinsCsvError, build_layout, check, check_files, check_layout, draw_wiring,
                      parse_pins_csv, read_pins_csv)
from wirediag.draw import to_svg

ROOT = Path(__file__).resolve().parents[2]  # hardware-studio/
STANDIN = ROOT / "products" / "desk-creature-standin" / "pins.csv"
COMPLEX = ROOT / "diagrams" / "examples" / "complex" / "pins.csv"


@pytest.fixture(scope="module")
def standin(tmp_path_factory):
    out = tmp_path_factory.mktemp("standin")
    return draw_wiring(STANDIN, out, "desk-creature-standin", subtitle="替身数据 / stand-in data")


@pytest.fixture(scope="module")
def complex_(tmp_path_factory):
    out = tmp_path_factory.mktemp("complex")
    return draw_wiring(COMPLEX, out, "complex-example")


def test_standin_files_and_check(standin):
    svg, png, lay, problems = standin
    assert svg.name == "wiring_desk-creature-standin.svg" and png.name.startswith("wiring_")
    assert svg.exists() and png.exists()
    res = check_files(STANDIN, svg)
    assert res.ok, res.report()
    assert res.expected == res.drawn == len(read_pins_csv(STANDIN))
    assert problems == []
    w, h = Image.open(png).size
    assert (w, h) == (round(lay.width * 2), round(lay.height * 2))


def test_complex_example_is_big_and_clean(complex_):
    svg, png, lay, problems = complex_
    wires = read_pins_csv(COMPLEX)
    assert len(wires) >= 10 and len({p for w in wires for p in (w.from_part, w.to_part)}) >= 6
    assert check_files(COMPLEX, svg).ok
    assert problems == [], problems


def test_colours_by_kind(complex_):
    lay = complex_[2]
    for wg in lay.wires:
        if wg.wire.kind == "ground":
            assert wg.color in ("#111111", "#555555")
        elif wg.wire.kind == "power":
            r, g, b = (int(wg.color[i:i + 2], 16) for i in (1, 3, 5))
            assert r > 150 and r > g + 40 and r > b + 20, wg.color  # reddish
    signal_nets = {wg.wire.net: wg.color for wg in lay.wires if wg.wire.kind == "signal"}
    assert len(set(signal_nets.values())) == len(signal_nets)  # distinct per net


def test_net_names_and_notes_in_svg(complex_):
    text = complex_[0].read_text(encoding="utf-8")
    for w in read_pins_csv(COMPLEX):
        assert f">{w.net}<" in text
        if w.note:
            assert w.note.replace("&", "&amp;") in text


def _drop_first_wire(svg_text: str) -> str:
    return re.sub(r'<polyline class="wire".*?</polyline>', "", svg_text, count=1, flags=re.S)


def test_check_fails_when_a_wire_is_missing(complex_):
    svg = complex_[0].read_text(encoding="utf-8")
    res = check(read_pins_csv(COMPLEX), _drop_first_wire(svg))
    assert not res.ok and len(res.missing) == 1 and not res.extra


def test_check_fails_on_extra_wire(complex_):
    svg = complex_[0].read_text(encoding="utf-8")
    first = re.search(r'<polyline class="wire".*?</polyline>', svg, flags=re.S).group(0)
    res = check(read_pins_csv(COMPLEX), svg.replace("</g>", first + "</g>", 1))
    assert not res.ok and len(res.extra) == 1


def test_check_fails_when_wire_ends_elsewhere(complex_):
    svg = complex_[0].read_text(encoding="utf-8")
    bad = re.sub(r'(<polyline class="wire".*?points=")([\d.]+),', r"\g<1>1,", svg, count=1, flags=re.S)
    res = check(read_pins_csv(COMPLEX), bad)
    assert not res.ok and res.geometry


def test_check_cli_exit_codes(complex_, tmp_path):
    svg = complex_[0]
    script = ROOT / "diagrams" / "check_wiring.py"
    ok = subprocess.run([sys.executable, str(script), str(COMPLEX), str(svg)], capture_output=True, text=True)
    assert ok.returncode == 0, ok.stdout
    broken = tmp_path / "wiring_broken.svg"
    broken.write_text(_drop_first_wire(svg.read_text(encoding="utf-8")), encoding="utf-8")
    bad = subprocess.run([sys.executable, str(script), str(COMPLEX), str(broken)], capture_output=True, text=True)
    assert bad.returncode == 1 and "MISSING" in bad.stdout


def test_wiring_cli(tmp_path):
    script = ROOT / "diagrams" / "wiring.py"
    r = subprocess.run([sys.executable, str(script), str(STANDIN), "--out", str(tmp_path), "--name", "x"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "wiring_x.svg").exists() and (tmp_path / "wiring_x.png").exists()


def test_layout_checker_detects_overlap(complex_):
    lay = complex_[2]
    a, b = lay.boxes[1], lay.boxes[2]
    b.x, b.y = a.x + 5, a.y + 5
    assert any("boxes overlap" in p for p in check_layout(lay))


@pytest.mark.parametrize("seed", range(40))
def test_random_netlists_layout_clean(seed):
    wires = random_netlist(seed, n_parts=3 + seed % 6, n_wires=8 + seed % 20)
    lay = build_layout(wires, "t")
    assert check_layout(lay) == []
    assert check(wires, to_svg(lay)).ok


@pytest.mark.parametrize("text,msg", [
    ("from_part,from_pin,to_part,to_pin,net,kind,note\nA,1,B,1,N,wire,\n", "kind"),
    ("from_part,from_pin,to_part,to_pin,net,kind,note\nA,1,B,1,N,signal,\nA,1,C,1,M,signal,\n", "net"),
    ("from_part,from_pin,to_part,to_pin,net\nA,1,B,1,N\n", "missing column"),
    ("from_part,from_pin,to_part,to_pin,net,kind,note\nA,1,A,1,N,signal,\n", "itself"),
])
def test_bad_csv_rejected(text, msg):
    with pytest.raises(PinsCsvError, match=msg):
        parse_pins_csv(text)
