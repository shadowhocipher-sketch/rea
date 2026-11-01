#!/usr/bin/env python3
"""用 KiCad 命令行跑 ERC（原理图）和 DRC（PCB），汇总结果。

KiCad 是 GPL 软件；这里只把 `kicad-cli` 当外部程序调用，不复制、不链接它的代码。

用法：
    python mfg/kicad_check.py path/to/project.kicad_pro          # 自动找同名 .kicad_sch / .kicad_pcb
    python mfg/kicad_check.py board.kicad_pcb schematic.kicad_sch
    python mfg/kicad_check.py proj/ --docker kicad/kicad:9.0      # 本机没有 kicad-cli 时用官方 Docker 镜像
    python mfg/kicad_check.py proj/ --out reports/ --fail-on warning

找 kicad-cli 的顺序：--kicad-cli 参数 → 环境变量 KICAD_CLI → PATH 里的 kicad-cli
→ --docker 参数或环境变量 KICAD_DOCKER_IMAGE。需要 KiCad 8 及以上（7.x 的 kicad-cli 没有 erc/drc）。

退出码：0 没有达到失败级别的违规；1 有违规；2 kicad-cli 运行出错或文件不对；4 找不到可用的 kicad-cli。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

INSTALL_HINT = """\
找不到可用的 KiCad 命令行（需要 KiCad 8 或更新版本，`kicad-cli sch erc` / `kicad-cli pcb drc`）。
安装方法任选其一：
  - Ubuntu/Debian：官方 PPA `sudo add-apt-repository ppa:kicad/kicad-9.0-releases && sudo apt install kicad`
    （Ubuntu 24.04 自带源里的 kicad 是 7.0，没有 erc/drc 子命令）
  - macOS：从 https://www.kicad.org/download/ 安装，kicad-cli 在
    /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli，用 --kicad-cli 指定
  - Docker：`docker pull kicad/kicad:9.0`，然后加参数 --docker kicad/kicad:9.0
