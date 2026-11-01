import pytest

from hwcad.usbc import DEFAULT_OVERMOLD, DEFAULT_RECEPTACLE, usbc_cutout, usbc_opening_size
from cad_testutil import slab, vol


def test_opening_rule_depends_on_recess():
    w, h, _ = usbc_opening_size(1.0, clearance=0.3)
    assert (w, h) == pytest.approx((DEFAULT_OVERMOLD[0] + 0.6, DEFAULT_OVERMOLD[1] + 0.6))
    w, h, _ = usbc_opening_size(-0.5, clearance=0.3)
    assert (w, h) == pytest.approx((DEFAULT_RECEPTACLE[0] + 0.6, DEFAULT_RECEPTACLE[1] + 0.6))


@pytest.mark.parametrize("recess", [1.0, 0.0, -0.5])
def test_cut_through_and_plug_inserts(recess):
    wall = 2.0
    f = usbc_cutout(wall, recess=recess)
    plate = slab(wall) - f.cut
    assert not plate.is_inside((0, 0, -wall / 2))           # 打穿
    plug = f.envelopes["usb_c_plug_overmold"]
    rec = f.envelopes["usb_c_receptacle"]
    assert vol(plate & plug) < 1e-6                           # 插头插到底不碰壳
    assert vol(plate & rec) < 1e-6
    assert plug.bounding_box().min.Z == pytest.approx(-recess)


def test_too_small_opening_is_detected():
    wall = 2.0
    good = usbc_cutout(wall, recess=1.0)
    # 反例：按"插座外形"开孔却把插座缩进 1 mm —— 插头外壳会顶到壳
    bad = usbc_cutout(wall, recess=1.0, overmold_w=DEFAULT_RECEPTACLE[0], overmold_h=DEFAULT_RECEPTACLE[1])
    plate_bad = slab(wall) - bad.cut
    assert vol(plate_bad & good.envelopes["usb_c_plug_overmold"]) > 1.0
