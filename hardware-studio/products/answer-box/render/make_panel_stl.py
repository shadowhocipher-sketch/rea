"""Product-only helper: a stand-in box for the 1.54" e-paper module (48x33x3 mm at z=12,
same as enclosure.yaml components.epd_module) so the render shows a screen in the window.
Run from hardware-studio/:  python products/answer-box/render/make_panel_stl.py"""
from build123d import Box, Align, Location, export_stl

panel = Box(48, 33, 3.0, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((0, 0, 12.0)))
export_stl(panel, "products/answer-box/render/epd_standin.stl")
print("wrote products/answer-box/render/epd_standin.stl")
