# Example firmware: 2.13" SSD1680 e-paper "status card" with partial updates.
# Written for the simulator demo; MIT licence.  Hardware status: only run in
# sim/ (mpsim); NOT run on a real board.  The e-paper API is the simulator's
# own (see sim/mpsim/mp_epaper.py) because MicroPython has no standard driver.
from machine import Pin, SPI
import epaper
import time

# ---- configuration ----
CFG = {
    "spi_id": 1, "sck": 12, "mosi": 11, "cs": 10, "dc": 9, "rst": 8, "busy": 7,
    "rotation": 1,               # landscape: 250 x 122
    "update_s": 30,              # partial update period
    "full_every": 4,             # full refresh after this many partial refreshes
}

spi = SPI(CFG["spi_id"], baudrate=4_000_000, sck=Pin(CFG["sck"]), mosi=Pin(CFG["mosi"]))
epd = epaper.SSD1680(spi, Pin(CFG["cs"], Pin.OUT), Pin(CFG["dc"], Pin.OUT),
                     Pin(CFG["rst"], Pin.OUT), Pin(CFG["busy"], Pin.IN),
                     rotation=CFG["rotation"])
W, H = epd.width, epd.height
B, Wh = epaper.BLACK, epaper.WHITE


def draw_static():
    epd.fill(Wh)
    epd.fill_rect(0, 0, W, 20, B)
    epd.text("ANSWER CARD", 6, 6, Wh)
    epd.rect(4, 26, W - 8, H - 30, B)
    epd.text("Q: Will it rain?", 12, 34, B)
    epd.hline(12, 46, W - 24, B)


def draw_dynamic(n):
    epd.fill_rect(10, 52, W - 20, 64, Wh)
    answers = ("Probably not.", "Take an umbrella", "Ask again later", "Yes, at 4 pm")
    epd.text("A: " + answers[n % len(answers)], 12, 58, B)
    epd.text("update #%d" % n, 12, 80, B)
    # little progress dots
    for i in range(CFG["full_every"]):
        epd.ellipse(W - 70 + i * 14, 100, 4, 4, B, i < n % CFG["full_every"] + 1)


draw_static()
draw_dynamic(0)
epd.show()                 # first draw: full refresh
n = 0
while True:
    time.sleep(CFG["update_s"])
    n += 1
    draw_dynamic(n)
    if n % CFG["full_every"] == 0:
        draw_static()
        draw_dynamic(n)
        epd.show()         # periodic full refresh clears ghosting
    else:
        epd.show_partial()
    if n >= 6:
        epd.sleep()
        break
