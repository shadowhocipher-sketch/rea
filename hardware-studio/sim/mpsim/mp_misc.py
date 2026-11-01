"""Small simulated modules: ``micropython``, ``gc``, ``network`` (stub).

* micropython: https://docs.micropython.org/en/latest/library/micropython.html
* gc:          https://docs.micropython.org/en/latest/library/gc.html
* network:     https://docs.micropython.org/en/latest/library/network.WLAN.html
"""

import gc as _pygc
import types

from .runtime import current


def _unsupported(modname):
    def __getattr__(name):
        raise current().unsupported_api(modname, name)
    return __getattr__


# ------------------------------------------------------------------ micropython
def _make_micropython():
    m = types.ModuleType("micropython")
    m.__doc__ = "mpsim: simulated micropython module"

    def const(expr):
        return expr

    def _identity(fn=None, *a, **k):
        return fn

    def opt_level(level=None):
        return 0 if level is None else None

    def alloc_emergency_exception_buf(size):
        return None

    def mem_info(verbose=None):
        print("mem: total=fake, current=fake, peak=fake (simulated)")

    def qstr_info(verbose=None):
        print("qstr pool: simulated")

    def stack_use():
        return 0

    state = {"locked": 0}

    def heap_lock():
        state["locked"] += 1
        return state["locked"] - 1

    def heap_unlock():
        state["locked"] = max(0, state["locked"] - 1)
        return state["locked"]

    def heap_locked():
        return state["locked"]

    def kbd_intr(chr):
        return None

    def schedule(func, arg):
        rt = current()
        rt.check()
        rt.record("micropython_schedule")
        rt.schedule_soft(func, arg)

    for name, fn in list(locals().items()):
        if callable(fn) and not name.startswith("_") and name != "state":
            setattr(m, name, fn)
    m.native = _identity
    m.viper = _identity
    m.asm_thumb = _identity
    m.asm_xtensa = _identity
    m.__getattr__ = _unsupported("micropython")
    return m


# ------------------------------------------------------------------ gc
def _make_gc():
    m = types.ModuleType("gc")
    m.__doc__ = "mpsim: simulated MicroPython gc (memory numbers are fake constants)"
    m.collect = lambda: (_pygc.collect(), None)[1]
    m.enable = lambda: None
    m.disable = lambda: None
    m.isenabled = lambda: True
    m.mem_free = lambda: 150000   # fake: there is no MCU heap to measure
    m.mem_alloc = lambda: 50000   # fake
    m.threshold = lambda amount=None: -1 if amount is None else None
    m.__getattr__ = _unsupported("gc")
    return m


# ------------------------------------------------------------------ network
def _make_network():
    m = types.ModuleType("network")
    m.__doc__ = "mpsim: network stub (no real networking). isconnected() follows stimulus wifi.connect"
    m.STA_IF = 0
    m.AP_IF = 1
    m.STAT_IDLE, m.STAT_CONNECTING, m.STAT_GOT_IP = 1000, 1001, 1010

    class WLAN:
        def __init__(self, interface=0):
            self._if = interface
            self._active = False
            self._connecting = False

        def active(self, is_active=None):
            if is_active is None:
                return self._active
            self._active = bool(is_active)
            current().record("wlan_active", value=self._active)
            return None

        def connect(self, ssid=None, key=None, **kw):
            # never record the key (credential)
            current().record("wlan_connect", ssid=ssid)
            self._connecting = True

        def disconnect(self):
            self._connecting = False

        def isconnected(self):
            rt = current()
            rt.check()
            return bool(self._connecting and rt.stim.wifi.get("connect", False))

        def status(self, param=None):
            if self.isconnected():
                return m.STAT_GOT_IP
            return m.STAT_CONNECTING if self._connecting else m.STAT_IDLE

        def ifconfig(self, cfg=None):
            if self.isconnected():
                return ("192.168.4.2", "255.255.255.0", "192.168.4.1", "192.168.4.1")
            return ("0.0.0.0", "0.0.0.0", "0.0.0.0", "0.0.0.0")

        def config(self, *a, **kw):
            return None

        def scan(self):
            return []

    m.WLAN = WLAN
    m.__getattr__ = _unsupported("network")
    return m


micropython = _make_micropython()
gc = _make_gc()
network = _make_network()
