# answer-box firmware (MicroPython, ESP32-C3-MINI-1 + 1.54" SSD1681 e-paper + LIS3DH).
#
# Shake -> a new "answer" on the e-paper.  Idle -> e-paper sleeps, MCU deep-sleeps,
# LIS3DH INT1 wakes it; the wake shake itself shows the next answer.
#
# Built from library templates: firmware/templates/shake.py (copied next to this
# file, unchanged) for the accelerometer; deep-sleep pattern from power.py.
#
# Verification status (2026-11-01):
#   - Run ONLY in the hardware-studio simulator (sim/run_firmware.py, see
#     products/answer-box/REPORT.md for the command and refresh counts).
#   - NOT run on a real board.  The e-paper API (`epaper.SSD1681`) is the
#     simulator's own; a real build needs an SSD1681 MicroPython driver with the
#     same methods (show / show_partial / sleep) - not in the library yet (未运行).
#   - Answers are English because framebuf.text has only an 8x8 ASCII font; the
#     Chinese product needs a bitmap CJK font (not done, see REPORT).
#   - Shake threshold / cooldown not tuned on hardware; esp32.wake_on_gpio on the
#     C3 port is 待核实.
import time
import machine
import random
import framebuf
from machine import Pin, SPI, I2C
import epaper
from shake import LIS3DH, ShakeInput, SensorError, wake_on_int1, make_int_pin, load_config

# Pins follow products/answer-box/pins.csv
CONFIG = {
    "i2c_id": 0, "sda": 1, "scl": 4, "addr": 0x18,
    "int_pin": 3, "int_pull": "down",
    "spi_id": 1, "sck": 6, "mosi": 7, "cs": 8, "dc": 10, "rst": 2, "busy": 5,
    "range_g": 4, "odr_hz": 50, "low_power": True, "threshold_mg": 1600, "duration": 1,
    "hp_filter": False, "latch": True,
    "cooldown_ms": 800,      # one answer per shake gesture
    "awake_ms": 15000,       # stay awake this long after the last shake, then deep sleep
    "full_every": 5,         # every 5th update in an awake session is a full refresh (clears ghosting)
    "poll_ms": 20,
}

ANSWERS = (
    "Go for it", "Not today", "Wait a week", "Trust your gut", "Ask a friend",
    "Yes, quietly", "Let it go", "Try once more", "Sleep on it", "Absolutely",
    "Maybe later", "Start small", "Say yes", "Not this one", "Look again",
)

cfg = load_config(CONFIG)
W = H = 200
BLACK, WHITE = epaper.BLACK, epaper.WHITE


def text_big(fb, s, cx, y, k):
    """Draw s centred at cx, scaled k times from the 8x8 framebuf font."""
    w = 8 * len(s)
    tmp = framebuf.FrameBuffer(bytearray(w), w, 8, framebuf.MONO_HLSB)
    tmp.fill(0)
    tmp.text(s, 0, 0, 1)
    x0 = cx - w * k // 2
    for yy in range(8):
        for xx in range(w):
            if tmp.pixel(xx, yy):
                fb.fill_rect(x0 + xx * k, y + yy * k, k, k, BLACK)


def wrap(s, n):
    lines, cur = [], ""
    for word in s.split():
        if cur and len(cur) + 1 + len(word) > n:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word) if cur else word
    lines.append(cur)
    return lines


def frame(epd):
    epd.fill(WHITE)
    epd.rect(4, 4, W - 8, H - 8, BLACK)
    epd.rect(6, 6, W - 12, H - 12, BLACK)


def draw_answer(epd, text, n):
    frame(epd)
    epd.text("the answer is", 48, 20, BLACK)
    epd.hline(40, 32, W - 80, BLACK)
    k = 3 if all(len(l) <= 7 for l in wrap(text, 7)) else 2
    lines = wrap(text, 7 if k == 3 else 11)
    y = 100 - len(lines) * (8 * k + 6) // 2
    for ln in lines:
        text_big(epd, ln, W // 2, y, k)
        y += 8 * k + 6
    epd.text("#%d" % n, 16, 176, BLACK)
    epd.text("shake again", 96, 176, BLACK)


def draw_welcome(epd):
    frame(epd)
    text_big(epd, "ANSWER", W // 2, 40, 3)
    text_big(epd, "BOX", W // 2, 70, 3)
    epd.text("think of a question", 24, 120, BLACK)
    epd.text("then shake me", 48, 136, BLACK)


def rtc_state():
    raw = machine.RTC().memory()
    if len(raw) >= 3:
        return raw[0], raw[1] | (raw[2] << 8)
    return 255, 0


def save_state(last, count):
    machine.RTC().memory(bytes([last, count & 0xFF, (count >> 8) & 0xFF]))


def next_answer(last):
    i = random.randrange(len(ANSWERS) - 1)
    return i + 1 if i >= last else i      # never the same answer twice in a row


def main():
    i2c = I2C(cfg["i2c_id"], sda=Pin(cfg["sda"]), scl=Pin(cfg["scl"]))
    spi = SPI(cfg["spi_id"], baudrate=4_000_000, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]))
    epd = epaper.SSD1681(spi, Pin(cfg["cs"], Pin.OUT), Pin(cfg["dc"], Pin.OUT), Pin(cfg["rst"], Pin.OUT),
                         Pin(cfg["busy"], Pin.IN))
    try:
        acc = LIS3DH(i2c, cfg["addr"])
        acc.setup_motion_interrupt(cfg["threshold_mg"], cfg["odr_hz"], cfg["range_g"], cfg["duration"],
                                   cfg["low_power"], cfg["hp_filter"], cfg["latch"])
    except SensorError as e:
        frame(epd)
        epd.text("sensor error", 52, 90, BLACK)
        epd.text(str(e)[:22], 16, 110, BLACK)
        epd.show()
        epd.sleep()
        print("FAULT", e)
        machine.deepsleep()                       # no wake source: stays off until reset/USB
    int_pin = make_int_pin(cfg)
    shake = ShakeInput(int_pin, acc, cfg["cooldown_ms"])
    last, count = rtc_state()
    woke = machine.reset_cause() == machine.DEEPSLEEP_RESET
    updates = 0

    def new_answer():
        nonlocal last, count, updates
        last = next_answer(last if last < len(ANSWERS) else 0)
        count += 1
        updates += 1
        draw_answer(epd, ANSWERS[last], count)
        # after deep sleep the controller RAM is gone -> the first update is a full refresh
        if updates == 1 and woke or updates % cfg["full_every"] == 0:
            epd.show()
            kind = "full"
        else:
            epd.show_partial()
            kind = "partial"
        save_state(last, count)
        print("ANSWER #%d %s (%s) t=%d" % (count, ANSWERS[last], kind, time.ticks_ms()))

    if woke:
        acc.clear_interrupt()
        new_answer()                              # the shake that woke us
    else:
        draw_welcome(epd)
        epd.show()
        updates = 1                               # the welcome screen was a full refresh
        print("WELCOME t=%d" % time.ticks_ms())
    t_last = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t_last) < cfg["awake_ms"]:
        if shake.update():
            new_answer()
            t_last = time.ticks_ms()
        time.sleep_ms(cfg["poll_ms"])
    epd.sleep()
    acc.clear_interrupt()
    print("SLEEP after %d answers" % count)
    wake_on_int1(int_pin, 1)
    machine.deepsleep()


main()
