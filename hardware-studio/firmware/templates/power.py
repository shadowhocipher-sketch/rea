# power.py - low power and sleep helpers for ESP32-family MicroPython boards:
#            wake-source setup, light/deep sleep, idle timeout, boot counter
#            kept in RTC memory, readable reset/wake reasons.
#
# Licence: MIT.
#
# Verification status (2026-11-01):
#   - Verified: ONLY in the hardware-studio desktop simulator (sim/, mpsim):
#     deep-sleep -> reboot cycle, timer wake, EXT0 button wake, touch wake
#     and RTC-memory boot counter (firmware/tests/test_fw_power.py).
#   - NOT verified on any real board.  Sleep CURRENT is not simulated at all:
#     measure it on hardware (USB-UART bridges, power LEDs, LDO quiescent
#     current and display modules usually dominate on dev boards).
#   - Not verified: which GPIOs can be EXT0/EXT1/touch wake sources on your chip.
#     ESP32: RTC pins 0, 2, 4, 12-15, 25-27, 32-39 (quickref "Deep-sleep mode").
#     ESP32-S2/S3/C3/C6: check the ESP-IDF "Sleep Modes" page for your chip (待核实).
#
# API references (behaviour notes in comments below cite these):
#   machine.lightsleep / deepsleep / reset_cause / wake_reason
#       https://docs.micropython.org/en/latest/library/machine.html#power-related-functions
#   ESP32 deep sleep and reset cause example
#       https://docs.micropython.org/en/latest/esp32/quickref.html#deep-sleep-mode
#   esp32.wake_on_ext0 / wake_on_ext1 / wake_on_touch / WAKEUP_ALL_LOW / WAKEUP_ANY_HIGH
#       https://docs.micropython.org/en/latest/library/esp32.html
#   TouchPad.config + esp32.wake_on_touch
#       https://docs.micropython.org/en/latest/esp32/quickref.html#capacitive-touch
#   RTC.memory (survives deep sleep)
#       https://docs.micropython.org/en/latest/library/machine.RTC.html
#
# Key facts from the docs:
#   * lightsleep keeps RAM and returns; deepsleep does not return - the board
#     restarts main.py and reset_cause() == machine.DEEPSLEEP_RESET.
#   * deepsleep() without an argument sleeps until a configured wake source fires.
#   * A software reset does not change the reset cause (ESP32 quickref).
import time
import machine

# ---- configuration (override with config.json on the device) ----
CONFIG = {
    "mode": "deep",            # "deep" or "light"
    "awake_ms": 8000,          # stay awake this long after the last activity
    "sleep_ms": 20000,         # timer wake; None = only wake on pin/touch
    "wake_pin": 0,             # EXT0 wake pin (button to GND), None to disable
    "wake_level": 0,           # 0 = wake when low (button with pull-up), 1 = when high
    "touch_pin": None,         # touch wake pad, e.g. 7; None to disable
    "touch_threshold": 500,    # TouchPad.config() value, board-specific
    "i2c_id": 0, "sda": 8, "scl": 9, "oled_addr": 0x3C, "width": 128, "height": 64,
}

RESET_NAMES = {
    getattr(machine, "PWRON_RESET", 1): "power-on",
    getattr(machine, "HARD_RESET", 2): "hard reset",
    getattr(machine, "WDT_RESET", 3): "watchdog",
    getattr(machine, "DEEPSLEEP_RESET", 4): "deep-sleep wake",
    getattr(machine, "SOFT_RESET", 5): "soft reset",
}
WAKE_NAMES = {
    getattr(machine, "EXT0_WAKE", 2): "ext0 pin",
    getattr(machine, "EXT1_WAKE", 3): "ext1 pins",
    getattr(machine, "TIMER_WAKE", 4): "timer",
    getattr(machine, "TOUCHPAD_WAKE", 5): "touch",
    getattr(machine, "ULP_WAKE", 6): "ulp",
    7: "gpio",   # ESP_SLEEP_WAKEUP_GPIO, no machine constant
}


def load_config(defaults, path="config.json"):
    cfg = dict(defaults)
    try:
        import json
        with open(path) as f:
            cfg.update(json.load(f))
    except (OSError, ValueError):
        pass
    return cfg


def reset_cause_name():
    return RESET_NAMES.get(machine.reset_cause(), "unknown")


