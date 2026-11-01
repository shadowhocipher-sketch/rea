"""mfg/cost.py 的测试：阶梯价、MOQ、损耗、估算比例、多数量档输出、缺价格处理、价格缓存检查。"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest
import yaml

MFG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MFG))

import cost  # noqa: E402

BOM_HEADER = "ref,name,qty_per_unit,category,lcsc,price_key,cost_mode,attrition,joints,dnp\n"


def _prices(tmp_path: Path, entries: list[dict]) -> dict[str, cost.PriceEntry]:
    base = {"currency": "USD", "date": "2026-11-01", "source_url": "https://example.invalid/x", "status": "quote"}
    full = [{**base, **e} for e in entries]
    p = tmp_path / "p.yaml"
    p.write_text(yaml.safe_dump(full, allow_unicode=True), encoding="utf-8")
    return cost.load_prices(p)


def _bom(tmp_path: Path, rows: str) -> list[cost.BomLine]:
    p = tmp_path / "bom.csv"
    p.write_text(BOM_HEADER + rows, encoding="utf-8")
    return cost.load_bom(p)


LADDER = [{"qty": 1, "price": 0.10}, {"qty": 10, "price": 0.08}, {"qty": 100, "price": 0.05}]


# ------------------------------------------------------------ 阶梯价


def test_price_break_selection(tmp_path):
    e = _prices(tmp_path, [{"key": "a", "breaks": LADDER}])["a"]
    assert e.price_at(1) == 0.10
    assert e.price_at(9) == 0.10
    assert e.price_at(10) == 0.08
    assert e.price_at(99) == 0.08
    assert e.price_at(100) == 0.05
    assert e.price_at(10_000) == 0.05


def test_breaks_sorted_even_if_cache_unsorted(tmp_path):
    e = _prices(tmp_path, [{"key": "a", "breaks": list(reversed(LADDER))}])["a"]
    assert [b.qty for b in e.breaks] == [1, 10, 100]
    assert e.price_at(50) == 0.08


def test_buy_up_to_cheaper_break(tmp_path):
    e = _prices(tmp_path, [{"key": "a", "breaks": [{"qty": 1, "price": 0.05}, {"qty": 100, "price": 0.03}]}])["a"]
    assert cost.order_quantity(90, e) == 100          # 100×0.03=3.0 < 90×0.05=4.5
    assert cost.order_quantity(90, e, optimize=False) == 90
    assert cost.order_quantity(50, e) == 50           # 50×0.05=2.5 < 3.0，不多买


# ------------------------------------------------------------ MOQ 和包装倍数


def test_moq_and_order_multiple(tmp_path):
    p = _prices(tmp_path, [
        {"key": "moq", "breaks": [{"qty": 10, "price": 1.0}]},                      # MOQ 默认取首档 10
        {"key": "reel", "moq": 1, "order_multiple": 50, "breaks": [{"qty": 1, "price": 1.0}]},
    ])
    assert cost.order_quantity(3, p["moq"]) == 10
    assert cost.order_quantity(51, p["reel"]) == 100
    bom = _bom(tmp_path, "U1,x,1,electronic,,moq,unit,0,,\n")
    t = cost.compute_tier(bom, p, 3)
    r = t.lines[0]
    assert r.order_qty == 10 and r.line_total == pytest.approx(10.0)
    assert t.per_unit == pytest.approx(10.0 / 3)


# ------------------------------------------------------------ 损耗


def test_attrition_default_override_and_process(tmp_path):
    p = _prices(tmp_path, [{"key": "a", "breaks": [{"qty": 1, "price": 1.0}]}])
    bom = _bom(tmp_path,
               "R1,a,2,electronic,,a,unit,,,\n"       # 默认损耗 5%
               "R2,b,2,电子件,,a,unit,0.5,,\n"        # 行覆盖 50%
               "R3,c,2,electronic,,a,unit,10%,,\n"    # 百分号写法
               "L1,labor,2,加工费,,a,unit,,,\n")      # 加工费不计默认损耗
    t = cost.compute_tier(bom, p, 100, attrition=0.05)
    need = [r.need for r in t.lines]
    assert need == pytest.approx([210, 300, 220, 200])
    assert [r.order_qty for r in t.lines] == [210, 300, 220, 200]


# ------------------------------------------------------------ 计费方式


def test_batch_joint_and_extended_modes(tmp_path):
    p = _prices(tmp_path, [
        {"key": "ic", "breaks": [{"qty": 1, "price": 1.0}], "jlc_class": "Extended", "joints": 8},
        {"key": "r", "breaks": [{"qty": 1, "price": 0.01}], "jlc_class": "Basic", "joints": 2},
        {"key": "setup", "breaks": [{"qty": 1, "price": 8.0}]},
        {"key": "joint", "breaks": [{"qty": 1, "price": 0.002}]},
        {"key": "ext", "breaks": [{"qty": 1, "price": 3.0}]},
    ])
    bom = _bom(tmp_path,
               "U1,ic,1,electronic,,ic,unit,0,,\n"
               "R1,r,3,electronic,,r,unit,0,,\n"
               "S1,setup,1,process,,setup,batch,,,\n"
               "S2,joints,1,process,,joint,per_joint,,,\n"
               "S3,ext,1,process,,ext,per_extended_type,,,\n")
    t = cost.compute_tier(bom, p, 10)
    by = {r.line.ref: r for r in t.lines}
    assert by["S1"].line_total == pytest.approx(8.0)              # 一次性，与数量无关
    assert by["S2"].need == pytest.approx((8 + 3 * 2) * 10)       # 每台 14 焊点 × 10 台
    assert by["S3"].need == 1                                     # 1 种扩展料
    assert t.one_time() == pytest.approx(8.0 + 3.0)


def test_bom_joints_column_overrides_cache_and_unknown_warns(tmp_path):
    p = _prices(tmp_path, [
        {"key": "ic", "breaks": [{"qty": 1, "price": 1.0}]},
        {"key": "joint", "breaks": [{"qty": 1, "price": 0.01}]},
    ])
    bom = _bom(tmp_path,
               "U1,ic,1,electronic,,ic,unit,0,20,\n"
               "U2,ic,1,electronic,,ic,unit,0,,\n"
               "S2,joints,1,process,,joint,per_joint,,,\n")
    t = cost.compute_tier(bom, p, 1)
    assert t.lines[2].need == 20
    assert any("U2" in w for w in t.warnings)


# ------------------------------------------------------------ 估算比例


def test_status_share(tmp_path):
    p = _prices(tmp_path, [
        {"key": "q", "breaks": [{"qty": 1, "price": 6.0}]},
        {"key": "u", "status": "unverified", "basis": "摘要", "breaks": [{"qty": 1, "price": 3.0}]},
        {"key": "e", "status": "estimate", "basis": "假设", "breaks": [{"qty": 1, "price": 1.0}]},
    ])
    bom = _bom(tmp_path, "A,q,1,electronic,,q,unit,0,,\nB,u,1,module,,u,unit,0,,\nC,e,1,packaging,,e,unit,0,,\n")
    t = cost.compute_tier(bom, p, 10)
    assert t.total == pytest.approx(100.0)
    assert t.share() == pytest.approx({"quote": 0.6, "unverified": 0.3, "estimate": 0.1})
    row = cost.summary_row(t)
    assert row["quote_share"] == 0.6 and row["estimate_amount"] == 10.0


# ------------------------------------------------------------ 缺价格


def test_missing_price_excluded_and_flagged(tmp_path):
    p = _prices(tmp_path, [{"key": "q", "breaks": [{"qty": 1, "price": 1.0}]}])
    bom = _bom(tmp_path, "A,q,1,electronic,,q,unit,0,,\nB,nokey,1,electronic,C999,,unit,0,,\nC,nolink,1,mechanical,,,unit,0,,\n")
    t = cost.compute_tier(bom, p, 10)
    assert [r.line.ref for r in t.missing] == ["B", "C"]
    assert t.total == pytest.approx(10.0)
    assert t.lines[1].line.price_key == "lcsc:C999"                 # 由立创编号自动生成价格来源键
    assert sum("缺价格" in w for w in t.warnings) == 2
    md = cost.render_markdown([t], "bom.csv", 0)
    assert "缺价格" in md


def test_cli_strict_exit_code(tmp_path, capsys):
    pdir = tmp_path / "prices"
    pdir.mkdir()
    (pdir / "a.yaml").write_text(yaml.safe_dump([{"key": "q", "currency": "USD", "date": "2026-11-01",
                                                  "source_url": "https://example.invalid", "status": "quote",
                                                  "breaks": [{"qty": 1, "price": 1.0}]}]), encoding="utf-8")
    bom = tmp_path / "bom.csv"
    bom.write_text(BOM_HEADER + "A,q,1,electronic,,q,unit,,,\nB,x,1,electronic,,missing,unit,,,\n", encoding="utf-8")
    assert cost.main([str(bom), "--prices", str(pdir), "--qty", "10"]) == 0
    assert cost.main([str(bom), "--prices", str(pdir), "--qty", "10", "--strict"]) == 3


def test_dnp_line_not_priced(tmp_path):
    p = _prices(tmp_path, [{"key": "q", "breaks": [{"qty": 1, "price": 1.0}]}])
    bom = _bom(tmp_path, "A,q,1,electronic,,q,unit,0,,\nB,q,1,electronic,,q,unit,0,,y\n")
    t = cost.compute_tier(bom, p, 10)
    assert t.total == pytest.approx(10.0)
    assert t.lines[1].status == "dnp" and not t.missing


# ------------------------------------------------------------ 多数量档输出


def test_multi_tier_outputs(tmp_path):
    p = _prices(tmp_path, [{"key": "q", "breaks": LADDER}, {"key": "s", "breaks": [{"qty": 1, "price": 5.0}]}])
    bom = _bom(tmp_path, "A,q,1,electronic,,q,unit,0,,\nS,setup,1,process,,s,batch,,,\n")
    tiers = [cost.compute_tier(bom, p, q) for q in (10, 100)]
    assert tiers[0].per_unit == pytest.approx(0.08 + 0.5)
    assert tiers[1].per_unit == pytest.approx(0.05 + 0.05)
    files = cost.write_outputs(tiers, tmp_path / "out", "bom.csv", 0)
    names = sorted(f.name for f in files)
    assert names == ["cost.md", "cost_10.csv", "cost_100.csv", "summary.csv"]
    with (tmp_path / "out" / "summary.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert [int(r["qty"]) for r in rows] == [10, 100]
    with (tmp_path / "out" / "cost_100.csv").open(encoding="utf-8") as fh:
        detail = list(csv.DictReader(fh))
    assert detail[0]["order_qty"] == "100" and detail[0]["status"] == "实查"


# ------------------------------------------------------------ 币种


def test_fx_required_and_applied(tmp_path):
    p = _prices(tmp_path, [{"key": "c", "currency": "CNY", "breaks": [{"qty": 1, "price": 10.0}]}])
    bom = _bom(tmp_path, "A,c,1,electronic,,c,unit,0,,\n")
    with pytest.raises(cost.InputError, match="--fx"):
        cost.compute_tier(bom, p, 1)
    t = cost.compute_tier(bom, p, 1, fx={"CNY": 0.5})
    assert t.total == pytest.approx(5.0)


# ------------------------------------------------------------ 输入检查


@pytest.mark.parametrize("entry, msg", [
    ({"key": "a", "status": "estimate", "breaks": [{"qty": 1, "price": 1}]}, "basis"),
    ({"key": "a", "status": "quote", "source_url": "", "breaks": [{"qty": 1, "price": 1}]}, "source_url"),
    ({"key": "a", "date": "", "breaks": [{"qty": 1, "price": 1}]}, "date"),
    ({"key": "a", "status": "guess", "breaks": [{"qty": 1, "price": 1}]}, "status"),
    ({"key": "a", "breaks": []}, "breaks"),
])
def test_price_cache_validation(tmp_path, entry, msg):
    with pytest.raises(cost.InputError, match=msg):
        _prices(tmp_path, [entry])


def test_duplicate_key_rejected(tmp_path):
    with pytest.raises(cost.InputError, match="重复"):
        _prices(tmp_path, [{"key": "a", "breaks": LADDER}, {"key": "a", "breaks": LADDER}])


def test_bom_bad_category_and_missing_column(tmp_path):
    with pytest.raises(cost.InputError, match="类别"):
        _bom(tmp_path, "A,x,1,螺丝,,,unit,,,\n")
    p = tmp_path / "bad.csv"
    p.write_text("ref,name\nA,x\n", encoding="utf-8")
    with pytest.raises(cost.InputError, match="必需列"):
        cost.load_bom(p)


# ------------------------------------------------------------ 仓库里的真实价格缓存和示例


def test_repo_price_cache_has_sources():
    prices = cost.load_prices(MFG / "prices")       # 缺链接/日期/依据会直接抛错
    assert prices
    for e in prices.values():
        assert e.date
        if e.status in ("quote", "unverified"):
            assert e.source_url.startswith("https://")
        if e.status != "quote":
            assert e.basis
    assert sum(e.status == "quote" for e in prices.values()) >= 10


def test_example_bom_two_tiers(tmp_path):
    bom = MFG / "examples" / "generic-esp32s3-gadget.bom.csv"
    rc = cost.main([str(bom), "--prices", str(MFG / "prices"), "--qty", "100", "1000",
                    "--out", str(tmp_path), "--strict"])
    assert rc == 0
    with (tmp_path / "summary.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert [int(r["qty"]) for r in rows] == [100, 1000]
    for r in rows:
        shares = sum(float(r[f"{s}_share"]) for s in cost.STATUSES)
        assert shares == pytest.approx(1.0, abs=1e-3)
    assert float(rows[1]["per_unit"]) < float(rows[0]["per_unit"])  # 批量越大单台越便宜
