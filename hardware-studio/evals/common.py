"""Shared helpers for the self-test graders in evals/tasks/*/grade.py.

Every task directory holds:
  task.md   - the task statement a future session would be given
  grade.py  - defines
                META     = {"id", "line", "title", "kind"}   (kind: capability | gap)
                produce(ctx) -> answer dict   runs the library's tools / reads its content
                score(answer) -> (float 0..1, reason str)
                                compares the answer with an answer key that was worked
                                out independently (by hand / from primary knowledge),
                                never by the tool under test
  other files - fixtures and the answer key (expected.yaml / comments in grade.py)

Graders are split into produce/score so evals/tests can feed deliberately wrong
answers into score() and prove it returns 0.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # hardware-studio/
EVALS = ROOT / "evals"
PY = sys.executable                                  # run tools with the same interpreter


@dataclass
class Ctx:
    root: Path
    work: Path            # scratch directory for this task (deleted after the run)

    def run(self, args, timeout=600, cwd=None, env=None):
        """Run a command (list), return CompletedProcess with text output."""
        e = dict(os.environ)
        e.setdefault("PYTHONIOENCODING", "utf-8")
        if env:
            e.update(env)
        return subprocess.run([str(a) for a in args], cwd=str(cwd or self.root), env=e,
                              capture_output=True, text=True, timeout=timeout)

    def py(self, *args, timeout=600, cwd=None):
        return self.run([PY, *args], timeout=timeout, cwd=cwd)


def new_ctx(root: Path | None = None) -> tuple[Ctx, tempfile.TemporaryDirectory]:
    td = tempfile.TemporaryDirectory(prefix="hs_eval_")
    return Ctx(root=Path(root or ROOT), work=Path(td.name)), td


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def weighted(parts: list[tuple[float, bool, str]]) -> tuple[float, str]:
    """parts: (weight, passed, description) -> (score, reason).  Weights need not sum to 1."""
    tot = sum(w for w, _, _ in parts) or 1.0
    got = sum(w for w, ok, _ in parts if ok)
    reason = "；".join(("✓ " if ok else "✗ ") + d for _, ok, d in parts)
    return round(got / tot, 4), reason


def rel_close(a, b, tol) -> bool:
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    return abs(a - b) <= tol * max(abs(b), 1e-12)


def task_dir(file: str) -> Path:
    return Path(file).resolve().parent


# ------------------------------------------------------------ markdown helpers
import re as _re

LINK_RE = _re.compile(r"https?://\S+")
DATE_RE = _re.compile(r"\b20\d\d-\d\d-\d\d\b")
LEVEL_RE = _re.compile(r"·\s*[SABC]\b")


def table_rows(path: Path) -> list[tuple[int, list[str], str]]:
    """Data rows of every Markdown table in a file: (line number, cells, raw line).
    Header rows (the row before a |---| separator) and separator rows are skipped."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    out, in_code = [], False
    for i, ln in enumerate(lines):
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        s = ln.strip()
        if in_code or not (s.startswith("|") and s.count("|") >= 2):
            continue
        if _re.fullmatch(r"\|?[\s:\-|]+\|?", s):
            continue
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        if _re.fullmatch(r"\|?[\s:\-|]+\|?", nxt) and "-" in nxt:
            continue                                   # header row
        cells = [c.strip() for c in s.strip("|").split("|")]
        out.append((i + 1, cells, ln))
    return out


def has_source(text: str) -> bool:
    """research-method: a fact needs link + level + date (unverified markers alone do not count here)."""
    return bool(LINK_RE.search(text) and DATE_RE.search(text) and LEVEL_RE.search(text))
