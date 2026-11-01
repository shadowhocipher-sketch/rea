"""合规地图的自动检查：数据完整性、触发逻辑、map.md 一致性、四个典型产品的清单。"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build_map  # noqa: E402
import checklist  # noqa: E402

DATA = checklist.load_data()
REQS = DATA["requirements"]
BY_ID = {r["id"]: r for r in REQS}
EXAMPLES = sorted((ROOT / "examples").glob("*.yaml"))

REQUIRED_FIELDS = (
    "id", "market", "features", "name", "instrument", "requirement", "applies_when",
    "trigger", "evidence", "sources", "checked", "status",
)


def ids_for(spec: dict) -> set[str]:
    p = checklist.make_product(spec)
    return {r["id"] for r in checklist.select(DATA, p)}


# ── 数据完整性 ──────────────────────────────────────────────

def test_ids_unique_and_prefixed():
    ids = [r["id"] for r in REQS]
    assert len(ids) == len(set(ids))
    for r in REQS:
        assert re.fullmatch(r"(CN|EU|US|UK|AU)-\d{2}", r["id"]), r["id"]
        assert r["id"].startswith(r["market"] + "-")


@pytest.mark.parametrize("r", REQS, ids=lambda r: r["id"])
def test_fields_and_values(r):
    for f in REQUIRED_FIELDS:
        assert r.get(f) not in (None, "", []), f"{r['id']} 缺少 {f}"
    assert r["market"] in DATA["markets"]
    assert set(r["features"]) <= set(DATA["features"])
    assert r["evidence"] in DATA["evidence_types"]
    assert r["status"] in ("已核实", "待核实")
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["checked"])
    assert set(r["trigger"]) <= {"all", "any", "none"}


@pytest.mark.parametrize("r", REQS, ids=lambda r: r["id"])
def test_every_requirement_has_links(r):
    """每条要求都有链接；没有 S/A 级官方链接的必须标待核实并写明疑点。"""
    assert r["sources"], f"{r['id']} 没有来源"
    for s in r["sources"]:
        assert s["url"].startswith("https://"), s
        assert s["level"] in ("S", "A", "B", "C")
        assert s["access"] in ("search", "pattern")
        assert s.get("title") and s.get("kind")
    official = [s for s in r["sources"] if s["level"] in ("S", "A")]
    if not official:
        assert r["status"] == "待核实", f"{r['id']} 只有 C 级来源却标了已核实"
    if r["status"] == "待核实":
        assert r.get("doubts"), f"{r['id']} 标待核实但没写疑点"


@pytest.mark.parametrize("r", REQS, ids=lambda r: r["id"])
def test_verified_needs_official_source_seen(r):
    """已核实的条目至少有一个在搜索结果里实际见到的 S/A 级来源。"""
    if r["status"] == "已核实":
        assert any(s["level"] in ("S", "A") and s["access"] == "search" for s in r["sources"]), r["id"]


def test_matrix_fully_covered():
    """四个特征 × 五个市场（外加基础、联网、纽扣电池行）每格都有条目。"""
    for f in build_map.FEATURE_ORDER:
        for m in DATA["markets"]:
            assert build_map.cell_ids(DATA, f, m), f"总表空格：{f} × {m}"


def test_triggers_use_known_tokens():
    for r in REQS:
        checklist.trigger_matches(r["trigger"], set())  # 未知 token 会抛错


# ── 触发逻辑 ──────────────────────────────────────────────

WIRELESS_ONLY = {"CN-01", "CN-02", "EU-01", "US-01", "US-02", "UK-01", "AU-01", "AU-02"}
BATTERY_ONLY = {"CN-05", "EU-10", "EU-11", "UK-06", "US-08", "US-09", "AU-08", "CN-08", "EU-14", "US-05", "UK-10", "AU-05"}
TOY_ONLY = {"CN-06", "EU-13", "US-06", "UK-08", "AU-06"}
ADAPTER_ONLY = {"CN-04", "EU-06", "EU-07", "US-07", "US-10", "UK-03", "UK-11", "AU-04"}
CONNECTED_ONLY = {"CN-09", "UK-09", "AU-07", "US-04"}


def test_ids_in_expectation_sets_exist():
    for s in (WIRELESS_ONLY, BATTERY_ONLY, TOY_ONLY, ADAPTER_ONLY, CONNECTED_ONLY):
        assert s <= set(BY_ID)


def test_no_wireless_no_radio_requirements():
    got = ids_for({"wireless": [], "connected": False})
    assert not (got & WIRELESS_ONLY)
    assert "EU-03" not in got and "EU-02" not in got
    assert {"EU-05", "UK-02"} <= got  # 无无线时走 EMC 指令/条例


def test_wireless_brings_radio_and_drops_emc():
    got = ids_for({"wireless": ["ble"], "connected": False})
    assert WIRELESS_ONLY <= got
    assert "EU-05" not in got and "UK-02" not in got


def test_battery_items_only_with_battery():
    none = ids_for({})
    assert not (none & BATTERY_ONLY)
    li = ids_for({"batteries": ["lithium"]})
    assert {"CN-05", "EU-10", "EU-11", "UK-06", "US-08", "US-09", "AU-08"} <= li
    assert not (li & {"CN-08", "EU-14", "US-05", "UK-10", "AU-05"})  # 纽扣电池条目不出
    coin = ids_for({"batteries": ["coin"]})
    assert {"CN-08", "EU-14", "US-05", "UK-10", "AU-05", "EU-10", "EU-11", "UK-06"} <= coin
    assert "CN-05" not in coin  # 锂离子 CCC 不出


def test_toy_items_only_for_children():
    assert not (ids_for({}) & TOY_ONLY)
    assert TOY_ONLY <= ids_for({"children": True})


def test_adapter_items_only_with_adapter():
    assert not (ids_for({}) & ADAPTER_ONLY)
    assert ADAPTER_ONLY <= ids_for({"adapter": True})


def test_connected_items_and_inference():
    assert not (ids_for({"wireless": ["ble"]}) & CONNECTED_ONLY)  # BLE 不推断为联网
    assert CONNECTED_ONLY <= ids_for({"wireless": ["wifi"]})      # 有 Wi-Fi 默认联网
    assert not (ids_for({"wireless": ["wifi"], "connected": False}) & CONNECTED_ONLY)


def test_red_cyber_toy_or_connected():
    assert "EU-03" in ids_for({"wireless": ["ble"], "children": True})
    assert "EU-03" in ids_for({"wireless": ["wifi"], "connected": True})
    assert "EU-03" not in ids_for({"wireless": ["ble"], "connected": False})
    assert "EU-03" not in ids_for({"children": True})


def test_common_charger_needs_radio_and_rechargeable():
    assert "EU-02" in ids_for({"wireless": ["ble"], "batteries": ["lithium"]})
    assert "EU-02" not in ids_for({"batteries": ["lithium"]})
    assert "EU-02" not in ids_for({"wireless": ["ble"], "batteries": ["coin"]})


def test_market_filter():
    p = checklist.make_product({"wireless": ["wifi"], "markets": ["CN"]})
    assert {r["market"] for r in checklist.select(DATA, p)} == {"CN"}


@pytest.mark.parametrize("bad", [
    {"wireless": ["zigbee5"]},
    {"batteries": ["nimh"]},
    {"markets": ["JP"]},
    {"adapter": "yes"},
    {"colour": "red"},
])
def test_bad_input_rejected(bad):
    with pytest.raises(checklist.InputError):
        checklist.make_product(bad)


# ── map.md 一致性 ──────────────────────────────────────────

def test_map_in_sync_with_yaml():
    current = (ROOT / "map.md").read_text(encoding="utf-8")
    assert current == build_map.render_map(DATA), "map.md 过期：运行 python build_map.py"


def test_map_anchors_match_yaml():
    text = (ROOT / "map.md").read_text(encoding="utf-8")
    anchors = set(re.findall(r'<a id="([A-Z]{2}-\d{2})"></a>', text))
    linked = set(re.findall(r"\]\(#([A-Z]{2}-\d{2})\)", text))
    assert anchors == set(BY_ID)
    assert linked == set(BY_ID)


def test_map_disclaimer():
    text = (ROOT / "map.md").read_text(encoding="utf-8")
    assert "不是法律意见" in text.splitlines()[2]


# ── 四个典型产品 ──────────────────────────────────────────

def test_four_examples_exist():
    assert len(EXAMPLES) == 4


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.stem)
def test_example_checklist_generated_and_current(path, tmp_path):
    out = tmp_path / (path.stem + ".md")
    rc = subprocess.run(
        [sys.executable, str(ROOT / "checklist.py"), "--product", str(path), "--out", str(out)],
        capture_output=True, text=True,
    )
    assert rc.returncode == 0, rc.stderr
    text = out.read_text(encoding="utf-8")
    lines = [l for l in text.splitlines() if l.strip()]
    assert "不是法律意见" in lines[1] and "不是法律意见" in lines[-1]
    committed = path.with_suffix(".md")
    assert committed.exists(), f"缺少 {committed.name}，运行 checklist.py 生成"
    assert committed.read_text(encoding="utf-8") == text, f"{committed.name} 过期"
    # 每个条目都带链接；待核实条目带标记
    for block in text.split("\n### ")[1:]:
        assert "](https://" in block
        rid = block.split()[0]
        if BY_ID[rid]["status"] == "待核实":
            assert "待核实" in block.splitlines()[0]


def _example_ids(stem: str) -> set[str]:
    import yaml
    spec = yaml.safe_load((ROOT / "examples" / f"{stem}.yaml").read_text(encoding="utf-8"))
    return ids_for(spec)


def test_example_a_wifi_desk():
    got = _example_ids("a_wifi_desk_usb")
    assert WIRELESS_ONLY | CONNECTED_ONLY | {"EU-03", "EU-04"} <= got
    assert not (got & (BATTERY_ONLY | TOY_ONLY | ADAPTER_ONLY))


def test_example_b_pocket_offline():
    got = _example_ids("b_pocket_lithium_offline")
    assert {"CN-05", "EU-10", "EU-11", "US-08", "EU-05", "UK-02"} <= got
    assert not (got & (WIRELESS_ONLY | CONNECTED_ONLY | TOY_ONLY | ADAPTER_ONLY | {"EU-02", "EU-03", "EU-04"}))


def test_example_c_ble_toy():
    got = _example_ids("c_ble_coin_toy")
    assert TOY_ONLY | WIRELESS_ONLY | {"EU-03", "US-05", "AU-05", "CN-08"} <= got
    assert not (got & ADAPTER_ONLY) and "CN-05" not in got


def test_example_d_wifi_adapter():
    got = _example_ids("d_wifi_with_adapter")
    assert ADAPTER_ONLY | WIRELESS_ONLY | CONNECTED_ONLY <= got
    assert not (got & (BATTERY_ONLY | TOY_ONLY))
