import math

import pytest

from hwcad.shell import ShellSpec, hollow_box, make_shell, rounded_box, rounded_rect_prism
from cad_testutil import vol


def test_rounded_box_volume_between_bounds():
    b = rounded_box(40, 30, 20, corner_radius=5, edge_radius=1)
    assert b.is_valid
    assert vol(b) < 40 * 30 * 20
    # 只倒竖直棱时的精确体积
    exact = (40 * 30 - (4 - math.pi) * 25) * 20
    assert vol(rounded_box(40, 30, 20, 5, 0)) == pytest.approx(exact, rel=1e-6)
    bb = b.bounding_box()
    assert (bb.size.X, bb.size.Y, bb.size.Z) == pytest.approx((40, 30, 20))


def test_hollow_box_volume_follows_wall():
    v1 = vol(hollow_box(40, 30, 20, wall=1.5, corner_radius=4, edge_radius=0))
    v2 = vol(hollow_box(40, 30, 20, wall=2.5, corner_radius=4, edge_radius=0))
    assert v2 > v1 > 0
    inner = vol(rounded_rect_prism(37, 27, 2.5, 0, 17))
    assert v1 == pytest.approx(vol(rounded_box(40, 30, 20, 4, 0)) - inner, rel=1e-6)


def test_split_no_interference_and_lip_clearance():
    spec = ShellSpec(length=60, width=40, height=20, wall=2.7, corner_radius=5, edge_radius=1,
                     split_z=8, lip_height=2, lip_thickness=1.2, lip_clearance=0.3)
    halves = make_shell(spec)
    lo, up = halves["lower"], halves["upper"]
    assert lo.is_valid and up.is_valid
    assert vol(lo & up) < 1e-6
    # 止口环在分模面以上，上壳在同一处有让位槽
    z = spec.split_z + 1.0
    x_lip = spec.length / 2 - spec.wall + 0.6       # 止口环中部
    assert lo.is_inside((x_lip, 0, z))
    assert not up.is_inside((x_lip, 0, z))
    x_gap = spec.length / 2 - spec.wall + spec.lip_thickness + 0.15  # 水平间隙中间
    assert not lo.is_inside((x_gap, 0, z)) and not up.is_inside((x_gap, 0, z))
    assert up.is_inside((spec.length / 2 - 0.5, 0, z))  # 上壳剩余外壁


def test_param_change_moves_split():
    a = make_shell(ShellSpec(split_z=8))
    b = make_shell(ShellSpec(split_z=12))
    assert b["lower"].bounding_box().max.Z > a["lower"].bounding_box().max.Z
    assert vol(b["lower"]) > vol(a["lower"])


def test_validate_reports_problems():
    assert ShellSpec(wall=2.0, lip_thickness=0.8, lip_clearance=0.3).validate(min_wall=1.2)  # 上壳剩余 0.9
    assert not ShellSpec(wall=2.7, lip_thickness=1.2, lip_clearance=0.3).validate(min_wall=1.2)
    with pytest.raises(ValueError):
        make_shell(ShellSpec(split_z=0.5))
    names = ShellSpec(style="front_back").part_names()
    assert names == {"lower": "back", "upper": "front"}
