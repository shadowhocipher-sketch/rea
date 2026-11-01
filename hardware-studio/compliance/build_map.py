#!/usr/bin/env python3
"""由 data/requirements.yaml 生成 map.md（总表 + 正文）。

这是资料整理，不是法律意见。

    python build_map.py          # 重新生成 map.md
    python build_map.py --check  # 只检查 map.md 是否与 YAML 一致（不一致时退出码 1）

requirements.yaml 每条要求的字段：
    id            市场前缀 + 序号，如 CN-01
    market        CN / EU / US / UK / AU
    features      在总表中出现的特征行（base/wireless/connected/lithium/coin/adapter/children）
    name          名称
    instrument    法规名称和编号
    requirement   要求是什么
    applies_when  适用条件（文字）
    trigger       触发条件 {all: [...], any: [...], none: [...]}，供 checklist.py 使用
    evidence      证据形式（见 evidence_types）
    evidence_note 证据形式说明
    sources       [{title, url, level(S/A/B/C), kind, access(search/pattern)}]
    checked       查询日期
    status        已核实 / 待核实
    doubts        疑点（待核实时必填）
    notes         备注
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from checklist import DATA, load_data  # noqa: E402

MAP = HERE / "map.md"
FEATURE_ORDER = ("base", "wireless", "connected", "lithium", "coin", "adapter", "children")


def cell_ids(data: dict, feature: str, market: str) -> list[dict]:
    return [r for r in data["requirements"] if r["market"] == market and feature in r["features"]]


def _link(r: dict) -> str:
    flag = "" if r["status"] == "已核实" else "⚠"
    return f"[{r['id']}](#{r['id']}){flag}"


def render_matrix(data: dict) -> str:
    markets = list(data["markets"])
    head = "| 特征 \\ 市场 | " + " | ".join(f"{m} {data['markets'][m]}" for m in markets) + " |"
    sep = "|---|" + "---|" * len(markets)
    rows = [head, sep]
    for f in FEATURE_ORDER:
        cells = []
        for m in markets:
            ids = cell_ids(data, f, m)
            cells.append("、".join(_link(r) for r in ids) if ids else "（无条目）")
        rows.append(f"| {data['features'][f]} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def render_source(s: dict, checked: str) -> str:
    note = "（按官方 URL 规则拼出，本次未在搜索结果中见到，使用前打开核对）" if s["access"] == "pattern" else ""
    return f"  - {s['kind']}：[{s['title']}]({s['url']}) · {s['level']} · {checked}{note}"


def render_requirement(data: dict, r: dict) -> str:
    ev = data["evidence_types"][r["evidence"]]
    status = "已核实" if r["status"] == "已核实" else "**待核实**"
    feats = "、".join(data["features"][f] for f in r["features"])
    out = [
        f'<a id="{r["id"]}"></a>',
        f"### {r['id']} {r['name']}",
        "",
        f"- 状态：{status} · 查询日期 {r['checked']}",
        f"- 总表位置：{feats}",
        f"- 依据：{r['instrument']}",
        f"- 要求：{r['requirement'].strip()}",
        f"- 适用条件：{r['applies_when'].strip()}",
        f"- 证据形式：{ev}。{r.get('evidence_note', '').strip()}",
        "- 来源：",
    ]
    out += [render_source(s, r["checked"]) for s in r["sources"]]
    if r.get("doubts"):
        out.append(f"- 疑点：{r['doubts'].strip()}")
    if r.get("notes"):
        out.append(f"- 备注：{r['notes'].strip()}")
    out.append("")
    return "\n".join(out)


def render_map(data: dict) -> str:
    reqs = data["requirements"]
    n_ok = sum(1 for r in reqs if r["status"] == "已核实")
    n_pending = len(reqs) - n_ok
    lines = [
        "# 合规地图（小型电子产品）",
        "",
        "> **这是资料整理，不是法律意见，也不是合规结论。** 本文件只按产品特征列出各市场可能涉及的法规和证据形式，",
        "> 方便提前规划。产品是否适用、具体怎么做，以法规原文和认证机构 / 检测机构的书面意见为准。",
        "",
        "本文件由 `build_map.py` 从 `data/requirements.yaml` 生成，**不要手改**；改 YAML 后重新生成。",
        "按产品出清单用 `checklist.py`，用法见 `.claude/skills/compliance-map/SKILL.md`。",
        "",
        "## 查询方法和局限",
        "",
        data["meta"]["method"].strip(),
        "",
        "来源级别按 `.claude/skills/research-method/SKILL.md`：S = 法规原文 / 监管机构原文；A = 监管机构或政府的解读、指南、转载；"
        "C = 第三方（只作线索）。",
        "",
        f"共 {len(reqs)} 条：已核实 {n_ok} 条，待核实 {n_pending} 条。",
        "",
        "## 总表：特征 × 市场",
        "",
        "格子里是要求编号，点击跳到正文；带 ⚠ 的是待核实。“基础”行是所有电子产品都要看的条目。",
        "",
        render_matrix(data),
        "",
        "证据形式：" + "；".join(f"{k} = {v}" for k, v in data["evidence_types"].items()) + "。",
        "",
        "## 正文",
        "",
    ]
    for m, mname in data["markets"].items():
        lines += [f"## {m} · {mname}", ""]
        for r in reqs:
            if r["market"] == m:
                lines.append(render_requirement(data, r))
    lines += [
        "---",
        "",
        "再次说明：这是资料整理，不是法律意见。",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true", help="只检查一致性")
    p.add_argument("--data", type=Path, default=DATA)
    p.add_argument("--map", type=Path, default=MAP)
    a = p.parse_args(sys.argv[1:] if argv is None else argv)
    text = render_map(load_data(a.data))
    if a.check:
        current = a.map.read_text(encoding="utf-8") if a.map.exists() else ""
        if current != text:
            print(f"{a.map} 与 {a.data} 不一致，请运行 python build_map.py 重新生成", file=sys.stderr)
            return 1
        print("map.md 与 requirements.yaml 一致")
        return 0
    a.map.write_text(text, encoding="utf-8")
    print(f"已写入 {a.map}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
