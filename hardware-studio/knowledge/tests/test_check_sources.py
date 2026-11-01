"""check_sources.py 的测试，包括故意缺来源的反例。"""

from __future__ import annotations

import importlib.util
from pathlib import Path

KNOWLEDGE = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_sources", KNOWLEDGE / "check_sources.py")
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)

GOOD = """# 示例

| 参数 | 值 | 来源 |
|---|---|---|
| 工作电压 | 3.0–3.6 V | [手册 表 1](https://example.com/ds.pdf) · S · 2026-11-01 |
| 价格 | ¥1 | 未查到（查过 https://example.com，页面打不开） |
| 单价 | ¥2 | 估算：按同类器件取中值 |
| 某坑 | 说明 | [论坛](https://example.com/t) · C · 2026-11-01 · 待核实 |

```
| 代码块 | 里的表格 |
|---|---|
| 不检查 | 不检查 |
```
"""

BAD_MISSING_SOURCE = """# 反例

| 参数 | 值 | 来源 |
|---|---|---|
| 工作电压 | 3.0–3.6 V | 数据手册 |
"""


def _write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_good_file_passes(tmp_path):
    p = _write(tmp_path, "good.md", GOOD)
    rows, problems = cs.check_file(p)
    assert rows == 4
    assert problems == []
    assert cs.main([str(p)]) == 0


def test_missing_source_fails(tmp_path, capsys):
    p = _write(tmp_path, "bad.md", BAD_MISSING_SOURCE)
    rows, problems = cs.check_file(p)
    assert rows == 1
    assert len(problems) == 1
    assert "链接" in problems[0].reason and "日期" in problems[0].reason
    assert cs.main([str(p)]) == 1
    out = capsys.readouterr().out
    assert "bad.md:5" in out


def test_link_without_date_or_level_fails():
    assert cs.check_row("| a | 1 | [x](https://example.com) |") is not None
    assert "日期" in cs.check_row("| a | 1 | [x](https://example.com) · S |")
    assert "来源级别" in cs.check_row("| a | 1 | [x](https://example.com) 2026-11-01 |")
    assert cs.check_row("| a | 1 | [x](https://example.com) · A · 2026-11-01 |") is None


def test_invalid_date_rejected():
    assert "日期" in cs.check_row("| a | 1 | [x](https://example.com) · S · 2026-13-45 |")


def test_markers_accepted():
    for marker in ("未查到", "估算", "待核实"):
        assert cs.check_row(f"| a | 1 | {marker} |") is None


def test_table_without_separator_is_ignored(tmp_path):
    p = _write(tmp_path, "notable.md", "| 不是 | 表格 |\n普通文字\n")
    rows, problems = cs.check_file(p)
    assert rows == 0 and problems == []


def test_missing_path_returns_2(tmp_path):
    assert cs.main([str(tmp_path / "nope")]) == 2


def test_real_knowledge_base_passes():
    """整个知识库必须通过来源检查。"""
    files = cs.collect([KNOWLEDGE])
    assert len(files) >= 6 * 3, "六类各至少 2 个器件页 + 1 张选型表"
    problems = []
    for f in files:
        problems.extend(cs.check_file(f)[1])
    assert problems == [], "\n".join(p.format() for p in problems)


def test_each_category_has_two_pages_and_selection():
    for cat in ("mcu", "display", "input", "audio", "power", "wireless"):
        d = KNOWLEDGE / cat
        pages = [p for p in d.glob("*.md") if p.name != "selection.md"]
        assert len(pages) >= 2, cat
        assert (d / "selection.md").is_file(), cat
