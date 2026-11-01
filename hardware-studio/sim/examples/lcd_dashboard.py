# Example firmware: ST7789 240x240 colour LCD dashboard (st7789py-style API).
# Written for the simulator demo; MIT licence.  Hardware status: only run in
# sim/ (mpsim); NOT run on a real board.
#
# Shows both drawing styles:
#   * direct drawing calls on the display (fill_rect, text, line, rect)
#   * a framebuf.RGB565 sprite pushed with blit_buffer() (note the byte swap:
#     the panel expects big-endian RGB565, framebuf stores little-endian).
from machine import Pin, SPI, PWM
import framebuf
import st7789py as st7789
import vga1_8x16 as font
import time

# ---- configuration (no board-specific values below this block) ----
CFG = {
    "spi_id": 1, "sck": 12, "mosi": 11, "dc": 13, "cs": 10, "rst": 14, "bl": 15,
    "width": 240, "height": 240, "baud": 40_000_000,
}

spi = SPI(CFG["spi_id"], baudrate=CFG["baud"], sck=Pin(CFG["sck"]), mosi=Pin(CFG["mosi"]))
tft = st7789.ST7789(spi, CFG["width"], CFG["height"], reset=Pin(CFG["rst"], Pin.OUT),
                    dc=Pin(CFG["dc"], Pin.OUT), cs=Pin(CFG["cs"], Pin.OUT),
                    backlight=Pin(CFG["bl"], Pin.OUT), rotation=0)
W, H = tft.width, tft.height
C = st7789.color565
BG, PANEL, ACCENT, OK, WARN = C(12, 16, 28), C(32, 40, 64), C(80, 170, 255), C(60, 200, 120), C(255, 170, 40)


def swap(c):  # framebuf RGB565 is little-endian; the panel reads big-endian
    return ((c & 0xFF) << 8) | (c >> 8)


# 24x24 heart sprite drawn into an RGB565 framebuf
SPR = 24
sbuf = bytearray(SPR * SPR * 2)
spr = framebuf.FrameBuffer(sbuf, SPR, SPR, framebuf.RGB565)
spr.fill(swap(PANEL))
spr.ellipse(7, 8, 6, 6, swap(C(255, 70, 90)), True)
spr.ellipse(16, 8, 6, 6, swap(C(255, 70, 90)), True)
spr.poly(0, 0, bytearray([1, 10, 22, 10, 12, 22]), swap(C(255, 70, 90)), True)


def frame(step):
    tft.fill(BG)
    tft.fill_rect(0, 0, W, 28, PANEL)
    tft.text(font, "DESK DASHBOARD", 8, 6, C(230, 230, 240), PANEL)
    # temperature card
    tft.fill_rect(10, 40, 105, 80, PANEL)
    tft.text(font, "TEMP", 18, 48, ACCENT, PANEL)
    temp = 21 + (step % 5)
    tft.text(font, "%d C" % temp, 18, 80, C(255, 255, 255), PANEL)
    # battery card with a bar
    tft.fill_rect(125, 40, 105, 80, PANEL)
    tft.text(font, "BATT", 133, 48, ACCENT, PANEL)
    pct = 100 - step * 7
    tft.rect(133, 78, 88, 20, C(200, 200, 210))
    tft.fill_rect(135, 80, max(0, 84 * pct // 100), 16, OK if pct > 30 else WARN)
    # sparkline
    tft.fill_rect(10, 132, 220, 70, PANEL)
    pts = [(14 + i * 12, 190 - ((i * 37 + step * 13) % 50)) for i in range(18)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        tft.line(x0, y0, x1, y1, ACCENT)
    # sprite via blit_buffer
    tft.blit_buffer(sbuf, 200 - (step % 3) * 4, 208, SPR, SPR)
    tft.text(font, "step %d" % step, 12, 214, C(160, 160, 180), BG)


for step in range(8):
    frame(step)
    time.sleep_ms(500)
