"""测试用小工具：一块代表外壳壁的平板（外表面 z = 0，往 -Z 是壁内）。"""
from build123d import Align, Box, Location


def slab(wall: float, size: float = 60.0):
    """局部坐标里的平板：z ∈ [-wall, 0]，XY 居中。"""
    return Box(size, size, wall, align=(Align.CENTER, Align.CENTER, Align.MAX)).moved(Location((0, 0, 0)))


def vol(s) -> float:
    return float(getattr(s, "volume", 0.0) or 0.0)
