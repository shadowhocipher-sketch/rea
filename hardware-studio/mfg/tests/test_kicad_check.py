"""mfg/kicad_check.py 的测试。

不需要 KiCad 的部分（报告解析、找不到 KiCad 时的提示）总会运行；
真正调用 kicad-cli 的集成测试只在本机有 KiCad 8+ 或设置了 KICAD_DOCKER_IMAGE 时运行。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

MFG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MFG))

import kicad_check  # noqa: E402

MINIMAL = MFG / "kicad" / "minimal"


def test_parse_erc_and_drc_reports(tmp_path):
    erc = {"sheets": [{"path": "/", "violations": [
        {"severity": "error", "type": "pin_not_connected", "description": "Pin not connected"},
        {"severity": "warning", "type": "lib_symbol_issues", "description": "x"},
    ]}]}
    drc = {"violations": [{"severity": "error", "type": "clearance", "description": "c"}],
           "unconnected_items": [{"severity": "error", "type": "unconnected_items", "description": "u"}],
           "schematic_parity": []}
    (tmp_path / "e.json").write_text(json.dumps(erc), encoding="utf-8")
    (tmp_path / "d.json").write_text(json.dumps(drc), encoding="utf-8")
    e = kicad_check.parse_report("ERC", Path("a.kicad_sch"), tmp_path / "e.json", 0)
    d = kicad_check.parse_report("DRC", Path("a.kicad_pcb"), tmp_path / "d.json", 0)
    assert e.counts == {"error": 1, "warning": 1, "info": 0}
    assert d.counts["error"] == 2 and d.by_type == {"clearance": 1, "unconnected_items": 1}
    md = kicad_check.render_summary([e, d], kicad_check.Runner(exe="kicad-cli"))
    assert "| ERC | a.kicad_sch | 1 | 1 | 0 | 已运行 |" in md


def test_collect_targets_from_project():
    targets = kicad_check.collect_targets([str(MINIMAL)])
    assert [k for k, _ in targets] == ["ERC", "DRC"]


def test_unavailable_gives_install_hint(monkeypatch, capsys):
    monkeypatch.setenv("PATH", "/nonexistent")
    monkeypatch.delenv("KICAD_CLI", raising=False)
    monkeypatch.delenv("KICAD_DOCKER_IMAGE", raising=False)
    with pytest.raises(kicad_check.KicadUnavailable, match="kicad-9.0-releases"):
        kicad_check.find_runner()
    assert kicad_check.main([str(MINIMAL)]) == 4
    assert "找不到可用的 KiCad 命令行" in capsys.readouterr().err


def test_bad_path_returns_2(tmp_path):
    assert kicad_check.main([str(tmp_path / "nothing.txt")]) == 2


def _runner_or_skip():
    try:
        return kicad_check.find_runner()
    except kicad_check.KicadUnavailable:
        pytest.skip("没有 KiCad 8+（可设置 KICAD_CLI 或 KICAD_DOCKER_IMAGE=kicad/kicad:9.0）")


def test_minimal_project_with_real_kicad(tmp_path):
    runner = _runner_or_skip()
    erc = kicad_check.run_check(runner, "ERC", MINIMAL / "minimal.kicad_sch", tmp_path, [])
    drc = kicad_check.run_check(runner, "DRC", MINIMAL / "minimal.kicad_pcb", tmp_path, [])
    assert erc.ran and drc.ran
    assert erc.counts["error"] == 0 and erc.counts["warning"] == 0
    # 夹具里故意放了两段悬空走线，KiCad 9 报 2 个 track_dangling 警告
    assert drc.by_type.get("track_dangling") == 2
    assert kicad_check.main([str(MINIMAL), "--out", str(tmp_path / "r")]) == 0
    assert kicad_check.main([str(MINIMAL), "--out", str(tmp_path / "r2"), "--fail-on", "warning"]) == 1
