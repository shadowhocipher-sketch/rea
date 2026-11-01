import pytest
from build123d import Location

from hwcad.frames import wall_plane
from hwcad.shell import ShellSpec, make_shell
from hwcad.snaps import cantilever_snap, snap_fit
from cad_testutil import vol


def _assembled(spec, **kw):
    halves = make_shell(spec)
    f = snap_fit(spec.wall, spec.split_z, **kw)
    loc = Location(wall_plane(spec.size, "+x", 0.0))
    lower = halves["lower"] + f.add.moved(loc)
    upper = halves["upper"] - f.cut.moved(loc)
    return lower, upper, f


def test_snap_assembly_zero_interference_and_engaged():
    spec = ShellSpec(length=60, width=40, height=24, wall=2.7, split_z=8, lip_thickness=1.2, lip_clearance=0.3)
    lower, upper, f = _assembled(spec, length=10, thickness=1.2, width=5, undercut=0.8, gap=0.2)
    assert lower.is_valid and upper.is_valid
    assert vol(lower & upper) < 1e-6
    # 卡钩伸进了上壳内壁原来的位置（被卡槽让开）
    x_in_wall = spec.length / 2 - spec.wall + 0.3
    z_hook = f.info["hook_z_range"][0] + 0.3
    assert lower.is_inside((x_in_wall, 0, z_hook))
    assert not upper.is_inside((x_in_wall, 0, z_hook))
    assert upper.is_inside((spec.length / 2 - 0.3, 0, z_hook))     # 卡槽是盲槽，外表面完整
    assert f.info["deflection"] == pytest.approx(0.6)
    assert f.info["root_strain_est"] == pytest.approx(1.5 * 1.2 * 0.6 / 100)


def test_snap_params_change_strain_and_validate():
    a = snap_fit(2.7, 8, length=10, undercut=0.8)
    b = snap_fit(2.7, 8, length=14, undercut=0.8)
    assert b.info["root_strain_est"] < a.info["root_strain_est"]
    assert snap_fit(2.7, 8, length=6, undercut=1.0, allowable_strain=0.02).info["warnings"]
    assert snap_fit(1.5, 8, undercut=1.0, gap=0.1, min_wall=1.2).info["warnings"]   # 卡槽太深
    with pytest.raises(ValueError):
        snap_fit(2.7, 8, undercut=0.2, gap=0.3)
    s = cantilever_snap(length=10, thickness=1.2, width=5, undercut=0.8)
    assert s.is_valid and s.bounding_box().max.X == pytest.approx(0.8)
