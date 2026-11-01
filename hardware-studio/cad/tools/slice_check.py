"""切片检查：能否切片、预计耗材和打印时间。

调用外部命令行切片软件（PrusaSlicer，AGPL-3.0）。只作为外部程序调用，不复制、不链接它的代码。
找不到切片软件时，返回 ``available: False`` 和安装提示，不崩溃。

安装（Ubuntu 24.04 实测可用）::

    sudo apt-get install -y --no-install-recommends prusa-slicer

可以 import::

    from tools.slice_check import slice_check
    r = slice_check("out/bottom.stl", layer_height=0.2, infill=0.15)

命令行::

    python cad/tools/slice_check.py out/bottom.stl --rotate-x 180 --json r.json

说明：

* 打印时间是 PrusaSlicer 按其**默认通用打印机配置**估算的，不代表某台具体打印机，属于"估算"。
* 耗材质量 = 切片给出的体积（cm³）× ``filament_density``。默认 1.24 g/cm³ 是 PLA 常见标称值，
  **待核实**（应按所用料卷规格书填写）。
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CANDIDATES = ("prusa-slicer", "PrusaSlicer", "prusa-slicer-console", "PrusaSlicer.AppImage")
INSTALL_HINT = (
    "未找到切片软件命令行。Ubuntu/Debian：sudo apt-get install -y --no-install-recommends prusa-slicer；"
    "其他系统从 https://github.com/prusa3d/PrusaSlicer/releases 下载，并保证 prusa-slicer 在 PATH 里，"
    "或用 --slicer 指定路径。"
)


def find_slicer(explicit: str | None = None) -> str | None:
    """返回切片软件可执行文件路径；找不到返回 None。"""
    if explicit:
        return explicit if Path(explicit).exists() or shutil.which(explicit) else None
    for c in CANDIDATES:
        p = shutil.which(c)
        if p:
            return p
    return None


def _parse_time(s: str) -> float | None:
    """'1d 2h 3m 4s' -> 秒。"""
    total, found = 0.0, False
    for val, unit in re.findall(r"(\d+)\s*([dhms])", s):
        found = True
        total += int(val) * {"d": 86400, "h": 3600, "m": 60, "s": 1}[unit]
    return total if found else None


def parse_gcode_summary(text: str) -> dict:
    """从 PrusaSlicer G-code 末尾注释里取耗材长度、体积、时间。"""
    out: dict = {}
    m = re.search(r"^; filament used \[mm\] = ([\d.]+)", text, re.M)
    if m:
        out["filament_mm"] = float(m.group(1))
    m = re.search(r"^; filament used \[cm3\] = ([\d.]+)", text, re.M)
    if m:
        out["filament_cm3"] = float(m.group(1))
    m = re.search(r"^; estimated printing time \(normal mode\) = (.+)$", text, re.M)
    if m:
        out["time_text"] = m.group(1).strip()
        out["time_s"] = _parse_time(m.group(1))
    return out


def slice_check(
    stl: str | Path,
    layer_height: float = 0.2,
    infill: float = 0.15,
    supports: bool = False,
    rotate_x: float = 0.0,
    bed: tuple[float, float] = (250.0, 210.0),
    filament_diameter: float = 1.75,
    filament_density: float = 1.24,
    slicer: str | None = None,
    keep_gcode: str | Path | None = None,
    timeout: float = 300.0,
) -> dict:
    """切片一个 STL，返回结果 dict。

    Args:
        stl: STL 路径。
        layer_height: 层高，mm。
        infill: 填充率（0–1）。
        supports: 是否自动加支撑。
        rotate_x: 切片前绕 X 轴旋转角度，°（上壳通常翻转 180° 打印）。
        bed: 平台 X、Y 尺寸，mm（零件放在中心）。
        filament_diameter: 线径，mm。
        filament_density: 耗材密度 g/cm³（默认 1.24，待核实，见模块说明）。
        slicer: 切片软件路径；None 时自动查找。
        keep_gcode: 给出时把 G-code 保存到这里。
        timeout: 超时，秒。

    Returns:
        {"available", "ok", "slicer", "filament_mm", "filament_cm3", "filament_g_est", "time_s", "time_text",
         "warnings", "error"}
    """
    exe = find_slicer(slicer)
    if exe is None:
        return {"available": False, "ok": False, "error": INSTALL_HINT}
    stl = Path(stl)
    with tempfile.TemporaryDirectory() as td:
        gcode = Path(keep_gcode) if keep_gcode else Path(td) / (stl.stem + ".gcode")
        gcode.parent.mkdir(parents=True, exist_ok=True)
        bx, by = bed
        cmd = [
            exe, "--export-gcode",
            "--layer-height", str(layer_height),
            "--first-layer-height", str(max(layer_height, 0.2)),
            "--fill-density", f"{infill * 100:.0f}%",
            "--filament-diameter", str(filament_diameter),
            "--bed-shape", f"0x0,{bx}x0,{bx}x{by},0x{by}",
            "--center", f"{bx / 2},{by / 2}",
            "--output", str(gcode),
        ]
        if supports:
            cmd += ["--support-material", "--support-material-auto"]
        if rotate_x:
            cmd += ["--rotate-x", str(rotate_x)]
        cmd.append(str(stl))
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"available": True, "ok": False, "slicer": exe, "error": f"切片超时（>{timeout}s）"}
        log = (proc.stdout or "") + (proc.stderr or "")
        warnings = [ln.strip() for ln in log.splitlines()
                    if re.search(r"support|warning|error|outside|empty", ln, re.I)
                    and "Alert if supports needed" not in ln]
        if proc.returncode != 0 or not gcode.exists():
            return {"available": True, "ok": False, "slicer": exe, "returncode": proc.returncode,
                    "error": log.strip()[-2000:], "warnings": warnings}
        summary = parse_gcode_summary(gcode.read_text(errors="replace"))
    res = {"available": True, "ok": "filament_mm" in summary, "slicer": exe, **summary,
           "settings": {"layer_height": layer_height, "infill": infill, "supports": supports, "rotate_x": rotate_x},
           "warnings": warnings,
           "note": "时间按 PrusaSlicer 默认通用配置估算；质量 = 体积 × 密度（密度待核实）"}
    if "filament_cm3" in summary:
        res["filament_g_est"] = round(summary["filament_cm3"] * filament_density, 2)
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="切片检查（PrusaSlicer 命令行）")
    ap.add_argument("stl")
    ap.add_argument("--layer-height", type=float, default=0.2)
    ap.add_argument("--infill", type=float, default=0.15)
    ap.add_argument("--supports", action="store_true")
    ap.add_argument("--rotate-x", type=float, default=0.0)
    ap.add_argument("--bed", type=float, nargs=2, default=(250.0, 210.0))
    ap.add_argument("--density", type=float, default=1.24)
    ap.add_argument("--slicer", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    r = slice_check(a.stl, a.layer_height, a.infill, a.supports, a.rotate_x, tuple(a.bed),
                    filament_density=a.density, slicer=a.slicer)
    text = json.dumps(r, ensure_ascii=False, indent=2)
    if a.json:
        Path(a.json).write_text(text, encoding="utf-8")
    print(text)
    if not r["available"]:
        return 2
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
