# shake.py - "shake to trigger" with a LIS3DH-class accelerometer (I2C):
#            hardware motion interrupt on INT1 (works across deep sleep) plus a
#            pure-software shake detector for boards that only poll samples.
#
# Licence: MIT.
#
# Verification status (2026-11-01):
#   - Verified: ONLY in the hardware-studio desktop simulator (sim/, mpsim):
#     WHO_AM_I check and register writes (values compared with the datasheet
#     tables below), INT1 edge -> SHAKE events with cooldown, deep-sleep wake on
#     INT1, and ShakeDetector on synthetic samples (firmware/tests/test_fw_shake.py).
#     The simulator's I2C devices are register tables only: it does NOT model
#     the sensor, so thresholds and "how hard is a shake" are NOT validated.
#   - NOT verified on any real board or real LIS3DH.  Tune threshold_mg,
#     duration and cooldown_ms on hardware; measure sleep current.
#   - Not verified: which MCU pins can wake from deep sleep on your chip
#     (ESP32-C3: GPIO0-5, see knowledge/mcu/esp32-c3.md) and whether your
#     MicroPython build has esp32.wake_on_gpio / wake_on_ext0 (待核实).
#
# Register facts used here (all from LIS3DH datasheet DocID17530 Rev 2, read from a
# third-party mirror, see knowledge/input/lis3dh.md "寄存器位"):
#   WHO_AM_I 0Fh = 0x33; I2C address 0x18 (SA0=GND) / 0x19 (SA0=VDD)
#   CTRL_REG1 20h: ODR[3:0] LPen Zen Yen Xen      (Table 29-31)
#   CTRL_REG2 21h: HP_IA1 = bit0                  (Table 32-33)
#   CTRL_REG3 22h: I1_IA1 = bit6                  (Table 35-36)
#   CTRL_REG4 23h: FS[1:0] = bits5:4              (Table 37-38)
#   CTRL_REG5 24h: LIR_INT1 = bit3                (Table 40-41)
#   CTRL_REG6 25h: INT_POLARITY = bit1, 0 = active-high (Table 42-43)
#   INT1_CFG 30h: ZHIE=bit5 YHIE=bit3 XHIE=bit1, AOI/6D=0 -> OR (Table 53-55)
#   INT1_SRC 31h: read clears the latched interrupt  (Table 56-57)
#   INT1_THS 32h: 7 bits, 16/32/62/186 mg per LSb at +-2/4/8/16 g (Table 58-59)
#   INT1_DURATION 33h: 7 bits, 1 LSb = 1/ODR       (Table 60-61)
#   OUT_X_L 28h..OUT_Z_H 2Dh, left-justified two's complement; set bit7 of the
#   register address to auto-increment (section 6.1.1).
# Without the high-pass filter one axis always reads ~1 g at rest, so the
# threshold must be above 1 g (default 1.6 g) - or set hp_filter=True.
#
# API references:
#   machine.I2C  https://docs.micropython.org/en/latest/library/machine.I2C.html
#   machine.Pin  https://docs.micropython.org/en/latest/library/machine.Pin.html
#   esp32.wake_on_gpio / wake_on_ext0  https://docs.micropython.org/en/latest/library/esp32.html
#
# Usage:
#   acc = LIS3DH(I2C(0, sda=Pin(4), scl=Pin(5)))          # address auto-detected
#   acc.setup_motion_interrupt(threshold_mg=1600, odr_hz=50, range_g=4)
#   shake = ShakeInput(Pin(3, Pin.IN, Pin.PULL_DOWN), acc, cooldown_ms=800)
#   while True:
#       if shake.update():         # True once per shake (rising INT1 edge, after cooldown)
#           ...
#       time.sleep_ms(20)
#   # before deep sleep: acc.clear_interrupt(); wake_on_int1(Pin(3))
import time

SHAKE = "shake"

CONFIG = {
    "i2c_id": 0, "sda": 4, "scl": 5,
    "addr": None,              # None = probe 0x18 then 0x19
    "int_pin": 3,              # LIS3DH INT1 -> MCU GPIO (must be deep-sleep capable if used for wake)
    "int_pull": "down",        # INT1 is push-pull; a pull-down keeps the pin defined while the sensor is off
    "range_g": 4,
    "odr_hz": 50,
    "low_power": True,         # LPen: 8-bit low-power mode (lowest current per ODR)
    "threshold_mg": 1600,
    "duration": 0,             # samples (1/ODR) above threshold before INT1 asserts
    "hp_filter": False,
    "latch": True,
    "cooldown_ms": 800,
    "poll_ms": 20,
    "demo_seconds": 0,         # 0 = run forever
    "oled_addr": 0x3C,
}

