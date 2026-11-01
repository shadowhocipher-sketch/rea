#!/usr/bin/env python3
"""按产品特征输出合规检查清单（Markdown）。

这是资料整理，不是法律意见。

用法：
    python checklist.py --product examples/a_wifi_desk_usb.yaml
    python checklist.py --wireless wifi,ble --connected --battery lithium \
        --adapter --children --markets CN,EU --out out.md

产品 YAML 格式：
    name: 产品名
    wireless: [wifi, ble]      # 可选值 wifi / ble / other；没有无线写 []
    connected: true            # 是否联网（直接或经手机 App 间接上网）；省略时按"有 Wi-Fi 即联网"推断
    batteries: [lithium]       # 可选值 lithium（可充电锂离子/锂聚合物）/ coin（纽扣电池）；没有写 []
    adapter: false             # 是否随附电源适配器
    children: false            # 是否给儿童用（玩具/儿童产品）
    markets: [CN, EU, US, UK, AU]

数据来自 data/requirements.yaml。
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "requirements.yaml"

WIRELESS_KINDS = ("wifi", "ble", "other")
BATTERY_KINDS = ("lithium", "coin")
ALL_MARKETS = ("CN", "EU", "US", "UK", "AU")
TOKENS = {"always", "wireless", "wifi", "ble", "connected", "lithium", "coin", "adapter", "children"}

DISCLAIMER = (
    "> **这是资料整理，不是法律意见。** 清单只根据你给出的产品特征，从 `compliance/data/requirements.yaml` "
    "里挑出可能相关的法规条目；是否适用、怎么做，以法规原文和认证机构/检测机构的书面意见为准。"
    "标\"待核实\"的条目尤其要确认。"
)


class InputError(ValueError):
    """产品特征输入不合法。"""


@dataclass(frozen=True)
class Product:
    name: str
    wireless: frozenset = field(default_factory=frozenset)
    connected: bool = False
    connected_inferred: bool = False
    batteries: frozenset = field(default_factory=frozenset)
    adapter: bool = False
    children: bool = False
    markets: tuple = ALL_MARKETS

    def tokens(self) -> set[str]:
        t = {"always"}
        if self.wireless:
            t.add("wireless")
            t |= set(self.wireless)
        if self.connected:
            t.add("connected")
        t |= set(self.batteries)
        if self.adapter:
            t.add("adapter")
        if self.children:
            t.add("children")
        return t


def _as_list(value, what: str) -> list[str]:
    if value is None or value is False:
        return []
    if isinstance(value, str):
        value = [v for v in value.replace(" ", "").split(",") if v]
    if not isinstance(value, (list, tuple)):
        raise InputError(f"{what} 应为列表，收到 {value!r}")
    return [str(v).strip().lower() for v in value]


def _as_bool(value, what: str) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    raise InputError(f"{what} 应为 true/false，收到 {value!r}")


def make_product(spec: dict) -> Product:
    """从字典构造 Product，校验取值。"""
    if not isinstance(spec, dict):
        raise InputError("产品描述应为字典")
    unknown = set(spec) - {"name", "wireless", "connected", "batteries", "adapter", "children", "markets", "note"}
    if unknown:
        raise InputError(f"未知字段：{sorted(unknown)}")
    wireless = _as_list(spec.get("wireless"), "wireless")
    for w in wireless:
        if w not in WIRELESS_KINDS:
            raise InputError(f"wireless 取值应为 {WIRELESS_KINDS}，收到 {w!r}")
    batteries = _as_list(spec.get("batteries"), "batteries")
    for b in batteries:
        if b not in BATTERY_KINDS:
            raise InputError(f"batteries 取值应为 {BATTERY_KINDS}，收到 {b!r}")
    markets = [m.upper() for m in _as_list(spec.get("markets") or list(ALL_MARKETS), "markets")]
    for m in markets:
        if m not in ALL_MARKETS:
            raise InputError(f"markets 取值应为 {ALL_MARKETS}，收到 {m!r}")
    if "connected" in spec and spec["connected"] is not None:
        connected = _as_bool(spec["connected"], "connected")
        inferred = False
    else:
        connected = "wifi" in wireless
        inferred = True
    return Product(
        name=str(spec.get("name") or "未命名产品"),
        wireless=frozenset(wireless),
        connected=connected,
        connected_inferred=inferred,
        batteries=frozenset(batteries),
        adapter=_as_bool(spec.get("adapter", False), "adapter"),
        children=_as_bool(spec.get("children", False), "children"),
        markets=tuple(m for m in ALL_MARKETS if m in markets),
    )


_FOLD_SPACE = re.compile(r"(?<=[，。；：、（）！？])\s+|\s+(?=[，。；：、（）！？])")


def _tidy(value):
    """YAML 折叠块会在中文标点后留下空格，读入时统一去掉。"""
    if isinstance(value, str):
        return _FOLD_SPACE.sub("", value)
    if isinstance(value, list):
        return [_tidy(v) for v in value]
    if isinstance(value, dict):
        return {k: _tidy(v) for k, v in value.items()}
    return value


def load_data(path: Path = DATA) -> dict:
    with open(path, encoding="utf-8") as f:
        return _tidy(yaml.safe_load(f))


def trigger_matches(trigger: dict, tokens: set[str]) -> bool:
    """trigger = {all: [...], any: [...], none: [...]}；三部分同时满足才算触发。"""
    all_ = trigger.get("all", [])
    any_ = trigger.get("any", [])
    none_ = trigger.get("none", [])
    for t in (*all_, *any_, *none_):
        if t not in TOKENS:
            raise ValueError(f"未知触发条件 {t!r}")
    if not all(t in tokens for t in all_):
        return False
    if any_ and not any(t in tokens for t in any_):
        return False
    if any(t in tokens for t in none_):
        return False
    return True


def select(data: dict, product: Product) -> list[dict]:
    tokens = product.tokens()
    return [
        r for r in data["requirements"]
        if r["market"] in product.markets and trigger_matches(r["trigger"], tokens)
    ]


def _yn(v: bool) -> str:
    return "是" if v else "否"


def _fmt_sources(r: dict) -> str:
    parts = []
    for s in r["sources"]:
        note = "（链接按官方 URL 规则拼出，未在搜索中见到，请打开核对）" if s.get("access") == "pattern" else ""
        parts.append(f"[{s['title']}]({s['url']}) · {s['level']} · {r['checked']}{note}")
    return "<br>".join(parts)


def render(data: dict, product: Product, selected: list[dict]) -> str:
    ev = data["evidence_types"]
    mk = data["markets"]
    checked = data["meta"]["checked"]
    lines = [f"# 合规检查清单：{product.name}", "", DISCLAIMER, ""]
    lines += [
        f"数据查询日期：{checked}。数据来源：`compliance/data/requirements.yaml`（共 {len(data['requirements'])} 条）。",
        "",
        "## 产品特征",
        "",
        "| 特征 | 取值 |",
        "|---|---|",
        f"| 无线 | {', '.join(sorted(product.wireless)) or '无'} |",
        f"| 联网 | {_yn(product.connected)}{'（未填写，按“有 Wi-Fi 即联网”推断）' if product.connected_inferred else ''} |",
        f"| 电池 | {', '.join(sorted(product.batteries)) or '无'} |",
        f"| 随附电源适配器 | {_yn(product.adapter)} |",
        f"| 儿童用 | {_yn(product.children)} |",
        f"| 目标市场 | {', '.join(product.markets)} |",
        "",
    ]
    hints = []
    if product.wireless and not product.connected:
        hints.append("产品有无线但标为不联网：如果它通过手机 App 间接上网，欧盟 RED 网络安全条款、CRA、英国 PSTI、澳洲智能设备规则都可能适用，"
                     "请把 connected 设为 true 再跑一次对比（待核实）。")
    if "lithium" in product.batteries and not product.adapter:
        hints.append("产品有可充电电池但不随附适配器：只要不在包装里提供充电器，适配器相关条目不会列出；如果随附充电器，请设 adapter: true。")
    if hints:
        lines += ["## 提示", ""] + [f"- {h}" for h in hints] + [""]

    n_total = len(selected)
    n_pending = sum(1 for r in selected if r["status"] != "已核实")
    lines += [f"共 {n_total} 条，其中待核实 {n_pending} 条。", ""]

    for m in product.markets:
        rows = [r for r in selected if r["market"] == m]
        lines += [f"## {m} · {mk[m]}", ""]
        if not rows:
            lines += ["（按当前特征没有匹配的条目。不代表没有要求，请向认证机构确认。）", ""]
            continue
        for r in rows:
            mark = "✅ 已核实" if r["status"] == "已核实" else "⚠️ **待核实**"
            lines += [
                f"### {r['id']} {r['name']}　{mark}",
                "",
                f"- **依据**：{r['instrument']}",
                f"- **要求**：{r['requirement'].strip()}",
                f"- **适用条件**：{r['applies_when'].strip()}",
                f"- **证据形式**：{ev[r['evidence']]}。{r.get('evidence_note', '').strip()}",
                f"- **来源**：{_fmt_sources(r)}",
            ]
            if r.get("doubts"):
                lines.append(f"- **疑点 / 待核实**：{r['doubts'].strip()}")
            if r.get("notes"):
                lines.append(f"- **备注**：{r['notes'].strip()}")
            lines.append("")

    lines += [
        "## 必须找认证机构 / 检测机构确认的事项",
        "",
        "- 上面所有标\"待核实\"的条目；",
        "- 产品归类：是否属于中国 CCC 目录、欧盟通用充电器类别、玩具定义、联网/可连接产品定义；",
        "- 使用已认证无线模组时，整机还需要做哪些测试（中国 SRRC、FCC、RED、ACMA）；",
        "- 测试项目、样机数量、周期和费用。",
        "",
        DISCLAIMER,
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="按产品特征输出合规检查清单（资料整理，不是法律意见）")
    p.add_argument("--product", type=Path, help="产品特征 YAML 文件")
    p.add_argument("--name", help="产品名")
    p.add_argument("--wireless", help="无线类型，逗号分隔：wifi,ble,other")
    p.add_argument("--connected", dest="connected", action="store_true", default=None, help="联网")
    p.add_argument("--not-connected", dest="connected", action="store_false", help="不联网")
    p.add_argument("--battery", help="电池类型，逗号分隔：lithium,coin")
    p.add_argument("--adapter", action="store_true", default=None, help="随附电源适配器")
    p.add_argument("--children", action="store_true", default=None, help="儿童用/玩具")
    p.add_argument("--markets", help="市场，逗号分隔：CN,EU,US,UK,AU（默认全部）")
    p.add_argument("--data", type=Path, default=DATA, help="requirements.yaml 路径")
    p.add_argument("--out", type=Path, help="输出 Markdown 文件；不填则打印")
    return p.parse_args(argv)


def spec_from_args(a: argparse.Namespace) -> dict:
    spec: dict = {}
    if a.product:
        with open(a.product, encoding="utf-8") as f:
            spec = yaml.safe_load(f) or {}
    overrides = {
        "name": a.name,
        "wireless": a.wireless,
        "connected": a.connected,
        "batteries": a.battery,
        "adapter": a.adapter,
        "children": a.children,
        "markets": a.markets,
    }
    for k, v in overrides.items():
        if v is not None:
            spec[k] = v
    return spec


def main(argv: list[str] | None = None) -> int:
    a = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        product = make_product(spec_from_args(a))
    except (InputError, OSError, yaml.YAMLError) as e:
        print(f"输入错误：{e}", file=sys.stderr)
        return 2
    data = load_data(a.data)
    text = render(data, product, select(data, product))
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(text, encoding="utf-8")
        print(f"已写入 {a.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
