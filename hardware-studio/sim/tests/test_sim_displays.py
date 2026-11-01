"""The three display families produce frames and images; CLI end to end."""
import os
import sys
import textwrap

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.join(HERE, "..")
ROOT = os.path.join(SIM, "..")
sys.path.insert(0, SIM)

from mpsim import run, render  # noqa: E402
import run_firmware  # noqa: E402

EYES = os.path.join(ROOT, "products", "desk-creature-standin", "eyes.py")
LCD_EXAMPLE = os.path.join(SIM, "examples", "lcd_dashboard.py")
EPD_EXAMPLE = os.path.join(SIM, "examples", "epaper_card.py")


def fw(tmp_path, body, name="fw.py"):
    p = tmp_path / name
    p.write_text(textwrap.dedent(body), encoding="utf-8")
    return p


def gif_frames(path):
    im = Image.open(path)
    n = 0
    try:
        while True:
            n += 1
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return n


# ------------------------------------------------------------------ OLED
def test_eyes_standin_gif_and_png(tmp_path):
    r = run(EYES, display="ssd1306", max_seconds=6, seed=1, echo=False)
    assert r.stop_reason == "time_limit" and r.error is None
    assert len(r.frames) > 20 and r.frames[0].rgb.shape == (64, 128, 3)
    lit = [int((f.rgb[:, :, 0] > 0).sum()) for f in r.frames]
    assert max(lit) > 1500 and min(lit[1:]) < max(lit)     # eyes drawn, blinks/moves change
    g = r.save(str(tmp_path / "sim_eyes.gif"))
    p = r.save(str(tmp_path / "sim_eyes.png"))
    assert gif_frames(g) > 10 and Image.open(p).size[0] > 512
    # reproducible: same seed -> same pixels
    r2 = run(EYES, display="ssd1306", max_seconds=6, seed=1, echo=False)
    assert all(np.array_equal(a.rgb, b.rgb) for a, b in zip(r.frames, r2.frames))


def test_ssd1306_invert_rotate_power_and_missing_device(tmp_path):
    p = fw(tmp_path, """
        from machine import Pin, I2C
        import ssd1306
        o = ssd1306.SSD1306_I2C(128, 32, I2C(0, scl=Pin(9), sda=Pin(8)))
        o.pixel(0, 0, 1); o.show()
        o.rotate(0)
        o.invert(1)
        o.poweroff()
    """)
    r = run(p, display="ssd1306", max_seconds=1, echo=False)
    show, rot, inv, off = r.frames[-4:]
    assert show.rgb[0, 0, 0] == 255 and show.rgb.shape[:2] == (32, 128)
    assert rot.rgb[31, 127, 0] == 255 and rot.rgb[0, 0, 0] == 0      # rotate(0) = 180 degrees
    assert inv.rgb[31, 127, 0] == 0 and inv.rgb[0, 0, 0] == 255
    assert off.rgb.max() == 0
    r = run(p, display="ssd1306", max_seconds=1, inputs={"i2c_devices": []}, echo=False)
    assert r.stop_reason == "exception" and "OSError" in r.error


# ------------------------------------------------------------------ LCD
def test_st7789_blit_byte_order_text_and_backlight(tmp_path):
    p = fw(tmp_path, """
        from machine import Pin, SPI
        import st7789, framebuf, time, vga1_8x16 as font
        tft = st7789.ST7789(SPI(1), 240, 240, dc=Pin(2), backlight=Pin(5, Pin.OUT))
        tft.fill_rect(0, 0, 10, 10, st7789.RED)
        buf = bytearray(4 * 4 * 2)
        fb = framebuf.FrameBuffer(buf, 4, 4, framebuf.RGB565)
        fb.fill(st7789.BLUE)                       # little-endian in RAM
        tft.blit_buffer(buf, 20, 0, 4, 4)          # panel reads big-endian -> swapped colour
        tft.text(font, "Hi", 40, 0, st7789.WHITE, st7789.BLACK)
        time.sleep_ms(10)
        Pin(5).value(0)
        tft.pixel(0, 100, st7789.GREEN)
        time.sleep_ms(10)
    """)
    r = run(p, display="st7789", max_seconds=1, echo=False)
    f1, f2 = r.frames[0], r.frames[1]
    assert tuple(f1.rgb[5, 5]) == (255, 0, 0)
    swapped = ((0x001F & 0xFF) << 8) | (0x001F >> 8)                # 0x1F00
    assert tuple(f1.rgb[1, 21]) == tuple(render_rgb565(swapped))
    assert (f1.rgb[0:16, 40:56] == 255).any()                       # text drawn
    assert f2.rgb.max() == 0                                          # backlight off


