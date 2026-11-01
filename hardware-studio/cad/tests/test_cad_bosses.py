import math

import pytest

from hwcad.bosses import boss, clearance_post, counterbore_cutter, heat_insert_boss, self_tap_boss, thread_diameter
from cad_testutil import slab, vol


def test_boss_volume_formula():
    b = boss(6, 2.4, 10)
    assert vol(b) == pytest.approx(math.pi * (3 ** 2 - 1.2 ** 2) * 10, rel=1e-6)
    assert not b.is_inside((0, 0, 5))      # 孔是空的
    assert b.is_inside((2.5, 0, 5))


def test_self_tap_follows_ejot_ratio_and_scales():
    b3, i3 = self_tap_boss("M3", 8)
    b2, i2 = self_tap_boss("M2", 8)
    assert i3["hole_d"] == pytest.approx(2.4) and i3["outer_d"] == pytest.approx(6.0)
    assert vol(b3) > vol(b2)
    assert thread_diameter("M2.5") == 2.5


def test_heat_insert_default_and_blind_hole():
    b, info = heat_insert_boss("M3", 10)
    assert info["hole_d"] == 4.0 and info["outer_d"] == pytest.approx(4.0 + 2 * 1.8)
    assert not b.is_inside((0, 0, 9.5))          # 孔口附近是空的
    assert b.is_inside((0, 0, 1.0))              # 孔底以下是实心（盲孔，深 6.8）
    with pytest.raises(ValueError):
        heat_insert_boss("M2", 10)               # 没有来源的规格必须显式给参数
    b2, _ = heat_insert_boss("M2", 6, insert_hole_d=3.2, insert_length=4.0, min_wall=1.5)
    assert b2.is_valid
    with pytest.raises(ValueError):
        heat_insert_boss("M3", 5)                # 柱高不够


def test_counterbore_goes_through_floor():
    floor = slab(2.0)
    cut = counterbore_cutter("M3", depth=1.0, through_len=5)
    holed = floor - cut
    assert not holed.is_inside((0, 0, -1.9))      # 过孔打穿
    assert not holed.is_inside((3.0, 0, -0.5))    # 沉头孔区（半径 3.3）
    assert holed.is_inside((3.0, 0, -1.5))        # 沉头孔底下仍有料
    p, info = clearance_post("M3", 5)
    assert info["hole_d"] == pytest.approx(3.4)
