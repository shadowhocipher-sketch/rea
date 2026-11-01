import pytest

from hwcad.buttons import button_cap, button_hole, cantilever_button, cantilever_strain
from cad_testutil import slab, vol


def test_button_hole_and_sleeve():
    wall = 2.0
    f = button_hole(wall, diameter=6, clearance=0.3, sleeve_length=4, sleeve_wall=1.2)
    part = (slab(wall) + f.add) - f.cut
    assert part.is_valid
    assert not part.is_inside((0, 0, -1.0))          # 孔打穿壁
    assert not part.is_inside((0, 0, -5.0))          # 导向筒内是空的
    assert part.is_inside((3.3 + 0.6, 0, -5.0))      # 导向筒壁
    cap = button_cap(wall, 6, sleeve_length=4, flange_t=1.2)
    assert vol(cap & part) < 1e-6                    # 按键帽与外壳不干涉
    assert cap.bounding_box().max.Z == pytest.approx(1.0)


def test_cantilever_button_geometry_and_strain():
    wall = 2.0
    f = cantilever_button(wall, length=12, width=7, slot=0.8, tongue_thickness=1.2, nub_height=1.5, travel=0.5)
    part = (slab(wall) + f.add) - f.cut
    assert part.is_valid
    assert len(part.solids()) == 1                   # 舌片仍连在壁上
    assert not part.is_inside((6.4, 0, -1.0))        # 自由端的槽打穿
    assert part.is_inside((0, 0, -0.6))             # 舌片
    assert not part.is_inside((0, 0, -1.6))          # 舌片内侧已减薄
    assert part.is_inside((3.5, 0, -2.0))            # 凸点
    assert f.info["root_strain_est"] == pytest.approx(cantilever_strain(12, 1.2, 0.5))
    assert cantilever_strain(10, 1.2, 0.6) == pytest.approx(1.5 * 1.2 * 0.6 / 100)
    longer = cantilever_button(wall, length=16, tongue_thickness=1.2, travel=0.5)
    assert longer.info["root_strain_est"] < f.info["root_strain_est"]
    assert cantilever_button(wall, length=6, travel=1.0, allowable_strain=0.01).info["warnings"]