"""

SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}


class KicadUnavailable(Exception):
    pass


@dataclass
class Runner:
    """封装"怎么调用 kicad-cli"：本机程序或 Docker 镜像。"""
    exe: str | None = None
    docker_image: str | None = None

    def describe(self) -> str:
        return f"docker:{self.docker_image}" if self.docker_image else str(self.exe)

    def run(self, args: list[str], workdir: Path, outdir: Path, timeout: int = 600) -> subprocess.CompletedProcess:
        """args 里的文件路径用 {work}/ 和 {out}/ 占位，由这里换成本机或容器内路径。"""
        if self.docker_image:
            work, out = "/work", "/out"
            cmd = ["docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/tmp",
                   "-v", f"{workdir}:/work:ro", "-v", f"{outdir}:/out", self.docker_image, "kicad-cli"]
        else:
            work, out = str(workdir), str(outdir)
            cmd = [self.exe]
        cmd += [a.replace("{work}", work).replace("{out}", out) for a in args]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _supports_erc(exe: str) -> bool:
    try:
        r = subprocess.run([exe, "sch", "erc", "--help"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return r.returncode == 0 and "erc" in (r.stdout + r.stderr).lower() and "Usage: erc" in (r.stdout + r.stderr)


def find_runner(kicad_cli: str | None = None, docker_image: str | None = None) -> Runner:
    tried = []
    for cand in (kicad_cli, os.environ.get("KICAD_CLI"), shutil.which("kicad-cli")):
        if not cand:
            continue
        if _supports_erc(cand):
            return Runner(exe=cand)
        tried.append(f"{cand}（不支持 `sch erc`，可能是 KiCad 7 或更早）")
    image = docker_image or os.environ.get("KICAD_DOCKER_IMAGE")
    if image:
        if not shutil.which("docker"):
            tried.append(f"docker:{image}（没有 docker 命令）")
        else:
            r = subprocess.run(["docker", "run", "--rm", image, "kicad-cli", "sch", "erc", "--help"],
                               capture_output=True, text=True, timeout=600)
            if r.returncode == 0 and "Usage: erc" in r.stdout + r.stderr:
                return Runner(docker_image=image)
            tried.append(f"docker:{image}（运行失败：{(r.stderr or r.stdout).strip()[:200]}）")
    msg = INSTALL_HINT + ("\n试过：\n  - " + "\n  - ".join(tried) if tried else "")
    raise KicadUnavailable(msg)


# ------------------------------------------------------------ 结果解析


@dataclass
class CheckResult:
    kind: str                       # "ERC" / "DRC"
    file: Path
    returncode: int
    counts: dict[str, int] = field(default_factory=lambda: {"error": 0, "warning": 0, "info": 0})
    by_type: dict[str, int] = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)
    report: Path | None = None
    stderr: str = ""

    @property
    def ran(self) -> bool:
        return self.report is not None


def _iter_violations(data: dict):
    """兼容 ERC（sheets[].violations）和 DRC（violations / unconnected_items / schematic_parity）。"""
    for sheet in data.get("sheets", []) or []:
        yield from sheet.get("violations", []) or []
    for key in ("violations", "unconnected_items", "schematic_parity"):
        yield from data.get(key, []) or []


def parse_report(kind: str, file: Path, report: Path, returncode: int, stderr: str = "") -> CheckResult:
    res = CheckResult(kind, file, returncode, report=report, stderr=stderr)
    data = json.loads(report.read_text(encoding="utf-8"))
    for v in _iter_violations(data):
        sev = str(v.get("severity", "error")).lower()
        res.counts[sev] = res.counts.get(sev, 0) + 1
        typ = v.get("type", "unknown")
        res.by_type[typ] = res.by_type.get(typ, 0) + 1
        if len(res.examples) < 5:
            res.examples.append(f"[{sev}] {typ}: {v.get('description', '')}")
    return res


# ------------------------------------------------------------ 主流程


def collect_targets(paths: list[str]) -> list[tuple[str, Path]]:
    targets: list[tuple[str, Path]] = []
    for p in map(Path, paths):
        if p.is_dir():
            pros = sorted(p.glob("*.kicad_pro"))
            if not pros:
                raise FileNotFoundError(f"{p} 里没有 .kicad_pro")
            p = pros[0]
        if p.suffix == ".kicad_pro":
            for suffix, kind in ((".kicad_sch", "ERC"), (".kicad_pcb", "DRC")):
                f = p.with_suffix(suffix)
                if f.exists():
                    targets.append((kind, f))
        elif p.suffix == ".kicad_sch":
            targets.append(("ERC", p))
        elif p.suffix == ".kicad_pcb":
            targets.append(("DRC", p))
        else:
            raise FileNotFoundError(f"不认识的文件：{p}（需要 .kicad_pro / .kicad_sch / .kicad_pcb 或目录）")
        if not targets or not targets[-1][1].exists():
            raise FileNotFoundError(f"文件不存在：{p}")
    return targets


def run_check(runner: Runner, kind: str, file: Path, outdir: Path, extra: list[str]) -> CheckResult:
    file = file.resolve()
    report_name = f"{file.stem}.{kind.lower()}.json"
    sub = ["sch", "erc"] if kind == "ERC" else ["pcb", "drc"]
    args = sub + ["--format", "json", "--severity-all", "--units", "mm", *extra,
                  "-o", f"{{out}}/{report_name}", f"{{work}}/{file.name}"]
    proc = runner.run(args, file.parent, outdir)
    report = outdir / report_name
    if not report.exists():
        return CheckResult(kind, file, proc.returncode, stderr=(proc.stderr or proc.stdout).strip())
    return parse_report(kind, file, report, proc.returncode, (proc.stderr or "").strip())


def render_summary(results: list[CheckResult], runner: Runner) -> str:
    lines = [f"# KiCad 检查（{runner.describe()}）", "",
             "| 检查 | 文件 | 错误 | 警告 | 提示 | 状态 |", "|---|---|---:|---:|---:|---|"]
    for r in results:
        status = "已运行" if r.ran else f"运行失败（退出码 {r.returncode}）"
        lines.append(f"| {r.kind} | {r.file.name} | {r.counts['error']} | {r.counts['warning']} | "
                     f"{r.counts.get('info', 0)} | {status} |")
    for r in results:
        if r.by_type:
            lines += ["", f"## {r.kind} {r.file.name} 按类型", ""]
            lines += [f"- {t}: {n}" for t, n in sorted(r.by_type.items(), key=lambda x: -x[1])]
            lines += ["", "示例：", ""] + [f"- {e}" for e in r.examples]
        if not r.ran:
            lines += ["", f"## {r.kind} {r.file.name} 出错", "", "```", r.stderr[:2000], "```"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="KiCad ERC/DRC 检查汇总")
    ap.add_argument("paths", nargs="+", help=".kicad_pro / .kicad_sch / .kicad_pcb 或项目目录")
    ap.add_argument("--kicad-cli", help="kicad-cli 可执行文件路径")
    ap.add_argument("--docker", metavar="IMAGE", help="本机没有 KiCad 8+ 时使用的 Docker 镜像，如 kicad/kicad:9.0")
    ap.add_argument("--out", help="报告目录（JSON 报告和 summary.md）；默认临时目录")
    ap.add_argument("--fail-on", choices=("error", "warning"), default="error", help="达到哪个级别算失败")
    ap.add_argument("--schematic-parity", action="store_true", help="DRC 时同时检查原理图与 PCB 一致性")
    a = ap.parse_args(argv)
    try:
        targets = collect_targets(a.paths)
    except FileNotFoundError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    try:
        runner = find_runner(a.kicad_cli, a.docker)
    except KicadUnavailable as exc:
        print(str(exc), file=sys.stderr)
        return 4
    outdir = Path(a.out) if a.out else Path(tempfile.mkdtemp(prefix="kicad_check_"))
    outdir.mkdir(parents=True, exist_ok=True)
    outdir = outdir.resolve()
    results = []
    for kind, f in targets:
        extra = ["--schematic-parity"] if kind == "DRC" and a.schematic_parity else []
        results.append(run_check(runner, kind, f, outdir, extra))
    summary = render_summary(results, runner)
    (outdir / "summary.md").write_text(summary, encoding="utf-8")
    print(summary)
    print(f"报告目录：{outdir}", file=sys.stderr)
    if any(not r.ran for r in results):
        return 2
    threshold = SEVERITY_ORDER[a.fail_on]
    failed = any(n > 0 for r in results for sev, n in r.counts.items() if SEVERITY_ORDER.get(sev, 2) >= threshold)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