WHO_AM_I, WHO_AM_I_VALUE = 0x0F, 0x33
CTRL_REG1, CTRL_REG2, CTRL_REG3, CTRL_REG4, CTRL_REG5, CTRL_REG6 = 0x20, 0x21, 0x22, 0x23, 0x24, 0x25
OUT_X_L, INT1_CFG, INT1_SRC, INT1_THS, INT1_DURATION = 0x28, 0x30, 0x31, 0x32, 0x33
ODR_CODES = {0: 0, 1: 1, 10: 2, 25: 3, 50: 4, 100: 5, 200: 6, 400: 7}
FS_CODES = {2: 0, 4: 1, 8: 2, 16: 3}
THS_MG_PER_LSB = {2: 16, 4: 32, 8: 62, 16: 186}
ADDRESSES = (0x18, 0x19)


def load_config(defaults, path="config.json"):
    cfg = dict(defaults)
    try:
        import json
        with open(path) as f:
            cfg.update(json.load(f))
    except (OSError, ValueError):
        pass
    return cfg


class SensorError(Exception):
    pass


def motion_registers(threshold_mg, odr_hz=50, range_g=4, duration=0, low_power=True, hp_filter=False,
                     latch=True):
    """Register values for an OR-of-high-events motion interrupt on INT1 (no I/O; testable)."""
    if odr_hz not in ODR_CODES or odr_hz == 0:
        raise ValueError("odr_hz must be one of %s" % sorted(k for k in ODR_CODES if k))
    if range_g not in FS_CODES:
        raise ValueError("range_g must be one of %s" % sorted(FS_CODES))
    ths = int(round(threshold_mg / THS_MG_PER_LSB[range_g]))
    if not 1 <= ths <= 127:
        raise ValueError("threshold %d mg is outside 1..127 LSb at +-%d g" % (threshold_mg, range_g))
    if not 0 <= duration <= 127:
        raise ValueError("duration must be 0..127 samples")
    if not hp_filter and ths * THS_MG_PER_LSB[range_g] <= 1000:
        raise ValueError("without hp_filter the threshold must exceed 1 g (gravity), got %d mg" % threshold_mg)
    return [
        (CTRL_REG1, (ODR_CODES[odr_hz] << 4) | (0x08 if low_power else 0) | 0x07),
        (CTRL_REG2, 0x01 if hp_filter else 0x00),
        (CTRL_REG4, FS_CODES[range_g] << 4),
        (CTRL_REG5, 0x08 if latch else 0x00),
        (CTRL_REG6, 0x00),                       # INT_POLARITY = 0: active-high
        (INT1_THS, ths),
        (INT1_DURATION, duration),
        (INT1_CFG, 0x2A),                        # ZHIE | YHIE | XHIE, OR combination
        (CTRL_REG3, 0x40),                       # I1_IA1 -> INT1 pin (last: enable routing after setup)
    ]


