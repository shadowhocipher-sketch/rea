# Eval fixture firmware (MIT): e-paper counter, partial refresh with a full refresh every 5th update.
# Uses the simulator's e-paper API (sim/mpsim/mp_epaper.py); explicit refresh times so the
# expected timing does not depend on the simulator's default panel model.
from machine import Pin, SPI
import epaper
import time

UPDATES = 10
FULL_EVERY = 5
PERIOD_S = 60

spi = SPI(1, baudrate=4_000_000, sck=Pin(12), mosi=Pin(11))
epd = epaper.SSD1681(spi, Pin(10, Pin.OUT), Pin(9, Pin.OUT), Pin(8, Pin.OUT), Pin(7, Pin.IN),
                     full_refresh_ms=2500, partial_refresh_ms=400)
epd.fill(epaper.WHITE)
epd.text("boot", 4, 4, epaper.BLACK)
epd.show()                                   # full refresh #1
n = 0
for n in range(1, UPDATES + 1):
    time.sleep(PERIOD_S)
    epd.fill_rect(0, 20, epd.width, 20, epaper.WHITE)
    epd.text("n=%d" % n, 4, 24, epaper.BLACK)
    if n % FULL_EVERY == 0:
        epd.show()                           # full refresh at n = 5, 10
    else:
        epd.show_partial()
epd.sleep()
print("done", n)
