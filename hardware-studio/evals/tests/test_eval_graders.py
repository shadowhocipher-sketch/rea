"""The graders must tell right from wrong: a deliberately wrong answer scores 0 for every task,
and a correct answer (built from the answer key, not from the tools) scores 1 where one can be
built without running the tools.  Also checks the task set itself (20 tasks, A-G coverage)."""
import importlib.util
import sys
from collections import Counter
from pathlib import Path

import pytest

EVALS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALS))
import run  # noqa: E402

SRC = "[DS 表 1](https://x.example/ds.pdf) · S · 2026-11-01"


def task(prefix):
    d = next(p for p in (EVALS / "tasks").iterdir() if p.name.startswith(prefix))
    spec = importlib.util.spec_from_file_location(f"t_{d.name}", d / "grade.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ task set


def test_twenty_tasks_cover_every_line_twice():
    dirs = run.task_dirs()
    assert len(dirs) == 20
    metas = [task(d.name).META for d in dirs]
    assert len({m["id"] for m in metas}) == 20
    lines = Counter(m["line"] for m in metas)
    assert all(lines[x] >= 2 for x in "ABCDEFG"), lines
    assert sum(m["kind"] == "gap" for m in metas) >= 4
    for d in dirs:
        assert (d / "task.md").read_text(encoding="utf-8").strip(), d


def test_runner_scores_a_crashing_grader_zero(tmp_path, monkeypatch):
    bad = tmp_path / "z99_broken"
    bad.mkdir()
    (bad / "grade.py").write_text("META={'id':'z99','line':'H','title':'x','kind':'capability'}\n"
                                  "def produce(ctx):\n    raise RuntimeError('boom')\n"
                                  "def score(a):\n    return 1.0, 'never'\n", encoding="utf-8")
    rec = run.run_one(bad)
    assert rec["score"] == 0.0 and rec["crashed"] and "boom" in rec["reason"]


def test_runner_end_to_end_fast_subset(capsys):
    assert run.main(["--only", "d03", "g01", "--no-write"]) == 0
    out = capsys.readouterr().out
    assert "总分 **2.00 / 2**" in out


# ------------------------------------------------------------------ wrong answers -> 0

WRONG = {
    "a01": {"pins": [0, 9, 46], "strap_row": "| Strapping | GPIO0、GPIO9、GPIO46 | 记忆 |",
            "gpio45_row": "| GPIO45 | 普通 IO | 无 |", "gpio3_row": "| GPIO3 | 未查到 | 未查到 |"},
    "a02": {"charger": "TP4056", "charger_row": "| 充电 | TP4056 | 没有来源 |", "protector": None, "protector_row": "",
            "cc_row": f"| CC1/CC2 | 10 kΩ 下拉 | {SRC} |", "float_row": f"| 浮充电压 | 4.35 V | {SRC} |",
            "ocp_row": f"| 过充保护电压 | 3.9 V | {SRC} |", "odp_row": f"| 过放保护电压 | 3.2 V | {SRC} |"},
    "a03": {"mcp73831": {"page": "knowledge/power/mcp73831.md", "sourced_rows": 2, "check_ok": False}, "gauge": None},
    "a04": {"busy_high": f"| BUSY | 低 = 忙 | {SRC} |", "sleep_exit_hw_reset": "| 深睡 | 发 0x12 软复位退出 | 无 |",
            "cmd_deep_sleep_10h": f"| 深睡 | 命令 0x07 | {SRC} |", "cmd_master_activation_20h": ""},
    "b01": {"exit": 1, "ok": False, "checks": {"interference_zero": False, "usb_plug_fully_inserts": False},
            "bbox_size": [70, 45, 30], "usb_probe_blocked": 112, "usb_probe_n": 112, "control_inside": False,
            "battery_probe_blocked": 30, "battery_probe_n": 252},
    "b02": {"exit": 0, "ok": True, "pairs": [["module_a", "module_c", 0.5]], "total": 0.5},
    "c01": {"exit": 1, "console_done": False, "stop_reason": "exception", "virtual_ms": 60000, "frames": 1,
            "frame_size": [250, 122], "full": 1, "partial": 0, "refresh_ms": 3000},
    "c02": {"exit": 1, "events": [["button", "click", 1030], ["button", "click", 1060], ["button", "click", 3100]]},
    "c03": {"exit": 1, "stop_reason": "exception", "frames": 1, "count": None, "blinks": None},
    "c04": {"template": None, "status_header": False, "stop_reason": None},
    "d01": {"exit": 0, "tiers": {100: {"per_unit": 5.90596, "quote": 254.796, "unverified": 225.8, "estimate": 110.0,
                                       "missing": 1},
                                 1000: {"per_unit": 5.2325, "quote": 2177.496, "unverified": 1955.0,
                                        "estimate": 1100.0, "missing": 1}}},
    "d02": {"exit": 0, "quote_share": {100: 0.0, 1000: 0.0}},
    "d03": {"exit": 0, "output": "价格缓存检查通过：5 条", "lib_exit": 2},
    "e01": {"exit": 0, "items": ["EU-05 电磁兼容指令 EMC 2014/30/EU **依据**：Directive 2014/30/EU",
                                 "EU-06 LVD **依据**：Directive 2014/35/EU",
                                 "EU-10 电池法规 **依据**：Regulation (EU) 2023/1542",
                                 "EU-13 玩具 **依据**：Directive 2009/48/EC",
                                 "US-05 Reese's Law **依据**：16 CFR part 1263",
                                 "UK-02 **依据**：The Electromagnetic Compatibility Regulations 2016"]},
    "e02": {"exit": 0, "items": ["EU-02 通用充电器 **依据**：Directive (EU) 2022/2380",
                                 "EU-06 LVD **依据**：Directive 2014/35/EU", "US-07 DOE **依据**：10 CFR 430.32(w)",
                                 "EU-05 EMC **依据**：Directive 2014/30/EU", "US-04 FCC Cyber Trust Mark **依据**：x"]},
    "e03": {"total": 52, "unverified": 10, "unverified_without_doubts": ["CN-01"], "without_source_url": []},
    "f01": {"exit": 1, "drawn": [[["MCU.3V3", "EPD.VCC"], "+3V3", "power", 2]], "missing_check": [0, False],
            "extra_check": [0, False]},
    "f02": {"exit": 1, "file": None},
    "g01": {"exit": 1, "flagged": ["工作电压", "参考价", "内部上拉", "论坛说法", "代码块示例"]},
    "g02": {"total": {"knowledge/x.md": 10}, "bad": {"knowledge/x.md": 10}},
}


@pytest.mark.parametrize("tid", sorted(WRONG))
def test_wrong_answer_scores_zero(tid):
    s, reason = task(tid).score(WRONG[tid])
    assert s == 0.0, (tid, s, reason)


def test_every_task_has_a_wrong_answer_case():
    assert {task(d.name).META["id"] for d in run.task_dirs()} == set(WRONG)


# ------------------------------------------------------------------ right answers -> 1 (from the keys)


def test_right_answers_score_one():
    a01 = task("a01")
    assert a01.score({"pins": [0, 3, 45, 46], "strap_row": f"| Strapping | GPIO0、3、45、46 | {SRC} |",
                      "gpio45_row": f"| GPIO45 | VDD_SPI 电压 | {SRC} |",
                      "gpio3_row": f"| GPIO3 | JTAG 信号源 | {SRC} |"})[0] == 1.0
    a04 = task("a04")
    assert a04.score({"busy_high": f"| BUSY | 高 = 忙 | {SRC} |",
                      "sleep_exit_hw_reset": f"| RES# | 退出深睡只能硬件复位 | {SRC} |",
                      "cmd_deep_sleep_10h": f"| 深睡 | 10h | {SRC} |",
                      "cmd_master_activation_20h": f"| 刷新 | 20h Master Activation | {SRC} |"})[0] == 1.0
    b02 = task("b02")
    assert b02.score({"exit": 1, "ok": False, "total": 500.0,
                      "pairs": [["module_a", "module_b", 400.0], ["bottom", "module_d", 100.0]]})[0] == 1.0
    c01 = task("c01")
    assert c01.score({"exit": 0, "console_done": True, "stop_reason": "finished", "virtual_ms": c01.VIRTUAL_MS,
                      "frames": 11, "frame_size": [200, 200], "full": 3, "partial": 8,
                      "refresh_ms": c01.REFRESH_MS})[0] == 1.0
    c02 = task("c02")
    assert c02.score({"exit": 1, "events": [list(k) for k in c02.KEY]})[0] == 1.0
    d01 = task("d01")
    assert d01.score({"exit": 0, "tiers": {q: dict(v, missing=0) for q, v in d01.KEY.items()}})[0] == 1.0
    e01 = task("e01")
    items = ["RED **依据**：Directive 2014/53/EU", "DA **依据**：Delegated Regulation (EU) 2022/30",
             "RoHS **依据**：Directive 2011/65/EU", "WEEE **依据**：Directive 2012/19/EU",
             "GPSR **依据**：Regulation (EU) 2023/988", "US-01 FCC Part 15 Subpart C 有意辐射体 **依据**：47 CFR",
             "UK-01 **依据**：The Radio Equipment Regulations 2017", "UK-09 PSTI **依据**：PSTI Act"]
    assert e01.score({"exit": 0, "items": items})[0] == 1.0
    f01 = task("f01")
    drawn = [[sorted(k[0]), k[1], k[2], n] for k, n in f01.expected_wires().items()]
    assert f01.score({"exit": 0, "drawn": drawn, "missing_check": [1, True], "extra_check": [1, True]})[0] == 1.0
    g01 = task("g01")
    assert g01.score({"exit": 1, "flagged": list(g01.MUST_FLAG)})[0] == 1.0


def test_partial_answers_score_between():
    d02 = task("d02")
    s, _ = d02.score({"exit": 0, "quote_share": {100: 0.25, 1000: 0.5}})
    assert s == pytest.approx(0.75)
    e03 = task("e03")
    s, _ = e03.score({"total": 50, "unverified": 20, "unverified_without_doubts": [], "without_source_url": []})
    assert s == pytest.approx(0.5)