class LIS3DH:
    def __init__(self, i2c, addr=None):
        self.i2c = i2c
        if addr is None:
            found = [a for a in ADDRESSES if a in i2c.scan()]
            if not found:
                raise SensorError("no LIS3DH at 0x18/0x19")
            addr = found[0]
        self.addr = addr
        try:
            who = self.read(WHO_AM_I)
        except OSError as e:
            raise SensorError("no answer at 0x%02x (%s)" % (addr, e))
        if who != WHO_AM_I_VALUE:
            raise SensorError("WHO_AM_I=0x%02x at 0x%02x, expected 0x33" % (who, addr))
        self.range_g = 2

    def read(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def write(self, reg, value):
        self.i2c.writeto_mem(self.addr, reg, bytes([value & 0xFF]))

    def setup_motion_interrupt(self, threshold_mg=1600, odr_hz=50, range_g=4, duration=0, low_power=True,
                               hp_filter=False, latch=True):
        regs = motion_registers(threshold_mg, odr_hz, range_g, duration, low_power, hp_filter, latch)
        for reg, val in regs:
            self.write(reg, val)
        self.range_g = range_g
        self.clear_interrupt()
        return regs

    def clear_interrupt(self):
        """Read INT1_SRC: clears a latched interrupt; returns the source bits."""
        return self.read(INT1_SRC)

    def power_down(self):
        self.write(CTRL_REG1, 0x07)                 # ODR = 0000: power-down, axes still enabled

    def accel_mg(self):
        """(x, y, z) in mg, scaled as full-scale / 32768 from the left-justified 16-bit outputs.
        Approximate: ignores mode-dependent resolution and sensitivity tolerance (待核实 on hardware)."""
        raw = self.i2c.readfrom_mem(self.addr, OUT_X_L | 0x80, 6)
        out = []
        for i in (0, 2, 4):
            v = raw[i] | (raw[i + 1] << 8)
            if v & 0x8000:
                v -= 0x10000
            out.append(v * self.range_g * 1000 // 32768)
        return tuple(out)


class ShakeInput:
    """INT1 rising edge -> one shake event, at most one per cooldown_ms.

    Edge (not level) detection: with a latched interrupt the pin stays high until
    INT1_SRC is read, so the sensor is cleared on each edge."""

    def __init__(self, pin, sensor=None, cooldown_ms=800, clock=None):
        self.pin = pin
        self.sensor = sensor
        self.cooldown_ms = cooldown_ms
        self._clock = clock or time.ticks_ms
        self._last = pin.value()
        self._t_last = None
        self.count = 0
        self.ignored = 0

    def update(self):
        lv = self.pin.value()
        rising = lv and not self._last
        self._last = lv
        if not rising:
            return False
        if self.sensor is not None:
            self.sensor.clear_interrupt()
        now = self._clock()
        if self._t_last is not None and time.ticks_diff(now, self._t_last) < self.cooldown_ms:
            self.ignored += 1
            return False
        self._t_last = now
        self.count += 1
        return True


class ShakeDetector:
    """Software detector for polled samples (no interrupt wiring).

    A "peak" is a sample whose magnitude differs from 1 g by more than
    delta_mg; `peaks` peaks within window_ms make one shake; then cooldown_ms."""

    def __init__(self, delta_mg=600, peaks=3, window_ms=600, cooldown_ms=800):
        self.delta_mg = delta_mg
        self.peaks = peaks
        self.window_ms = window_ms
        self.cooldown_ms = cooldown_ms
        self._hits = []
        self._t_last = None

    def feed(self, t_ms, x, y, z):
        """Feed one sample (mg); returns True when a shake is recognised."""
        mag = (x * x + y * y + z * z) ** 0.5
        if self._t_last is not None and time.ticks_diff(t_ms, self._t_last) < self.cooldown_ms:
            return False
        if abs(mag - 1000) > self.delta_mg:
            if not self._hits or self._hits[-1] != t_ms:
                self._hits.append(t_ms)
        self._hits = [t for t in self._hits if time.ticks_diff(t_ms, t) <= self.window_ms]
        if len(self._hits) >= self.peaks:
            self._hits = []
            self._t_last = t_ms
            return True
        return False


def wake_on_int1(pin, level=1):
    """Configure INT1 as a deep-sleep wake source.  Returns the API used, or None."""
    try:
        import esp32
    except ImportError:
        return None
    if hasattr(esp32, "wake_on_gpio"):          # ESP32-C3/C6 style GPIO wake (待核实 per port)
        esp32.wake_on_gpio((pin,), level)
        return "wake_on_gpio"
    if hasattr(esp32, "wake_on_ext0"):          # ESP32 / S2 / S3 RTC pin
        esp32.wake_on_ext0(pin, level)
        return "wake_on_ext0"
    return None


def make_int_pin(cfg):
    from machine import Pin
    pull = {"down": Pin.PULL_DOWN, "up": Pin.PULL_UP}.get(cfg["int_pull"])
    return Pin(cfg["int_pin"], Pin.IN, pull) if pull is not None else Pin(cfg["int_pin"], Pin.IN)


# ---------------------------------------------------------------------- demo
def demo():
    from machine import I2C, Pin
    cfg = load_config(CONFIG)
    i2c = I2C(cfg["i2c_id"], sda=Pin(cfg["sda"]), scl=Pin(cfg["scl"]))
    try:
        acc = LIS3DH(i2c, cfg["addr"])
    except (SensorError, OSError) as e:
        print("SELFTEST accel FAIL:", e)
        return
    acc.setup_motion_interrupt(cfg["threshold_mg"], cfg["odr_hz"], cfg["range_g"], cfg["duration"],
                               cfg["low_power"], cfg["hp_filter"], cfg["latch"])
    print("SELFTEST accel OK addr=0x%02x" % acc.addr)
    oled = None
    try:
        import ssd1306
        if cfg["oled_addr"] in i2c.scan():
            oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=cfg["oled_addr"])
    except (ImportError, OSError):
        oled = None
    shake = ShakeInput(make_int_pin(cfg), acc, cfg["cooldown_ms"])

    def show():
        if oled:
            oled.fill(0)
            oled.text("shake to go", 0, 0, 1)
            oled.text("shakes: %d" % shake.count, 0, 24, 1)
            oled.show()
    show()
    t0 = time.ticks_ms()
    while not cfg["demo_seconds"] or time.ticks_diff(time.ticks_ms(), t0) < cfg["demo_seconds"] * 1000:
        if shake.update():
            print("EVENT %s %d t=%d" % (SHAKE, shake.count, time.ticks_diff(time.ticks_ms(), t0)))
            show()
        time.sleep_ms(cfg["poll_ms"])


if __name__ == "__main__":
    demo()
