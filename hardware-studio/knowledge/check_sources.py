#!/usr/bin/env python3
"""检查 knowledge/ 下 Markdown 表格的每一行数据是否带来源。

规则（与 .claude/skills/research-method/SKILL.md 一致）：
一行数据合格，当且仅当满足下面任意一条：
  1. 同时含有 http(s) 链接、YYYY-MM-DD 日期、来源级别（"· S"、"· A"、"· B"、"· C"）；
  2. 含有标记"未查到"、"估算"或"待核实"（这三种标记本身就说明了可靠程度，
     但页面仍应写清查过哪里、推算依据或冲突点）。

表头行和分隔行（|---|）不检查；``` 代码块里的表格不检查。

用法：
    python knowledge/check_sources.py            # 检查本脚本所在目录
    python knowledge/check_sources.py PATH ...   # 检查指定文件或目录
退出码：0 = 全部合格；1 = 有不合格行；2 = 参数错误（路径不存在）。
只用 Python 标准库。
"""

from __future__ import annotations

import datetime as _dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path

LINK_RE = re.compile(r"https?://[^\s)>\]]+")
DATE_RE = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
LEVEL_RE = re.compile(r"·\s*[SABC](?![A-Za-z])")
MARKERS = ("未查到", "估算", "待核实")
SEPARATOR_RE = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


@dataclass
class Problem:
    path: Path
    line: int
    reason: str
    text: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.reason}: {self.text.strip()}"


def _is_table_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.count("|") >= 2


def _valid_date(text: str) -> bool:
    for y, m, d in DATE_RE.findall(text):
        try:
            _dt.date(int(y), int(m), int(d))
            return True
        except ValueError:
            continue
    return False


def check_row(text: str) -> str | None:
    """返回不合格原因；合格返回 None。"""
    if any(marker in text for marker in MARKERS):
        return None
    missing = []
    if not LINK_RE.search(text):
        missing.append("链接")
    if not _valid_date(text):
        missing.append("日期")
    if not LEVEL_RE.search(text):
        missing.append("来源级别")
    if missing:
        return "缺" + "、".join(missing) + "（且没有 未查到/估算/待核实 标记）"
    return None


def iter_table_rows(lines: list[str]):
    """逐个产出 (行号, 文本)：只产出表格的数据行。"""
    in_fence = False
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if FENCE_RE.match(line):
            in_fence = not in_fence
            i += 1
            continue
        if in_fence or not _is_table_line(line):
            i += 1
            continue
        # 表格开始：第一行是表头，下一行必须是分隔行，否则不当作表格。
        if i + 1 < n and SEPARATOR_RE.match(lines[i + 1].strip()):
            j = i + 2
            while j < n and _is_table_line(lines[j]) and not FENCE_RE.match(lines[j]):
                yield j + 1, lines[j]
                j += 1
            i = j
        else:
            i += 1


def check_file(path: Path) -> tuple[int, list[Problem]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = 0
    problems: list[Problem] = []
    for lineno, text in iter_table_rows(lines):
        rows += 1
        reason = check_row(text)
        if reason:
            problems.append(Problem(path, lineno, reason, text))
    return rows, problems


def collect(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files.extend(sorted(q for q in p.rglob("*.md") if "tests" not in q.relative_to(p).parts))
        elif p.is_file():
            files.append(p)
        else:
            raise FileNotFoundError(str(p))
    return files


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    targets = [Path(a) for a in argv] or [Path(__file__).resolve().parent]
    try:
        files = collect(targets)
    except FileNotFoundError as exc:
        print(f"路径不存在：{exc}", file=sys.stderr)
        return 2
    total_rows = 0
    all_problems: list[Problem] = []
    for f in files:
        rows, problems = check_file(f)
        total_rows += rows
        all_problems.extend(problems)
    for p in all_problems:
        print(p.format())
    status = "不合格" if all_problems else "全部合格"
    print(f"检查 {len(files)} 个文件、{total_rows} 行表格数据：{len(all_problems)} 行不合格，{status}。")
    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())
