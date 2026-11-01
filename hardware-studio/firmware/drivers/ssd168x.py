# ssd168x.py - SSD1680 / SSD1681 e-paper driver for MicroPython (SPI + CS/DC/RST/BUSY).
#
# Licence: MIT (written for this library; no third-party code copied).
#
# !!! Hardware status (2026-11-01): NOT run on real hardware. !!!
# Written from the controller datasheets and checked only on the desktop:
#   * firmware/tests/test_fw_ssd168x.py records the SPI/pin traffic with fake SPI/Pin
#     objects and compares it with the datasheet operation flow;
#   * the same firmware runs in sim/ (where `import ssd168x` / `epaper` load the simulator's
#     model with the SAME API and draw frames).
# Unverified on a panel: RAM bit/scan orientation, the rotation direction, whether the
# panel's OTP waveform for "Display Mode 2" is a partial-update waveform, border values,
# refresh times. Verify on the board and record the result here.
#
# API (identical to sim/mpsim/mp_epaper.py, so firmware runs unchanged in the simulator
# and on the device - copy this file to the board as ssd168x.py, or as epaper.py if the
# firmware does `import epaper`):
#
#   epd = SSD1680(spi, cs, dc, rst, busy, width=None, height=None, *, red=False, rotation=0,
#                 full_refresh_ms=None, partial_refresh_ms=None, busy_timeout_ms=None)
#   epd.fill(WHITE); epd.text("hi", 0, 0, BLACK)  # framebuf.FrameBuffer, MONO_HLSB, 1=white
#   epd.red.fill_rect(...)                        # red layer when red=True, 1=red
#   epd.show()          full refresh   (aliases display(), refresh(); show(full=False) = partial)
#   epd.show_partial()  partial refresh (aliases display_partial(), partial())
#   epd.clear()         white + full refresh
#   epd.sleep()         deep sleep mode 1; the next refresh re-initialises (hardware reset)
#   epd.init()          hardware reset + init sequence (called by the constructor)
#   epd.full_refreshes, epd.partial_refreshes, epd.refresh_ms_total (measured BUSY time)
#   BusyTimeout (OSError) raised when BUSY stays high longer than the timeout.
#
# Pins: cs/dc/rst must be Pin.OUT, busy Pin.IN (BUSY high = busy). Exiting deep sleep needs
# a hardware reset, so sleep() requires rst.
#
# Sources (all read 2026-11-01; see knowledge/display/ssd1680-ssd1681.md):
#  [DS1680] SSD1680 Rev 0.14 (Solomon Systech, Jun 2019, Product Preview), GitHub mirror
#           https://github.com/CursedHardware/epd-driver-ic/blob/8c147a71ff451da3b16450162559cb0ccd8bdaec/SSD1680.pdf
#           s7 command table, s9.1 "General operation flow to drive display panel" (Fig 9-1).
#  [DS1681] SSD1681 Rev 0.13 (2019, Product Preview), GitHub mirror
#           https://github.com/libdriver/ssd1681/blob/db14fa9ad397e25fcf5589f042cbf58b8fec2be6/datasheet/ssd1681_datasheet.pdf
#           same command codes; s8.1 operation flow identical to [DS1680] s9.1.
#  [WS] Waveshare e-Paper demo epd2in13_V4.py (MIT-style licence), commit d28b3c4,
#       https://github.com/waveshareteam/e-Paper/blob/d28b3c4cfc78eef1c6cd6e6e3013654e449d2864/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd2in13_V4.py
#       only as a second source for the 22h values used in practice (F7 full / FF partial)
#       and the border values; no code copied.
# Both datasheets are "Product Preview" mirrors, not hosted by Solomon Systech: 待核实.

import framebuf
import time

try:
    from micropython import const
except ImportError:  # CPython tests
    def const(x):
        return x

WHITE = 1
BLACK = 0
RED = 1

