"""prender: headless product renderer for hardware-studio (numpy rasteriser, no bpy/OpenGL).

    import sys; sys.path.insert(0, "hardware-studio/render")
    from prender import PartSpec, RenderJob, render_product
    render_product(RenderJob(parts=[PartSpec("shell.stl", "#EFE9DF")], views=["iso"], out="out"))
"""

from .api import (PROPS, QUALITY, SCENES, VIEW_PRESETS, PartSpec, RenderConfigError, RenderedImage,
                  RenderJob, job_from_dict, load_job, render_product, render_view, view_angles)
from .label import DEFAULT_LABEL, LabelInfo
from .mesh import MeshLoadError, load_part

__all__ = [
    "PROPS", "QUALITY", "SCENES", "VIEW_PRESETS", "PartSpec", "RenderConfigError", "RenderedImage",
    "RenderJob", "job_from_dict", "load_job", "render_product", "render_view", "view_angles",
    "DEFAULT_LABEL", "LabelInfo", "MeshLoadError", "load_part",
]
