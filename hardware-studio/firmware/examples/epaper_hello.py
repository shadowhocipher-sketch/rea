# Example firmware (MIT): SSD1681 1.54" e-paper "hello + counter" using the ssd168x API.
#
# Same file runs in the simulator and on a board:
#   simulator:  python sim/run_firmware.py firmware/examples/epaper_hello.py --display epaper \
#                   --seconds 60 --out /tmp/sim_hello.png
#               (`import ssd168x` loads the simulator's e-paper model)
#   board:      copy firmware/drivers/ssd168x.py and this file (as main.py) to the device.
# Hardware status (2026-11-01): run only in sim/; NOT run on a real board.  Pins below are
# placeholders - change CONFIG for your wiring.
from machine import Pin, SPI
import time
import ssd168x

CONFIG = {
    "spi_id": 1, "sck": 12, "mosi": 11, "cs": 10, "dc": 9, "rst": 8, "busy": 7,
    "baudrate": 4_000_000,   # SSD1681 write clock max 20 MHz (knowledge/display/ssd1680-ssd1681.md)
    "updates": 5,            # partial updates after the first full refresh
    "period_s": 10,
}


def main(cfg=CONFIG):
    spi = SPI(cfg["spi_id"], baudrate=cfg["baudrate"], sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]))
    epd = ssd168x.SSD1681(spi, Pin(cfg["cs"], Pin.OUT), Pin(cfg["dc"], Pin.OUT),
                          Pin(cfg["rst"], Pin.OUT), Pin(cfg["busy"], Pin.IN))
    B, W = ssd168x.BLACK, ssd168x.WHITE
    epd.fill(W)
    epd.rect(0, 0, epd.width, epd.height, B)
    epd.fill_rect(0, 0, epd.width, 24, B)
    epd.text("HELLO EPAPER", 8, 8, W)
    epd.show()                                  # full refresh
    for n in range(1, cfg["updates"] + 1):
        time.sleep(cfg["period_s"])
        epd.fill_rect(8, 90, epd.width - 16, 20, W)
        epd.text("count %d" % n, 8, 96, B)
        epd.show_partial()                      # partial refresh
    epd.sleep()                                 # deep sleep (~1 uA typ.)
    print("done full=%d partial=%d" % (epd.full_refreshes, epd.partial_refreshes))


if __name__ == "__main__":
    main()