# Command codes [DS1680] s7 / [DS1681] s7
CMD_DRIVER_OUTPUT = const(0x01)   # MUX = gates - 1 (9 bits) + scan direction byte
CMD_DEEP_SLEEP = const(0x10)      # 01h = mode 1 (keeps RAM), 11h = mode 2; exit only by HW reset
CMD_DATA_ENTRY = const(0x11)      # 03h = Y increment, X increment, update X first [POR]
CMD_SW_RESET = const(0x12)        # BUSY high while it runs
CMD_TEMP_SENSOR = const(0x18)     # 80h = internal temperature sensor
CMD_MASTER_ACTIVATION = const(0x20)  # run the sequence chosen by 22h; BUSY high meanwhile
CMD_UPDATE_CTRL2 = const(0x22)    # display update sequence option
CMD_WRITE_BW = const(0x24)        # B/W RAM: 1 = white, 0 = black
CMD_WRITE_RED = const(0x26)       # RED RAM: 1 = red (B/W panels: ignored for colour, Table 6-5)
CMD_BORDER = const(0x3C)          # border waveform (VBD)
CMD_RAM_X_WINDOW = const(0x44)    # start/end in units of 8 pixels
CMD_RAM_Y_WINDOW = const(0x45)    # start/end gate (9 bits each)
CMD_RAM_X_COUNTER = const(0x4E)
CMD_RAM_Y_COUNTER = const(0x4F)

# 22h parameters, [DS1680] 22h table:
#   B1 = clock on, load temperature, load LUT Display Mode 1, clock off   (flow step 4)
#   F7 = clock+analog on, load temperature, display with Display Mode 1, analog+osc off
#   FF = same with Display Mode 2
# Display Mode 2 is used for partial updates as in [WS]; whether Mode 2 is a partial
# waveform is decided by the panel's OTP (37h "Display Mode for WS"), 待核实 per panel.
UPDATE_LOAD_LUT = const(0xB1)
UPDATE_FULL = const(0xF7)
UPDATE_PARTIAL = const(0xFF)
# 3Ch: 05h = GS transition, follow LUT, LUT1 (white border); 80h = VBD at VCOM (border not
# driven during partial updates).  Bit meanings [DS1680] 3Ch; values as used in [WS].
BORDER_FULL = const(0x05)
BORDER_PARTIAL = const(0x80)
TEMP_INTERNAL = const(0x80)
DEEP_SLEEP_MODE1 = const(0x01)

RESET_MS = 10   # RES# low / recovery: datasheet gives no minimum pulse width; 10 ms is conservative
SW_RESET_WAIT_MS = 10   # flow step 2: "SW Reset by Command 0x12, Wait 10ms"
POLL_MS = 5


class BusyTimeout(OSError):
    """BUSY stayed high longer than the timeout (panel not connected, asleep, or broken)."""


