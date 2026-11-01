#!/usr/bin/env python3
"""从 jlcparts 数据镜像里取 JLCPCB/LCSC 阶梯价，生成价格缓存条目（YAML）。

为什么需要它：有些环境（例如受限的云端会话）打不开 jlcpcb.com / lcsc.com，
但能访问 GitHub。yaqwsx/jlcparts 项目每天把 JLCPCB 元件库（含阶梯价、库存）
导出到它的 gh-pages 分支。这些数据来自 JLCPCB（B 级），但我们是经第三方镜像
拿到的，所以生成的条目记 `access: mirror`，并写明镜像的提交号和快照日期。
能直接打开立创/JLCPCB 商品页时，应优先直接查（见 mfg/pricing.md）。

用法：
    # 1) 只拉目录树，不下载全部数据（约几 MB）
    git clone --depth 1 --filter=blob:none --no-checkout -b gh-pages \
        https://github.com/yaqwsx/jlcparts.git /path/to/jlcparts
    # 2) 按立创编号导出
    python mfg/jlcparts_import.py --repo /path/to/jlcparts C725790 C82942 > new.yaml

注意：不要对这个仓库运行 `git ls-tree -l` 之类需要读取全部 blob 的命令，
会触发几百 MB 的按需下载。本脚本只按需读取 lookup 文件和对应分类文件。
本脚本只读数据文件，不包含 jlcparts 的任何代码。
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import subprocess
import sys

import yaml

MIRROR_URL = "https://github.com/yaqwsx/jlcparts/tree/gh-pages"


def _git(repo: str, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", repo, "-c", "gc.auto=0", *args],
        capture_output=True, check=True, timeout=300,
    ).stdout


def _blob(repo: str, path: str) -> bytes:
    return gzip.decompress(_git(repo, "show", f"HEAD:data/{path}"))


def _attr(lut: list, indices: list[int], name: str) -> str | None:
    for i in indices or []:
        attr_name, spec = lut[i]
        if attr_name == name:
            vals = [v[0] for v in spec["values"].values()]
            return " ".join(str(v) for v in vals)
    return None


def lookup(repo: str, codes: list[str]) -> tuple[list[dict], list[str]]:
    commit, commit_date = _git(repo, "log", "-1", "--format=%H %cs").decode().split()
    lut = json.loads(_blob(repo, "attributes-lut.json.gz"))
    lookups: dict[str, dict] = {}
    files: dict[str, list] = {}
    entries, missing = [], []
    for code in codes:
        n = int(code.lstrip("Cc"))
        lk = f"lookup-{n // 100000:05d}.json.gz"
        if lk not in lookups:
            try:
                lookups[lk] = json.loads(_blob(repo, lk))
            except subprocess.CalledProcessError:
                lookups[lk] = {}
        fname = lookups[lk].get(code)
        if not fname:
            missing.append(code)
            continue
        if fname not in files:
            lines = _blob(repo, fname).decode().splitlines()
            files[fname] = [json.loads(x) for x in lines[1:] if x.strip()]
        rec = next((r for r in files[fname] if r[0] == code), None)
        if rec is None:
            missing.append(code)
            continue
        breaks = [{"qty": p["qFrom"], "price": p["price"]} for p in rec[5]]
        entries.append({
            "key": f"lcsc:{code}",
            "mpn": rec[1],
            "manufacturer": _attr(lut, rec[8], "Manufacturer"),
            "package": _attr(lut, rec[8], "Package"),
            "jlc_class": _attr(lut, rec[8], "Basic/Extended"),
            "joints": rec[2],
            "description": rec[3][:200],
            "currency": "USD",
            "moq": breaks[0]["qty"] if breaks else 1,
            "breaks": breaks,
            "stock": rec[9],
            "status": "quote",
            "level": "B",
            "access": "mirror",
            "source_url": f"https://jlcpcb.com/partdetail/{code}",
            "alt_url": f"https://www.lcsc.com/product-detail/{code}.html",
            "mirror": f"{MIRROR_URL} @ {commit[:7]}（快照 {commit_date}）",
            "date": dt.date.today().isoformat(),
            "basis": "",
            "note": "JLCPCB 元件库价格（贴片下单价），经 jlcparts 镜像取得；下单前在商品页复核",
        })
    return entries, missing


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True, help="jlcparts gh-pages 的本地部分克隆路径")
    ap.add_argument("codes", nargs="+", help="立创编号，如 C725790")
    a = ap.parse_args(argv)
    entries, missing = lookup(a.repo, a.codes)
    yaml.safe_dump(entries, sys.stdout, allow_unicode=True, sort_keys=False)
    for code in missing:
        print(f"# 未查到：{code} 不在镜像 lookup 中（镜像只收录部分编号区间）", file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
