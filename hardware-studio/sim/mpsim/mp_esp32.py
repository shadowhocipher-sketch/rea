"""Simulated MicroPython ``esp32`` module (wake-source configuration, NVS).

API per https://docs.micropython.org/en/latest/library/esp32.html.
Wake sources configured here are used by machine.lightsleep()/deepsleep() in
the simulator to decide when the chip wakes (see mp_machine._wake_fn).
"""

from .runtime import current

WAKEUP_ALL_LOW = False
WAKEUP_ANY_HIGH = True
HEAP_DATA = 4      # MALLOC_CAP_8BIT
HEAP_EXEC = 1      # MALLOC_CAP_EXEC


def _rt():
    rt = current()
    rt.check()
    return rt


def _pid(p):
    return getattr(p, "_id", p)


def wake_on_touch(wake):
    rt = _rt()
    rt.wake_cfg["touch"] = bool(wake)
    rt.record("esp32_wake_on_touch", wake=bool(wake))


def wake_on_ulp(wake):
    rt = _rt()
    rt.wake_cfg["ulp"] = bool(wake)
    rt.record("esp32_wake_on_ulp", wake=bool(wake))
    if wake:
        rt.warn("esp32.wake_on_ulp: the ULP coprocessor is not simulated; it never wakes the chip")


def wake_on_ext0(pin, level):
    rt = _rt()
    rt.wake_cfg["ext0"] = None if pin is None else (_pid(pin), 1 if level else 0)
    rt.record("esp32_wake_on_ext0", pin=None if pin is None else _pid(pin), level=bool(level))


def wake_on_ext1(pins, level):
    rt = _rt()
    rt.wake_cfg["ext1"] = None if not pins else ([_pid(p) for p in pins], 1 if level else 0)
    rt.record("esp32_wake_on_ext1", pins=None if not pins else [_pid(p) for p in pins], level=bool(level))


def wake_on_gpio(pins, level):
    rt = _rt()
    rt.wake_cfg["gpio"] = None if not pins else ([_pid(p) for p in pins], 1 if level else 0)
    rt.record("esp32_wake_on_gpio", pins=None if not pins else [_pid(p) for p in pins], level=bool(level))


def gpio_deep_sleep_hold(enable):
    _rt().record("esp32_gpio_deep_sleep_hold", enable=bool(enable))


def raw_temperature():
    return 128  # fixed fake value (ESP32 only; Fahrenheit-ish raw units)


def mcu_temperature():
    return 35   # fixed fake value, degrees C (S2/S3/C3)


def idf_heap_info(capabilities):
    # (total, free, largest free block, minimum free seen) - fake numbers
    return [(240000, 180000, 110000, 170000)]


class NVS:
    """In-memory NVS that survives simulated resets; uncommitted writes are lost
    on reset, as the docs warn."""

    def __init__(self, namespace):
        rt = _rt()
        self._ns = namespace
        self._committed = rt.nvs.setdefault(namespace, {})
        self._staged = dict(self._committed)

    def set_i32(self, key, value):
        self._staged[key] = ("i32", int(value))

    def get_i32(self, key):
        v = self._staged.get(key)
        if v is None or v[0] != "i32":
            raise OSError(-4354, "ESP_ERR_NVS_NOT_FOUND")
        return v[1]

    def set_blob(self, key, value):
        self._staged[key] = ("blob", bytes(value))

    def get_blob(self, key, buffer):
        v = self._staged.get(key)
        if v is None or v[0] != "blob":
            raise OSError(-4354, "ESP_ERR_NVS_NOT_FOUND")
        n = min(len(buffer), len(v[1]))
        buffer[:n] = v[1][:n]
        return len(v[1])

    def erase_key(self, key):
        if key not in self._staged:
            raise OSError(-4354, "ESP_ERR_NVS_NOT_FOUND")
        del self._staged[key]

    def commit(self):
        rt = _rt()
        self._committed.clear()
        self._committed.update(self._staged)
        rt.record("nvs_commit", namespace=self._ns)


def __getattr__(name):
    raise current().unsupported_api("esp32", name)