class _EPD(framebuf.FrameBuffer):
    PHYS_W = 122
    PHYS_H = 250
    FULL_MS = 3000
    PARTIAL_MS = 300
    RED_FULL_MS = 15000
    CHIP = "ssd168x"

    def __init__(self, spi=None, cs=None, dc=None, rst=None, busy=None, width=None, height=None,
                 *, red=False, rotation=0, full_refresh_ms=None, partial_refresh_ms=None,
                 busy_timeout_ms=None):
        if spi is None or cs is None or dc is None or busy is None:
            raise ValueError("%s needs spi, cs, dc and busy (rst strongly recommended)" % self.CHIP)
        self.spi, self.cs, self.dc, self.rst, self.busy = spi, cs, dc, rst, busy
        self.phys_w = width or self.PHYS_W      # sources (X)
        self.phys_h = height or self.PHYS_H     # gates (Y)
        self.rotation = int(rotation) % 4
        if self.rotation % 2:
            self.width, self.height = self.phys_h, self.phys_w
        else:
            self.width, self.height = self.phys_w, self.phys_h
        self.has_red = bool(red)
        self._row_bytes = (self.phys_w + 7) // 8
        nbytes = ((self.width + 7) // 8) * self.height
        self.buffer = bytearray(b"\xff" * nbytes)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.red_buffer = bytearray(nbytes) if red else None
        self.red = framebuf.FrameBuffer(self.red_buffer, self.width, self.height,
                                        framebuf.MONO_HLSB) if red else None
        if full_refresh_ms is None:
            full_refresh_ms = self.RED_FULL_MS if red else self.FULL_MS
        self.full_refresh_ms = full_refresh_ms
        self.partial_refresh_ms = self.PARTIAL_MS if partial_refresh_ms is None else partial_refresh_ms
        self.busy_timeout_ms = busy_timeout_ms
        self.full_refreshes = 0
        self.partial_refreshes = 0
        self.refresh_ms_total = 0
        nphys = self._row_bytes * self.phys_h
        # physical-orientation scratch buffer (only needed when rotated)
        self._phys = bytearray(nphys) if self.rotation else None
        # image currently on the panel = "old" image for partial updates (white after init)
        self._prev = bytearray(b"\xff" * nphys)
        self._asleep = True
        self._warned_red_partial = False
        self.cs.value(1)
        self.init()

    # ------------------------------------------------------------ low level
    def _command(self, cmd, data=None):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes((cmd,)))
        if data is not None:
            self.dc.value(1)
            self.spi.write(data)
        self.cs.value(1)

    def _timeout(self, expected_ms):
        if self.busy_timeout_ms is not None:
            return self.busy_timeout_ms
        return max(5000, 3 * expected_ms)

    def wait_busy(self, timeout_ms):
        """Poll BUSY (high = busy) until low; returns the measured ms, raises BusyTimeout."""
        t0 = time.ticks_ms()
        while self.busy.value():
            if time.ticks_diff(time.ticks_ms(), t0) > timeout_ms:
                raise BusyTimeout(110, "%s: BUSY still high after %d ms" % (self.CHIP, timeout_ms))
            time.sleep_ms(POLL_MS)
        return time.ticks_diff(time.ticks_ms(), t0)

    def _hw_reset(self):
        if self.rst is None:
            return
        self.rst.value(1)
        time.sleep_ms(RESET_MS)
        self.rst.value(0)
        time.sleep_ms(RESET_MS)
        self.rst.value(1)
        time.sleep_ms(RESET_MS)

    # ------------------------------------------------------------ datasheet flow
    def init(self):
        """Steps 2-4 of [DS1680] Fig 9-1: HW reset, SW reset, init code, load LUT."""
        self._hw_reset()
        self.wait_busy(self._timeout(0))
        self._command(CMD_SW_RESET)
        time.sleep_ms(SW_RESET_WAIT_MS)
        self.wait_busy(self._timeout(0))
        mux = self.phys_h - 1
        self._command(CMD_DRIVER_OUTPUT, bytes((mux & 0xFF, (mux >> 8) & 0x01, 0x00)))
        self._command(CMD_DATA_ENTRY, b"\x03")
        self._command(CMD_RAM_X_WINDOW, bytes((0x00, (self._row_bytes - 1) & 0x3F)))
        self._command(CMD_RAM_Y_WINDOW, bytes((0x00, 0x00, mux & 0xFF, (mux >> 8) & 0x01)))
        self._command(CMD_BORDER, bytes((BORDER_FULL,)))
        self._command(CMD_TEMP_SENSOR, bytes((TEMP_INTERNAL,)))
        self._command(CMD_UPDATE_CTRL2, bytes((UPDATE_LOAD_LUT,)))
        self._command(CMD_MASTER_ACTIVATION)
        self.wait_busy(self._timeout(0))
        self._asleep = False

    def sleep(self):
        """Deep sleep mode 1 (RAM kept, ~1 uA typ. [DS1680] Table 11-1); exit needs HW reset."""
        if self.rst is None:
            raise ValueError("%s.sleep(): only a hardware reset (RST pin) leaves deep sleep" % self.CHIP)
        self._command(CMD_DEEP_SLEEP, bytes((DEEP_SLEEP_MODE1,)))
        self._asleep = True

    def _to_phys(self, src):
        """Logical (rotated) MONO_HLSB buffer -> panel RAM order (X bytes along sources)."""
        if not self.rotation:
            return src
        pw, ph = self.phys_w, self.phys_h
        s = framebuf.FrameBuffer(src, self.width, self.height, framebuf.MONO_HLSB)
        d = framebuf.FrameBuffer(self._phys, pw, ph, framebuf.MONO_HLSB)
        r = self.rotation
        for y in range(self.height):
            for x in range(self.width):
                if r == 1:      # 90 deg clockwise (direction 待核实 on a panel)
                    px, py = pw - 1 - y, x
                elif r == 2:
                    px, py = pw - 1 - x, ph - 1 - y
                else:
                    px, py = y, ph - 1 - x
                d.pixel(px, py, s.pixel(x, y))
        return self._phys

    def _write_ram(self, cmd, data):
        self._command(CMD_RAM_X_COUNTER, b"\x00")
        self._command(CMD_RAM_Y_COUNTER, b"\x00\x00")
        self._command(cmd, data)

    def _refresh(self, partial):
        if self._asleep:
            self.init()
        if partial and self.has_red:
            if not self._warned_red_partial:
                print("%s: partial refresh not supported on 3-colour panels; full refresh" % self.CHIP)
                self._warned_red_partial = True
            partial = False
        bw = self._to_phys(self.buffer)
        # flow step 5: 4Eh/4Fh, 24h, 26h, (0Ch soft start left at its POR value), 22h, 20h, BUSY
        if partial:
            self._command(CMD_BORDER, bytes((BORDER_PARTIAL,)))
            self._write_ram(CMD_WRITE_BW, bw)
            self._write_ram(CMD_WRITE_RED, self._prev)       # old image for Display Mode 2
            self._prev[:] = bw
            self._command(CMD_UPDATE_CTRL2, bytes((UPDATE_PARTIAL,)))
            expected = self.partial_refresh_ms
        else:
            self._command(CMD_BORDER, bytes((BORDER_FULL,)))
            self._write_ram(CMD_WRITE_BW, bw)
            self._prev[:] = bw          # before bw's scratch buffer is reused for the red layer
            if self.has_red:
                self._write_ram(CMD_WRITE_RED, self._to_phys(self.red_buffer))
            else:
                self._write_ram(CMD_WRITE_RED, bw)           # keep both RAMs equal (B/W panel)
            self._command(CMD_UPDATE_CTRL2, bytes((UPDATE_FULL,)))
            expected = self.full_refresh_ms
        self._command(CMD_MASTER_ACTIVATION)
        ms = self.wait_busy(self._timeout(expected))
        self.refresh_ms_total += ms
        if partial:
            self.partial_refreshes += 1
        else:
            self.full_refreshes += 1

    # ------------------------------------------------------------ public API
    def show(self, full=True):
        self._refresh(partial=not full)

    display = show
    refresh = show

    def show_partial(self):
        self._refresh(partial=True)

    display_partial = show_partial
    partial = show_partial

    def clear(self, color=WHITE):
        self.fill(color)
        if self.has_red:
            self.red.fill(0)
        self._refresh(partial=False)


class SSD1680(_EPD):
    """2.13" class panels, 122x250 (portrait) by default; controller max 176x296 [DS1680]."""
    PHYS_W, PHYS_H = 122, 250
    FULL_MS, PARTIAL_MS = 3000, 300
    CHIP = "ssd1680"


class SSD1681(_EPD):
    """1.54" class panels, 200x200 by default (controller max 200x200 [DS1681])."""
    PHYS_W, PHYS_H = 200, 200
    FULL_MS, PARTIAL_MS = 2000, 260
    CHIP = "ssd1681"