def render_rgb565(c):
    from mpsim.mp_st7789 import rgb565_to_rgb
    return rgb565_to_rgb(np.array([c]))[0]


def test_st7789_fb_show_and_example(tmp_path):
    p = fw(tmp_path, """
        import st7789
        d = st7789.ST7789_FB(None, 135, 240, rotation=1)
        d.fill(st7789.color565(0, 255, 0)); d.show()
    """)
    r = run(p, display="st7789", max_seconds=1, echo=False)
    assert r.frames[0].rgb.shape == (135, 240, 3) and tuple(r.frames[0].rgb[0, 0]) == (0, 255, 0)
    r = run(LCD_EXAMPLE, display="st7789", max_seconds=6, echo=False)
    assert r.error is None and len(r.frames) == 8
    out = r.save(str(tmp_path / "sim_lcd.png"), png_mode="last")
    assert Image.open(out).size[1] > 480


# ------------------------------------------------------------------ e-paper
def test_epaper_refresh_counts_time_and_ghosting(tmp_path):
    p = fw(tmp_path, """
        from machine import Pin, SPI
        import epaper
        e = epaper.SSD1680(SPI(1), Pin(1), Pin(2), Pin(3), Pin(4))
        e.fill(epaper.WHITE); e.fill_rect(0, 0, 20, 20, epaper.BLACK); e.show()
        e.fill(epaper.WHITE); e.show_partial()
        e.sleep()
    """)
    r = run(p, display="epaper", max_seconds=60, echo=False)
    full, part = r.frames
    assert full.meta["refresh"] == "full" and part.meta["refresh"] == "partial"
    assert full.rgb.shape == (250, 122, 3) and tuple(full.rgb[5, 5]) == (0, 0, 0)
    assert tuple(part.rgb[5, 5]) == (200, 200, 200)                   # ghost after partial
    assert part.t_us - full.t_us == 3000 * 1000                       # full refresh blocks 3 s
    assert r.rt.stats["epaper"]["ssd1680#0"] == {"full": 1, "partial": 1, "refresh_ms": 3300}


def test_epaper_red_panel_forces_full_refresh(tmp_path):
    p = fw(tmp_path, """
        import epaper
        e = epaper.SSD1681(red=True)
        e.fill(1); e.red.fill_rect(0, 0, 5, 5, 1); e.show_partial()
    """)
    r = run(p, display="epaper", max_seconds=60, echo=False)
    f = r.frames[0]
    assert f.meta["refresh"] == "full" and tuple(f.rgb[1, 1]) == (255, 0, 0)
    assert any("3-colour" in w for w in r.warnings) and r.virtual_ms >= 15000


def test_epaper_example_outputs(tmp_path):
    r = run(EPD_EXAMPLE, display="epaper", max_seconds=400, echo=False)
    assert r.error is None and len(r.frames) == 7
    assert r.frames[0].rgb.shape == (122, 250, 3)
    g = r.save(str(tmp_path / "sim_card.gif"))
    assert gif_frames(g) >= 7


# ------------------------------------------------------------------ outputs / CLI
def test_outputs_are_prefixed_and_labelled(tmp_path):
    r = run(EYES, display="ssd1306", max_frames=3, echo=False)
    out = r.save(str(tmp_path / "eyes.png"), png_mode="last")
    assert os.path.basename(out) == "sim_eyes.png"
    assert render.label_text() in (render.LABEL, render.LABEL_ASCII)
    im = np.asarray(Image.open(out).convert("RGB"))
    footer = im[-20:, -200:]
    assert ((footer[:, :, 0] > 200) & (footer[:, :, 2] < 120)).any()   # orange label pixels


def test_cli_end_to_end(tmp_path):
    out = str(tmp_path / "sim_cli.gif")
    log = str(tmp_path / "log.json")
    rc = run_firmware.main([EYES, "--display", "ssd1306", "--seconds", "3", "--out", out,
                            "--seed", "2", "--log", log, "--quiet"])
    assert rc == 0 and os.path.getsize(out) > 1000 and os.path.exists(log)
