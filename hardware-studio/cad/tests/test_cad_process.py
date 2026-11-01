import pytest

from hwcad.process import HEAT_INSERT_TABLE, PRINTER_BEDS, PROCESSES, get_process


def test_aliases_and_unknown():
    assert get_process("FDM").key == "fdm"
    assert get_process("dlp").key == "sla"
    assert get_process("injection").key == "im"
    with pytest.raises(KeyError):
        get_process("cnc")


def test_every_numeric_rule_has_source():
    for p in PROCESSES.values():
        for f in ("min_wall", "default_wall", "fit_clearance", "moving_clearance", "tolerance_100mm", "min_hole"):
            assert f in p.sources, (p.key, f)
        assert p.default_wall >= p.min_wall
    for row in list(HEAT_INSERT_TABLE.values()) + list(PRINTER_BEDS.values()):
        assert "source" in row
