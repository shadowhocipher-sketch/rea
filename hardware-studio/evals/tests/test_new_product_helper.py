"""The new-product helper (.claude/skills/new-product/product.py): the blank template must fail its
checks, a filled brief must pass step 1, and compliance-yaml must round-trip brief features."""
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / ".claude" / "skills" / "new-product" / "product.py"
TEMPLATE = ROOT / "products" / "_template"


def run(*args):
    return subprocess.run([sys.executable, str(HELPER), *map(str, args)], cwd=ROOT, capture_output=True, text=True)


def test_blank_template_fails_brief_check(tmp_path):
    d = tmp_path / "p"
    shutil.copytree(TEMPLATE, d)
    r = run("check", d, "--step", "1", "9")
    assert r.returncode == 1
    assert "[FAIL] 1." in r.stdout and "[FAIL] 9." in r.stdout


def test_filled_brief_passes_and_compliance_yaml_roundtrips(tmp_path):
    d = tmp_path / "p"
    shutil.copytree(TEMPLATE, d)
    b = yaml.safe_load((TEMPLATE / "brief.yaml").read_text(encoding="utf-8"))
    b["name"] = "test-gadget"
    b["one_liner"] = "测试"
    b["scenario"] = {"who": "成人", "where": "桌面", "when": "每天", "feeling": ["安静"], "interaction": "按键",
                     "not_doing": []}
    b["market"] = {"regions": ["EU", "US"], "channel": "自用"}
    b["price"] = {"currency": "USD", "target_retail": 30, "target_unit_cost": 12, "quantities": [100, 1000]}
    b["features"] = {"wireless": ["ble"], "connected": False, "batteries": ["lithium"], "adapter": False,
                     "children": False}
    b["hardware_intent"]["size_limit_mm"] = [60, 40, 20]
    b["enclosure_intent"]["look"] = "白色"
    (d / "brief.yaml").write_text(yaml.safe_dump(b, allow_unicode=True), encoding="utf-8")
    r = run("check", d, "--step", "1")
    assert r.returncode == 0, r.stdout
    assert run("compliance-yaml", d).returncode == 0
    spec = yaml.safe_load((d / "compliance.yaml").read_text(encoding="utf-8"))
    assert spec["wireless"] == ["ble"] and spec["batteries"] == ["lithium"] and spec["markets"] == ["EU", "US"]
    r = run("check", d, "--step", "7")
    assert "[OK  ] 7.合规：compliance.yaml 与 brief.yaml 的 features 一致" in r.stdout
    b["features"]["wireless"] = ["zigbee"]
    (d / "brief.yaml").write_text(yaml.safe_dump(b, allow_unicode=True), encoding="utf-8")
    assert run("compliance-yaml", d).returncode == 2
