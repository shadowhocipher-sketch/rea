import pytest

from hwcad.battery import battery_bay, swollen_thickness
from cad_testutil import vol


def test_swell_and_envelope_clear_of_frame():
    f = battery_bay(40, 30, 5, swell=0.10, xy_clearance=0.5, rib_height=3)
    assert swollen_thickness(5, 0.10) == pytest.approx(5.5)
    assert f.info["required_height"] == pytest.approx(5.8)
    cell = f.envelopes["battery_cell_swollen"]
    assert vol(cell & f.add) < 1e-6
    assert f.info["pocket_inner"] == [41.0, 31.0]


def test_wire_slot_and_params():
    f = battery_bay(40, 30, 5, wire_side="+x", wire_slot_width=4)
    assert not f.add.is_inside((20.5 + 0.6, 0, 1.0))      # 走线口处没有筋
    assert f.add.is_inside((20.5 + 0.6, 10, 1.0))         # 别处有筋
    g = battery_bay(40, 30, 5, wire_side="-y")
    assert not g.add.is_inside((0, -(15.5 + 0.6), 1.0))
    bigger = battery_bay(50, 30, 5)
    assert vol(bigger.add) > vol(f.add)
    with pytest.raises(ValueError):
        battery_bay(40, 30, 5, wire_side="up")
