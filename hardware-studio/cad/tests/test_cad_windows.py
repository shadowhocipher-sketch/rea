import pytest

from hwcad.windows import screen_window
from cad_testutil import slab, vol


def test_rect_window_cuts_through():
    wall = 2.0
    f = screen_window(wall, "rect", 20, 10, corner_radius=0)
    plate = slab(wall) - f.cut
    assert not plate.is_inside((0, 0, -wall / 2))
    assert vol(slab(wall)) - vol(plate) == pytest.approx(20 * 10 * wall, rel=1e-6)


def test_circle_window_and_size_change():
    f1 = screen_window(2.0, "circle", 20)
    f2 = screen_window(2.0, "circle", 30)
    assert vol(slab(2.0) - f1.cut) > vol(slab(2.0) - f2.cut)
    assert f2.info["opening"] == [30, 30]


def test_step_leaves_bezel_and_warns_when_thin():
    wall = 2.0
    f = screen_window(wall, "rect", 20, 10, corner_radius=0.5, step_width=26, step_height=16, step_depth=0.8,
                      step_clearance=0.2, min_wall=1.2)
    plate = slab(wall) - f.cut
    assert f.info["bezel_thickness"] == pytest.approx(1.2)
    assert plate.is_inside((11.5, 0, -0.6))        # 压边（台阶外侧，透光口内侧以外）
    assert not plate.is_inside((11.5, 0, -1.6))    # 台阶槽
    assert not f.info["warnings"]
    thin = screen_window(wall, "rect", 20, 10, step_width=26, step_height=16, step_depth=1.2, min_wall=1.2)
    assert thin.info["warnings"]
    with pytest.raises(ValueError):
        screen_window(wall, "rect", 20, 10, step_width=26, step_depth=2.5)
