"""坐标约定、外壳面上的局部坐标系、以及"特征"（加料 + 去料）数据结构。

全局坐标约定（整个 hwcad 包统一）
---------------------------------
* 单位 mm。
* 外壳外形包围盒：X 方向长度 ``length``，Y 方向宽度 ``width``，Z 方向高度 ``height``。
* X、Y 以外形中心为 0；Z = 0 是外壳底面（外表面），Z = height 是顶面（外表面）。
* 分模面垂直于 Z（``split_z``）。"上下壳"和"前后壳"只是命名不同：
  手持设备把 +Z 当作"前"（屏幕面），桌面设备把 +Z 当作"上"。

面上的局部坐标系（``face_plane``）
---------------------------------
每个特征（开孔、按键、USB 口……）都在一个局部坐标系里建模，再摆到外壳的某个面上：

* 局部原点在**外表面**上；局部 +Z 是该面的**外法线**；局部 Z < 0 是往壁内、往壳内。
* ``u``、``v`` 是特征中心的位置，用**全局坐标**给出：

  ===========  ==================  =================  ==================
  面 face      u 对应               v 对应              局部 +X 方向
  ===========  ==================  =================  ==================
  ``top``      全局 x               全局 y              +X（局部 +Y = +Y）
  ``bottom``   全局 x               全局 y              +X（局部 +Y = -Y）
  ``+x``       全局 y               全局 z              +Y
  ``-x``       全局 y               全局 z              -Y
  ``+y``       全局 x               全局 z              -X
  ``-y``       全局 x               全局 z              +X
  ===========  ==================  =================  ==================

  侧面（±x、±y）的局部 +Y 一律朝全局 +Z（朝上）。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from build123d import Location, Part, Plane, Vector

FACES = ("top", "bottom", "+x", "-x", "+y", "-y")

_FACE_AXES = {
    #        normal         local x dir
    "top": ((0, 0, 1), (1, 0, 0)),
    "bottom": ((0, 0, -1), (1, 0, 0)),
    "+x": ((1, 0, 0), (0, 1, 0)),
    "-x": ((-1, 0, 0), (0, -1, 0)),
    "+y": ((0, 1, 0), (-1, 0, 0)),
    "-y": ((0, -1, 0), (1, 0, 0)),
}


def face_plane(size: tuple[float, float, float], face: str, u: float = 0.0, v: float = 0.0) -> Plane:
    """返回外壳某个面上、位于 (u, v) 处的局部坐标系。

    Args:
        size: 外壳外形 (length_x, width_y, height_z)，mm。
        face: ``top`` / ``bottom`` / ``+x`` / ``-x`` / ``+y`` / ``-y``。
        u, v: 特征中心的全局坐标，含义见模块说明表格，mm。

    Returns:
        build123d ``Plane``：原点在外表面，z_dir 为外法线。
    """
    if face not in _FACE_AXES:
        raise ValueError(f"face 必须是 {FACES} 之一，收到 {face!r}")
    L, W, H = size
    n, xd = _FACE_AXES[face]
    if face == "top":
        origin = (u, v, H)
    elif face == "bottom":
        origin = (u, v, 0.0)
    elif face == "+x":
        origin = (L / 2, u, v)
    elif face == "-x":
        origin = (-L / 2, u, v)
    elif face == "+y":
        origin = (u, W / 2, v)
    else:
        origin = (u, -W / 2, v)
    return Plane(origin=origin, x_dir=xd, z_dir=n)


def wall_plane(size: tuple[float, float, float], face: str, u: float = 0.0) -> Plane:
    """侧壁上的"竖直"坐标系：原点在外表面、全局 z = 0 处；局部 +X = 外法线，局部 +Z = 全局 +Z。

    用于卡扣等沿 Z 方向生长的特征。``u`` 含义同 :func:`face_plane`（沿墙方向的全局坐标）。
    """
    if face not in ("+x", "-x", "+y", "-y"):
        raise ValueError("wall_plane 只用于侧面 ±x / ±y")
    p = face_plane(size, face, u, 0.0)
    return Plane(origin=p.origin, x_dir=p.z_dir, z_dir=(0, 0, 1))


@dataclass
class Feature:
    """一个特征 = 要加上去的实体 + 要挖掉的实体（都在局部坐标里），以及放置位置。

    Attributes:
        name: 名字，出现在报告里。
        plane: 局部坐标系（``face_plane`` / ``wall_plane`` 的结果；None 表示已是全局坐标）。
        add: 加料实体（例如按键导向筒、固定柱），可为 None。
        cut: 去料实体（例如开孔），可为 None。
        add_to: 加料归属哪个壳件（``lower`` / ``upper``）。
        cut_from: 去料作用到哪些壳件（默认两个都切，切不到的不受影响）。
        envelopes: 检查用的包络体（全局坐标），例如 USB 插头外壳、电池膨胀后的外形。
        info: 设计数据（尺寸推导、应变估算等），写进检查报告。
    """

    name: str
    plane: Plane | None = None
    add: Part | None = None
    cut: Part | None = None
    add_to: str = "lower"
    cut_from: tuple[str, ...] = ("lower", "upper")
    envelopes: dict[str, Part] = field(default_factory=dict)
    info: dict = field(default_factory=dict)

    def _place(self, shape: Part | None) -> Part | None:
        if shape is None:
            return None
        if self.plane is None:
            return shape
        return shape.moved(Location(self.plane))

    def placed_add(self) -> Part | None:
        """加料实体（全局坐标）。"""
        return self._place(self.add)

    def placed_cut(self) -> Part | None:
        """去料实体（全局坐标）。"""
        return self._place(self.cut)

    def placed_envelopes(self) -> dict[str, Part]:
        """检查用包络体（全局坐标）。"""
        return {k: self._place(v) for k, v in self.envelopes.items()}


def vec(p) -> Vector:
    """把三元组转成 Vector。"""
    return Vector(*p)
