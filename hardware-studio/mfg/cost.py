#!/usr/bin/env python3
"""BOM 成本计算：BOM（CSV）+ 价格缓存（YAML 目录）+ 数量档 → 每档单价、总价、明细表。

用法：
    python mfg/cost.py BOM.csv --prices mfg/prices --qty 100 1000 --out out/
    python mfg/cost.py --check-prices mfg/prices        # 只检查价格缓存的来源字段

格式定义见 mfg/README.md。退出码：0 正常；2 输入错误；3 有缺价格的行且用了 --strict。
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# ---------------------------------------------------------------- 常量

CATEGORIES = {
    "electronic": ("electronic", "电子件"),
    "mechanical": ("mechanical", "结构件"),
    "module": ("module", "外购模块"),
    "packaging": ("packaging", "包装"),
    "process": ("process", "加工费"),
}
CATEGORY_LABEL = {k: v[1] for k, v in CATEGORIES.items()}
_CATEGORY_ALIAS = {alias.lower(): k for k, aliases in CATEGORIES.items() for alias in aliases}

COST_MODES = ("unit", "batch", "per_joint", "per_extended_type")
STATUSES = ("quote", "unverified", "estimate")
STATUS_LABEL = {"quote": "实查", "unverified": "待核实", "estimate": "估算", "missing": "缺价格", "dnp": "不贴"}

BOM_REQUIRED = ("ref", "name", "qty_per_unit", "category")
DETAIL_COLUMNS = (
    "ref", "name", "category", "mpn", "price_key", "cost_mode", "qty_per_unit",
    "need", "order_qty", "unit_price", "line_total", "per_product", "leftover",
    "status", "currency", "source_url", "date", "note",
)


class InputError(Exception):
    """BOM 或价格缓存的格式错误。"""


# ---------------------------------------------------------------- 价格缓存


@dataclass(frozen=True)
class PriceBreak:
    qty: int
    price: float


@dataclass
class PriceEntry:
    key: str
    currency: str
    breaks: list[PriceBreak]
    status: str
    moq: int = 1
    order_multiple: int = 1
    source_url: str = ""
    date: str = ""
    basis: str = ""
    jlc_class: str | None = None
    joints: float | None = None
    mpn: str = ""
    origin: str = ""

    def price_at(self, qty: int) -> float:
        """数量 qty 落在哪一档就用哪一档；低于第一档按第一档。"""
        price = self.breaks[0].price
        for b in self.breaks:
            if qty >= b.qty:
                price = b.price
        return price


def _problems(e: dict) -> list[str]:
    out = []
    status = e.get("status")
    if status not in STATUSES:
        out.append(f"status 必须是 {STATUSES} 之一，现在是 {status!r}")
    if not e.get("currency"):
        out.append("缺 currency")
    if not e.get("breaks"):
        out.append("缺 breaks（阶梯价）")
    if not e.get("date"):
        out.append("缺 date（查询日期）")
    if status in ("quote", "unverified") and not e.get("source_url"):
        out.append("实查/待核实条目必须有 source_url")
    if status in ("unverified", "estimate") and not e.get("basis"):
        out.append("待核实/估算条目必须写 basis（依据）")
    for b in e.get("breaks") or []:
        if not isinstance(b, dict) or "qty" not in b or "price" not in b:
            out.append(f"阶梯价格式错误：{b!r}")
        elif b["qty"] < 1 or b["price"] < 0:
            out.append(f"阶梯价数值错误：{b!r}")
    return out


def load_prices(path: str | Path) -> dict[str, PriceEntry]:
    """读取一个 YAML 文件或目录下所有 *.yaml。重复的 key 或缺来源字段都报错。"""
    path = Path(path)
    files = sorted(path.glob("*.yaml")) + sorted(path.glob("*.yml")) if path.is_dir() else [path]
    if not files:
        raise InputError(f"价格缓存为空：{path}")
    prices: dict[str, PriceEntry] = {}
    errors: list[str] = []
    for f in files:
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or []
        if not isinstance(data, list):
            raise InputError(f"{f}: 顶层必须是条目列表")
        for e in data:
            key = e.get("key") if isinstance(e, dict) else None
            if not key:
                errors.append(f"{f}: 有条目缺 key")
                continue
            if key in prices:
                errors.append(f"{f}: key 重复 {key}（已在 {prices[key].origin}）")
                continue
            probs = _problems(e)
            if probs:
                errors.extend(f"{f}: {key}: {p}" for p in probs)
                continue
            breaks = sorted((PriceBreak(int(b["qty"]), float(b["price"])) for b in e["breaks"]),
                            key=lambda b: b.qty)
            prices[key] = PriceEntry(
                key=key, currency=str(e["currency"]).upper(), breaks=breaks, status=e["status"],
                moq=int(e.get("moq") or breaks[0].qty), order_multiple=int(e.get("order_multiple") or 1),
                source_url=e.get("source_url") or "", date=str(e.get("date") or ""),
                basis=e.get("basis") or "", jlc_class=e.get("jlc_class"),
                joints=float(e["joints"]) if e.get("joints") is not None else None,
                mpn=str(e.get("mpn") or ""), origin=str(f),
            )
    if errors:
        raise InputError("价格缓存有错误：\n  " + "\n  ".join(errors))
    return prices


# ---------------------------------------------------------------- BOM


@dataclass
class BomLine:
    ref: str
    name: str
    qty_per_unit: float
    category: str
    mpn: str = ""
    manufacturer: str = ""
    package: str = ""
    lcsc: str = ""
    price_key: str = ""
    cost_mode: str = "unit"
    attrition: float | None = None
    joints: float | None = None
    dnp: bool = False
    note: str = ""


def _num(value: str, what: str, row: int) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value.rstrip("%")) / 100 if value.endswith("%") else float(value)
    except ValueError:
        raise InputError(f"BOM 第 {row} 行：{what} 不是数字：{value!r}") from None


def load_bom(path: str | Path) -> list[BomLine]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if any((v or "").strip() for v in r.values())]
        header = rows[0].keys() if rows else []
    missing = [c for c in BOM_REQUIRED if c not in header]
    if missing:
        raise InputError(f"BOM 缺必需列：{missing}（见 mfg/README.md）")
    lines = []
    for i, r in enumerate(rows, start=2):
        g = lambda k: (r.get(k) or "").strip()  # noqa: E731
        cat = _CATEGORY_ALIAS.get(g("category").lower())
        if cat is None:
            raise InputError(f"BOM 第 {i} 行：类别 {g('category')!r} 不认识，可用：{list(CATEGORIES)} 或中文名")
        mode = g("cost_mode") or "unit"
        if mode not in COST_MODES:
            raise InputError(f"BOM 第 {i} 行：计费方式 {mode!r} 不认识，可用：{COST_MODES}")
        qty = _num(g("qty_per_unit"), "每台用量", i)
        if qty is None or qty < 0:
            raise InputError(f"BOM 第 {i} 行：每台用量必须是非负数")
        lcsc = g("lcsc")
        lines.append(BomLine(
            ref=g("ref"), name=g("name"), qty_per_unit=qty, category=cat, mpn=g("mpn"),
            manufacturer=g("manufacturer"), package=g("package"), lcsc=lcsc,
            price_key=g("price_key") or (f"lcsc:{lcsc}" if lcsc else ""),
            cost_mode=mode, attrition=_num(g("attrition"), "损耗率", i),
            joints=_num(g("joints"), "焊点数", i),
            dnp=g("dnp").lower() in ("y", "yes", "1", "true", "dnp", "是"), note=g("note"),
        ))
    return lines


# ---------------------------------------------------------------- 计算


@dataclass
class LineResult:
    line: BomLine
    need: float
    order_qty: int | None
    unit_price: float | None
    line_total: float | None
    status: str
    entry: PriceEntry | None
    note: str = ""


@dataclass
class TierResult:
    qty: int
    currency: str
    lines: list[LineResult]
    warnings: list[str] = field(default_factory=list)

    @property
    def priced(self) -> list[LineResult]:
        return [r for r in self.lines if r.line_total is not None]

    @property
    def total(self) -> float:
        return sum(r.line_total for r in self.priced)

    @property
    def per_unit(self) -> float:
        return self.total / self.qty

    @property
    def missing(self) -> list[LineResult]:
        return [r for r in self.lines if r.status == "missing"]

    def by_status(self) -> dict[str, float]:
        out = {s: 0.0 for s in STATUSES}
        for r in self.priced:
            out[r.status] += r.line_total
        return out

    def share(self) -> dict[str, float]:
        tot = self.total
        return {s: (v / tot if tot else 0.0) for s, v in self.by_status().items()}

    def by_category(self) -> dict[str, float]:
        out = {c: 0.0 for c in CATEGORIES}
        for r in self.priced:
            out[r.line.category] += r.line_total
        return out

    def one_time(self) -> float:
        return sum(r.line_total for r in self.priced if r.line.cost_mode in ("batch", "per_extended_type"))


def order_quantity(need: float, entry: PriceEntry, optimize: bool = True) -> int:
    """采购数量：向上取整 → 不低于 MOQ → 按包装倍数取整 → （可选）多买到下一档反而更便宜就多买。"""
    q = max(math.ceil(need - 1e-9), entry.moq, 0)
    m = max(entry.order_multiple, 1)
    q = math.ceil(q / m) * m
    if optimize and q > 0:
        best_q, best_cost = q, q * entry.price_at(q)
        for b in entry.breaks:
            bq = math.ceil(b.qty / m) * m
            if bq > q and bq * entry.price_at(bq) < best_cost - 1e-12:
                best_q, best_cost = bq, bq * entry.price_at(bq)
        q = best_q
    return q


def _fx(currency: str, out_currency: str, fx: dict[str, float]) -> float:
    if currency == out_currency:
        return 1.0
    if currency not in fx:
        raise InputError(f"价格币种 {currency} 和输出币种 {out_currency} 不同，请用 --fx {currency}=汇率 给出换算")
    return fx[currency]


def compute_tier(bom: list[BomLine], prices: dict[str, PriceEntry], qty: int, *,
                 attrition: float = 0.0, currency: str = "USD", fx: dict[str, float] | None = None,
                 optimize_breaks: bool = True) -> TierResult:
    if qty <= 0:
        raise InputError("数量档必须是正整数")
    fx = fx or {}
    active = [ln for ln in bom if not ln.dnp]
    warnings: list[str] = []

    # 每台焊点数、扩展料种数（给 per_joint / per_extended_type 行用）
    joints_per_unit = 0.0
    no_joints = []
    extended_keys = set()
    for ln in active:
        if ln.category != "electronic" or ln.cost_mode != "unit":
            continue
        entry = prices.get(ln.price_key)
        j = ln.joints if ln.joints is not None else (entry.joints if entry else None)
        if j is None:
            no_joints.append(ln.ref)
        else:
            joints_per_unit += j * ln.qty_per_unit
        if entry and (entry.jlc_class or "").lower() == "extended":
            extended_keys.add(entry.key)

    results = []
    for ln in bom:
        entry = prices.get(ln.price_key) if ln.price_key else None
        if ln.dnp:
            results.append(LineResult(ln, 0, None, None, None, "dnp", entry, "不贴（DNP），不计价"))
            continue
        note = ""
        if ln.cost_mode == "unit":
            rate = ln.attrition if ln.attrition is not None else (0.0 if ln.category == "process" else attrition)
            need = ln.qty_per_unit * qty * (1 + rate)
        elif ln.cost_mode == "batch":
            need = ln.qty_per_unit
        elif ln.cost_mode == "per_joint":
            need = ln.qty_per_unit * joints_per_unit * qty
            note = f"每台焊点 {joints_per_unit:g}"
            if no_joints:
                warnings.append(f"{ln.ref}: 这些行焊点数未知，没有计入：{', '.join(no_joints)}")
        else:  # per_extended_type
            need = ln.qty_per_unit * len(extended_keys)
            note = f"扩展料 {len(extended_keys)} 种"
        if entry is None:
            results.append(LineResult(ln, need, None, None, None, "missing", None,
                                      f"价格缓存里没有 {ln.price_key or '（未填价格来源键）'}"))
            continue
        oq = order_quantity(need, entry, optimize_breaks) if need > 0 else 0
        up = entry.price_at(oq) if oq else entry.breaks[0].price
        k = _fx(entry.currency, currency, fx)
        results.append(LineResult(ln, need, oq, up * k, oq * up * k, entry.status, entry, note))
    tier = TierResult(qty, currency, results, warnings)
    for r in tier.missing:
        tier.warnings.append(f"{r.line.ref} {r.line.name}: 缺价格（{r.note}），总价里没有这一项")
    return tier


# ---------------------------------------------------------------- 输出


def _fmt(v: float | None, nd: int = 4) -> str:
    return "" if v is None else f"{v:.{nd}f}"


def detail_rows(t: TierResult) -> list[dict]:
    rows = []
    for r in t.lines:
        e = r.entry
        rows.append({
            "ref": r.line.ref, "name": r.line.name, "category": CATEGORY_LABEL[r.line.category],
            "mpn": r.line.mpn or (e.mpn if e else ""), "price_key": r.line.price_key,
            "cost_mode": r.line.cost_mode, "qty_per_unit": f"{r.line.qty_per_unit:g}",
            "need": f"{r.need:g}", "order_qty": "" if r.order_qty is None else r.order_qty,
            "unit_price": _fmt(r.unit_price), "line_total": _fmt(r.line_total, 2),
            "per_product": _fmt(None if r.line_total is None else r.line_total / t.qty),
            "leftover": "" if r.order_qty is None or r.line.cost_mode != "unit" else
            f"{max(r.order_qty - r.line.qty_per_unit * t.qty, 0):g}",
            "status": STATUS_LABEL[r.status], "currency": t.currency,
            "source_url": e.source_url if e else "", "date": e.date if e else "",
            "note": "；".join(x for x in (r.note, r.line.note) if x),
        })
    return rows


def summary_row(t: TierResult) -> dict:
    s, sh = t.by_status(), t.share()
    return {
        "qty": t.qty, "currency": t.currency, "total": round(t.total, 2), "per_unit": round(t.per_unit, 4),
        "one_time": round(t.one_time(), 2),
        **{f"{k}_amount": round(v, 2) for k, v in s.items()},
        **{f"{k}_share": round(v, 4) for k, v in sh.items()},
        "missing_lines": len(t.missing),
        **{f"cat_{k}": round(v, 2) for k, v in t.by_category().items()},
    }


def render_markdown(tiers: list[TierResult], bom_path: str, attrition: float) -> str:
    cur = tiers[0].currency
    out = [f"# 成本表：{Path(bom_path).name}", "",
           f"币种 {cur}；损耗率 {attrition:.1%}（加工费行不计损耗）。"
           "\"实查\" = B 级来源的阶梯价；\"待核实\" = 只有搜索摘要；\"估算\" = 推算或假设，依据见价格缓存。", "",
           "## 汇总", "",
           "| 数量 | 总价 | 单台 | 其中一次性费用 | 实查 | 待核实 | 估算 | 缺价格行 |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for t in tiers:
        sh = t.share()
        out.append(f"| {t.qty} | {t.total:.2f} | {t.per_unit:.4f} | {t.one_time():.2f} | "
                   f"{sh['quote']:.1%} | {sh['unverified']:.1%} | {sh['estimate']:.1%} | {len(t.missing)} |")
    out += ["", "## 按类别（单台）", "", "| 数量 | " + " | ".join(CATEGORY_LABEL.values()) + " |",
            "|---:|" + "---:|" * len(CATEGORIES)]
    for t in tiers:
        out.append(f"| {t.qty} | " + " | ".join(f"{v / t.qty:.4f}" for v in t.by_category().values()) + " |")
    for t in tiers:
        out += ["", f"## 明细：{t.qty} 台", "",
                "| 位号 | 名称 | 类别 | 计费 | 需求量 | 采购量 | 单价 | 小计 | 单台 | 状态 | 来源 | 备注 |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|"]
        for r in detail_rows(t):
            src = f"[链接]({r['source_url']}) {r['date']}" if r["source_url"] else r["date"]
            out.append(f"| {r['ref']} | {r['name']} | {r['category']} | {r['cost_mode']} | {r['need']} | "
                       f"{r['order_qty']} | {r['unit_price']} | {r['line_total']} | {r['per_product']} | "
                       f"{r['status']} | {src} | {r['note'].replace('|', '/')} |")
        if t.warnings:
            out += ["", "警告：", ""] + [f"- {w}" for w in t.warnings]
    return "\n".join(out) + "\n"


def write_outputs(tiers: list[TierResult], out_dir: str | Path, bom_path: str, attrition: float) -> list[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for t in tiers:
        p = out_dir / f"cost_{t.qty}.csv"
        with p.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=DETAIL_COLUMNS)
            w.writeheader()
            w.writerows(detail_rows(t))
        written.append(p)
    p = out_dir / "summary.csv"
    rows = [summary_row(t) for t in tiers]
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    written.append(p)
    p = out_dir / "cost.md"
    p.write_text(render_markdown(tiers, bom_path, attrition), encoding="utf-8")
    written.append(p)
    return written


# ---------------------------------------------------------------- CLI


def _parse_fx(items: list[str]) -> dict[str, float]:
    fx = {}
    for it in items or []:
        cur, _, rate = it.partition("=")
        try:
            fx[cur.strip().upper()] = float(rate)
        except ValueError:
            raise InputError(f"--fx 格式应为 CNY=0.14（1 CNY 折合多少输出币种），收到 {it!r}") from None
    return fx


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="BOM 成本计算（格式见 mfg/README.md）")
    ap.add_argument("bom", nargs="?", help="BOM CSV 文件")
    ap.add_argument("--prices", default=str(Path(__file__).with_name("prices")), help="价格缓存目录或 YAML 文件")
    ap.add_argument("--qty", type=int, nargs="+", default=[100], help="数量档，如 --qty 10 100 1000")
    ap.add_argument("--attrition", type=float, default=0.02, help="默认损耗率（0.02 = 2%%），BOM 的 attrition 列可逐行覆盖")
    ap.add_argument("--currency", default="USD", help="输出币种")
    ap.add_argument("--fx", nargs="*", default=[], help="换算，如 CNY=0.139 表示 1 CNY = 0.139 输出币种；须写明汇率来源")
    ap.add_argument("--no-optimize-breaks", action="store_true", help="不自动多买到更便宜的下一档")
    ap.add_argument("--out", help="输出目录（写 cost_<数量>.csv、summary.csv、cost.md）")
    ap.add_argument("--strict", action="store_true", help="有缺价格的行时返回退出码 3")
    ap.add_argument("--check-prices", action="store_true", help="只检查价格缓存，不算成本")
    a = ap.parse_args(argv)
    try:
        prices = load_prices(a.prices)
        if a.check_prices:
            counts = {s: sum(1 for e in prices.values() if e.status == s) for s in STATUSES}
            print(f"价格缓存检查通过：{len(prices)} 条；" +
                  "，".join(f"{STATUS_LABEL[s]} {n}" for s, n in counts.items()))
            return 0
        if not a.bom:
            ap.error("需要 BOM 文件（或用 --check-prices）")
        bom = load_bom(a.bom)
        fx = _parse_fx(a.fx)
        tiers = [compute_tier(bom, prices, q, attrition=a.attrition, currency=a.currency.upper(), fx=fx,
                              optimize_breaks=not a.no_optimize_breaks) for q in a.qty]
    except InputError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    md = render_markdown(tiers, a.bom, a.attrition)
    if a.out:
        for p in write_outputs(tiers, a.out, a.bom, a.attrition):
            print(f"写出 {p}", file=sys.stderr)
    print(md.split("\n## 按类别")[0])
    if any(t.missing for t in tiers):
        print(f"注意：有 {len(tiers[0].missing)} 行缺价格，总价不完整。", file=sys.stderr)
        if a.strict:
            return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