def wake_reason_name():
    try:
        return WAKE_NAMES.get(machine.wake_reason(), "none")
    except AttributeError:          # wake_reason() exists on ESP32 / WiPy only
        return "n/a"


class BootCounter:
    """Counter in RTC memory: survives deep sleep, cleared on power-on."""
    MAGIC = b"BC1"

    def __init__(self):
        self.rtc = machine.RTC()
        raw = self.rtc.memory()
        if machine.reset_cause() != machine.DEEPSLEEP_RESET or len(raw) < 7 or raw[:3] != self.MAGIC:
            self.count = 0
        else:
            self.count = int.from_bytes(raw[3:7], "little")

    def bump(self):
        self.count += 1
        self.rtc.memory(self.MAGIC + self.count.to_bytes(4, "little"))
        return self.count


class IdleTimer:
    def __init__(self, timeout_ms):
        self.timeout_ms = timeout_ms
        self.kick()

    def kick(self):
        self._t = time.ticks_ms()

    def expired(self):
        return time.ticks_diff(time.ticks_ms(), self._t) >= self.timeout_ms


def configure_wake(cfg):
    """Set up wake sources for the next sleep.  Returns a list of descriptions."""
    from machine import Pin
    import esp32
    srcs = []
    if cfg.get("wake_pin") is not None:
        level = cfg.get("wake_level", 0)
        pin = Pin(cfg["wake_pin"], Pin.IN, Pin.PULL_UP if level == 0 else Pin.PULL_DOWN)
        esp32.wake_on_ext0(pin, esp32.WAKEUP_ANY_HIGH if level else esp32.WAKEUP_ALL_LOW)
        srcs.append("ext0 pin %s level %d" % (cfg["wake_pin"], level))
    if cfg.get("touch_pin") is not None:
        from machine import TouchPad
        pad = TouchPad(Pin(cfg["touch_pin"]))
        pad.config(cfg["touch_threshold"])
        esp32.wake_on_touch(True)
        srcs.append("touch pin %s" % cfg["touch_pin"])
    if cfg.get("sleep_ms"):
        srcs.append("timer %d ms" % cfg["sleep_ms"])
    return srcs


def sleep_now(cfg, before_sleep=None):
    """Run the before_sleep hook (turn off displays, sensors...) and sleep.

    Deep sleep does not return; light sleep returns after wake.
    """
    if before_sleep:
        before_sleep()
    ms = cfg.get("sleep_ms")
    if cfg.get("mode", "deep") == "light":
        if ms:
            machine.lightsleep(ms)
        else:
            machine.lightsleep()
        return wake_reason_name()
    if ms:
        machine.deepsleep(ms)
    machine.deepsleep()


# ---------------------------------------------------------------------- demo
def demo():
    from machine import Pin, I2C
    cfg = load_config(CONFIG)
    boots = BootCounter().bump()
    cause, wake = reset_cause_name(), wake_reason_name()
    print("BOOT %d cause=%s wake=%s" % (boots, cause, wake))
    oled = None
    try:
        import ssd1306
        i2c = I2C(cfg["i2c_id"], scl=Pin(cfg["scl"]), sda=Pin(cfg["sda"]))
        if cfg["oled_addr"] in i2c.scan():
            oled = ssd1306.SSD1306_I2C(cfg["width"], cfg["height"], i2c, addr=cfg["oled_addr"])
    except (ImportError, OSError):
        oled = None
    if oled:
        oled.fill(0)
        oled.text("boot %d" % boots, 0, 0, 1)
        oled.text(cause[:16], 0, 16, 1)
        oled.text("wake: " + wake[:10], 0, 32, 1)
        oled.show()
    btn = Pin(cfg["wake_pin"], Pin.IN, Pin.PULL_UP) if cfg.get("wake_pin") is not None else None
    idle = IdleTimer(cfg["awake_ms"])
    while not idle.expired():
        if btn is not None and btn.value() == cfg.get("wake_level", 0):
            idle.kick()               # activity keeps the device awake
        time.sleep_ms(50)
    srcs = configure_wake(cfg)
    print("SLEEP %s wake on: %s" % (cfg["mode"], ", ".join(srcs) or "nothing"))

    def off():
        if oled:
            oled.poweroff()
    r = sleep_now(cfg, off)
    print("WOKE (light) reason=%s" % r)


if __name__ == "__main__":
    demo()
