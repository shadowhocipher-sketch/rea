#!/usr/bin/env python3
"""New-product helper for the new-product skill (run from hardware-studio/).

    python .claude/skills/new-product/product.py new <name>                 # copy products/_template -> products/<name>
    python .claude/skills/new-product/product.py compliance-yaml products/<name>   # brief.yaml features -> compliance.yaml
    python .claude/skills/new-product/product.py check products/<name> [--step 1 3 5] [--json]

`check` verifies each step's deliverables (see SKILL.md "交付清单") and re-runs the cheap library checks
(wiring cross-check, price-cache rules); it reads the reports the heavier tools already wrote
(cad_out/check_report.json, cost/summary.csv) instead of rebuilding them.
Exit code: 0 = every checked step OK; 1 = something missing or failing; 2 = bad arguments.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]          # hardware-studio/
TEMPLATE = ROOT / "products" / "_template"
sys.path.insert(0, str(ROOT / "compliance"))
from checklist import InputError, make_product  # noqa: E402  (compliance owns the feature vocabulary)

STEP_NAMES = {1: "场景与简报", 2: "选型", 3: "开发板原型", 4: "屏幕与交互模拟", 5: "外壳",
              6: "BOM 与成本", 7: "合规", 8: "小批量与出图", 9: "REPORT"}
TODO = re.compile(r"\bTODO\b")


class Result:
    def __init__(self):
        self.items: list[tuple[int, str, bool, str]] = []

    def add(self, step, what, ok, detail=""):
        self.items.append((step, what, bool(ok), detail))

    def ok(self):
        return all(o for _, _, o, _ in self.items)


def _py(*args, timeout=600):
    return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, capture_output=True, text=True,
                          timeout=timeout)


def load_brief(pdir: Path) -> dict:
    p = pdir / "brief.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {} if p.exists() else {}


def compliance_spec(brief: dict) -> dict:
    f = brief.get("features") or {}
    return {"name": brief.get("name") or "未命名产品", "wireless": f.get("wireless") or [],
            "connected": f.get("connected"), "batteries": f.get("batteries") or [],
            "adapter": bool(f.get("adapter")), "children": bool(f.get("children")),
            "markets": (brief.get("market") or {}).get("regions") or []}


# ------------------------------------------------------------------ step checks


def check_brief(pdir, r):
    p = pdir / "brief.yaml"
    if not p.exists():
        r.add(1, "brief.yaml", False, "没有")
        return
    text = p.read_text(encoding="utf-8")
    todos = [i + 1 for i, ln in enumerate(text.splitlines()) if TODO.search(ln.split("#", 1)[0])]
    r.add(1, "brief.yaml 没有 TODO", not todos, f"TODO 在第 {todos} 行" if todos else "")
    b = yaml.safe_load(text) or {}
    sc = b.get("scenario") or {}
    unfilled = [k for k in ("who", "where", "when", "feeling", "interaction")
                if not sc.get(k) or TODO.search(str(sc.get(k)))]
    r.add(1, "场景：who/where/when/feeling/interaction 都填了", not unfilled, f"没填：{unfilled}" if unfilled else "")
    pr = b.get("price") or {}
    qty = pr.get("quantities") or []
    r.add(1, "价格目标和 ≥2 档数量",
          (pr.get("target_unit_cost") or 0) > 0 and len(qty) >= 2 and all(int(q) > 0 for q in qty),
          f"target_unit_cost={pr.get('target_unit_cost')} quantities={qty}")
    try:
        make_product(compliance_spec(b))
        r.add(1, "features / market.regions 取值合法（compliance/checklist.py 校验）", bool(compliance_spec(b)["markets"]))
    except InputError as e:
        r.add(1, "features / market.regions 取值合法", False, str(e))


def check_selection(pdir, r):
    p = pdir / "selection.md"
    if not p.exists():
        r.add(2, "selection.md", False, "没有")
        return
    text = p.read_text(encoding="utf-8")
    r.add(2, "selection.md 没有 TODO", not TODO.search(text))
    pages = sorted(set(re.findall(r"knowledge/[\w/.-]+\.md", text)))
    missing = [x for x in pages if not (ROOT / x).exists()]
    r.add(2, "引用的知识库页都存在", pages and not missing, f"引用 {len(pages)} 页，缺 {missing}")
    k = _py("knowledge/check_sources.py")
    r.add(2, "knowledge/ 来源检查通过（含本次补的页）", k.returncode == 0, k.stdout.strip().splitlines()[-1:])


def check_prototype(pdir, r):
    pins = pdir / "pins.csv"
    if not pins.exists():
        r.add(3, "pins.csv", False, "没有")
    else:
        out = pdir / "out"
        w = _py("diagrams/wiring.py", pins, "--out", out)
        r.add(3, "接线图生成且与 pins.csv 一一对应（wiring.py 退出码 0）", w.returncode == 0,
              (w.stdout + w.stderr).strip().splitlines()[-1:])
        r.add(3, "pins.csv 没有 TODO", not TODO.search(pins.read_text(encoding="utf-8")))
    fw = sorted((pdir / "firmware").glob("*.py")) if (pdir / "firmware").is_dir() else []
    real = [f for f in fw if "raise SystemExit(\"replace this file" not in f.read_text(encoding="utf-8")]
    r.add(3, "firmware/*.py（不是模板占位）", bool(real), [f.name for f in fw])


def check_sim(pdir, r):
    imgs = sorted(p for p in pdir.rglob("sim_*") if p.suffix.lower() in (".png", ".gif"))
    r.add(4, "模拟图 sim_*.png/gif", bool(imgs), [str(p.relative_to(pdir)) for p in imgs][:6])


def check_enclosure(pdir, r):
    r.add(5, "enclosure.yaml", (pdir / "enclosure.yaml").exists())
    rep = pdir / "cad_out" / "check_report.json"
    if not rep.exists():
        r.add(5, "cad_out/check_report.json（build_enclosure.py 输出）", False, "没有，先跑 build_enclosure.py")
        return
    d = json.loads(rep.read_text(encoding="utf-8"))
    c = d.get("checks", {})
    r.add(5, "外壳检查 ok（干涉 0、USB 插到底、平台、参数警告 0）", d.get("ok") is True,
          {k: c.get(k) for k in ("interference_zero", "usb_plug_fully_inserts", "fits_printer_bed", "spec_warnings")})
    stl = sorted((pdir / "cad_out").glob("*.stl"))
    r.add(5, "导出了 STL/STEP", bool(stl), [p.name for p in stl])


def check_bom(pdir, r):
    bom = pdir / "bom.csv"
    r.add(6, "bom.csv", bom.exists())
    p = _py("mfg/cost.py", "--check-prices")
    r.add(6, "价格缓存合规（cost.py --check-prices）", p.returncode == 0, p.stdout.strip()[:120])
    s = pdir / "cost" / "summary.csv"
    if not s.exists():
        r.add(6, "cost/summary.csv（cost.py --out products/<name>/cost）", False, "没有")
        return
    rows = list(csv.DictReader(s.open(encoding="utf-8")))
    r.add(6, "≥2 档数量", len(rows) >= 2, [x["qty"] for x in rows])
    r.add(6, "缺价格行 = 0", all(int(x["missing_lines"]) == 0 for x in rows), [x["missing_lines"] for x in rows])
    brief = load_brief(pdir)
    target = (brief.get("price") or {}).get("target_unit_cost")
    if target:
        big = max(rows, key=lambda x: int(x["qty"]))
        r.add(6, f"最大数量档单台 ≤ brief 目标 {target}（超了回第 2 步换料，或在 REPORT 写明原因）",
              float(big["per_unit"]) <= float(target), f"{big['qty']} 台单台 {big['per_unit']}，"
              f"实查占比 {float(big['quote_share']):.0%}")


def check_compliance(pdir, r):
    cy, cm = pdir / "compliance.yaml", pdir / "compliance_checklist.md"
    r.add(7, "compliance.yaml", cy.exists())
    r.add(7, "compliance_checklist.md", cm.exists())
    if cy.exists() and (pdir / "brief.yaml").exists():
        def norm(spec):
            return {"wireless": sorted(spec.get("wireless") or []), "batteries": sorted(spec.get("batteries") or []),
                    "markets": sorted(m.upper() for m in spec.get("markets") or []),
                    "adapter": bool(spec.get("adapter")), "children": bool(spec.get("children")),
                    "connected": spec.get("connected")}
        want = norm(compliance_spec(load_brief(pdir)))
        have = norm(yaml.safe_load(cy.read_text(encoding="utf-8")) or {})
        diff = [k for k in want if want[k] != have[k]]
        r.add(7, "compliance.yaml 与 brief.yaml 的 features 一致", not diff, f"不一致：{diff}" if diff else "")


def check_batch(pdir, r):
    renders = sorted(pdir.rglob("render_*.png"))
    r.add(8, "渲染图 render_*.png", bool(renders), [str(p.relative_to(pdir)) for p in renders][:6])
    kicad = pdir / "kicad"
    if kicad.is_dir():
        r.add(8, "KiCad 检查报告 kicad-report/summary.md", (pdir / "kicad-report" / "summary.md").exists())


def check_report(pdir, r):
    p = pdir / "REPORT.md"
    if not p.exists():
        r.add(9, "REPORT.md", False, "没有")
        return
    t = p.read_text(encoding="utf-8")
    r.add(9, "REPORT 没有 TODO", not TODO.search(t))
    sections = {m.group(1).strip(): m.group(2) for m in
                re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", t, flags=re.M | re.S)}

    def body(key):
        return next((v for k, v in sections.items() if key in k), "")
    reuse_rows = [ln for ln in body("复用").splitlines()
                  if ln.startswith("|") and not re.fullmatch(r"\|[\s:|-]+\|?", ln.strip())][1:]
    r.add(9, "「复用 / 临时补 / 回写」表每步至少一行", len(reuse_rows) >= 8, f"{len(reuse_rows)} 行")
    for key in ("结论", "交付清单", "待核实"):
        r.add(9, f"「{key}」一节有内容", len(re.sub(r"\s|（.*?）", "", body(key))) >= 10)


CHECKS = {1: check_brief, 2: check_selection, 3: check_prototype, 4: check_sim, 5: check_enclosure,
          6: check_bom, 7: check_compliance, 8: check_batch, 9: check_report}


# ------------------------------------------------------------------ commands


def cmd_new(name):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        print("产品名只用小写字母、数字、连字符", file=sys.stderr)
        return 2
    dst = ROOT / "products" / name
    if dst.exists():
        print(f"已存在：{dst}", file=sys.stderr)
        return 2
    shutil.copytree(TEMPLATE, dst)
    for p in dst.rglob("*"):
        if p.is_file() and p.suffix in (".yaml", ".md", ".py", ".csv"):
            p.write_text(p.read_text(encoding="utf-8").replace("TODO-product-name", name), encoding="utf-8")
    print(f"已创建 {dst.relative_to(ROOT)}；下一步填写 brief.yaml，然后：\n"
          f"  python .claude/skills/new-product/product.py check products/{name} --step 1")
    return 0


def cmd_compliance_yaml(pdir):
    brief = load_brief(pdir)
    if not brief:
        print(f"没有 {pdir / 'brief.yaml'}", file=sys.stderr)
        return 2
    spec = compliance_spec(brief)
    try:
        make_product(spec)
    except InputError as e:
        print(f"brief.yaml 的 features 不合法：{e}", file=sys.stderr)
        return 2
    out = pdir / "compliance.yaml"
    out.write_text("# 由 brief.yaml 生成（product.py compliance-yaml）；改特征请改 brief.yaml 再重新生成\n"
                   + yaml.safe_dump(spec, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"写出 {out}")
    return 0


def cmd_check(pdir, steps, as_json):
    if not pdir.is_dir():
        print(f"没有目录 {pdir}", file=sys.stderr)
        return 2
    r = Result()
    for s in steps:
        CHECKS[s](pdir, r)
    if as_json:
        print(json.dumps([{"step": s, "check": w, "ok": o, "detail": str(d)} for s, w, o, d in r.items],
                         ensure_ascii=False, indent=1))
    else:
        for s, w, o, d in r.items:
            print(f"[{'OK  ' if o else 'FAIL'}] {s}.{STEP_NAMES[s]}：{w}" + (f" —— {d}" if d not in ("", [], None) else ""))
        n_bad = sum(1 for _, _, o, _ in r.items if not o)
        print(f"\n{len(r.items) - n_bad}/{len(r.items)} 项通过")
    return 0 if r.ok() else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="new-product skill helper")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a_new = sub.add_parser("new")
    a_new.add_argument("name")
    a_cy = sub.add_parser("compliance-yaml")
    a_cy.add_argument("product_dir")
    a_ck = sub.add_parser("check")
    a_ck.add_argument("product_dir")
    a_ck.add_argument("--step", type=int, nargs="+", choices=sorted(CHECKS), default=sorted(CHECKS))
    a_ck.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "new":
        return cmd_new(a.name)
    pdir = Path(a.product_dir)
    pdir = pdir if pdir.is_absolute() else (Path.cwd() / pdir)
    if a.cmd == "compliance-yaml":
        return cmd_compliance_yaml(pdir)
    return cmd_check(pdir, a.step, a.json)


if __name__ == "__main__":
    sys.exit(main())
