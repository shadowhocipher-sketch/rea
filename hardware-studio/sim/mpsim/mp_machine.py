"""Simulated MicroPython ``machine`` module (ESP32 flavour).

Behaviour follows https://docs.micropython.org/en/latest/library/machine.html and
the ESP32 quick reference https://docs.micropython.org/en/latest/esp32/quickref.html.
Constant VALUES are the esp32 port's (ports/esp32/machine_pin.c, modmachine.c);
portable firmware only uses them symbolically.

Every call is recorded in the run log (``SimRuntime.log`` / ``log_counts``).
External signals (buttons, touch, ADC voltages, I2C devices) come from the
stimulus (see stimulus.py).  Attributes that are not implemented raise
``SimUnsupported`` (an AttributeError) and are listed in the run result.
"""

from . import runtime as _r
from .runtime import unsupported as _r_unsupported
from .runtime import current, SimReboot

# ---------------------------------------------------------------- constants
IDLE, SLEEP, DEEPSLEEP = 0x01, 0x02, 0x04          # extmod/modmachine.h MACHINE_WAKE_*
PWRON_RESET = _r.PWRON_RESET
HARD_RESET = _r.HARD_RESET
WDT_RESET = _r.WDT_RESET
DEEPSLEEP_RESET = _r.DEEPSLEEP_RESET
SOFT_RESET = _r.SOFT_RESET
PIN_WAKE = EXT0_WAKE = _r.WAKE_EXT0
EXT1_WAKE = _r.WAKE_EXT1
TIMER_WAKE = _r.WAKE_TIMER
TOUCHPAD_WAKE = _r.WAKE_TOUCHPAD
ULP_WAKE = _r.WAKE_ULP

_DEFAULT_I2C_DEVICES = ()


def _rt():
    rt = current()
    rt.check()
    return rt


def _pin_id(p):
    if isinstance(p, Pin):
        return p._id
    return p


# ---------------------------------------------------------------- Pin
class Pin:
    IN = 1                 # GPIO_MODE_INPUT
    OUT = 3                # GPIO_MODE_INPUT_OUTPUT
    OPEN_DRAIN = 7         # GPIO_MODE_INPUT_OUTPUT_OD
    PULL_UP = 1
    PULL_DOWN = 2
    PULL_HOLD = 4
    IRQ_RISING = 1         # GPIO_INTR_POSEDGE
    IRQ_FALLING = 2        # GPIO_INTR_NEGEDGE
    WAKE_LOW = 4           # GPIO_INTR_LOW_LEVEL
    WAKE_HIGH = 5          # GPIO_INTR_HIGH_LEVEL
    IRQ_LOW_LEVEL = 4
    IRQ_HIGH_LEVEL = 5
    DRIVE_0, DRIVE_1, DRIVE_2, DRIVE_3 = 0, 1, 2, 3

    def __init__(self, id, mode=-1, pull=-1, *, value=None, drive=None, alt=None, hold=None):
        self._id = id
        rt = _rt()
        if id not in rt.pins:
            rt.pins[id] = {"mode": None, "pull": None, "out": 0, "history": []}
        self.init(mode, pull, value=value, drive=drive, alt=alt, hold=hold)

    def _st(self):
        rt = _rt()
        st = rt.pins.get(self._id)
        if st is None:  # pin object survived a reboot: re-create its state
            st = rt.pins[self._id] = {"mode": None, "pull": None, "out": 0, "history": []}
        return rt, st

    def init(self, mode=-1, pull=-1, *, value=None, drive=None, alt=None, hold=None):
        rt, st = self._st()
        if mode != -1 and mode is not None:
            st["mode"] = mode
        elif mode is None:
            st["mode"] = None
        if pull != -1:
            st["pull"] = pull
        if drive is not None:
            st["drive"] = drive
        if hold is not None:
            st["hold"] = hold
        rt.record("pin_init", pin=self._id, mode=st["mode"], pull=st["pull"])
        if value is not None:
            self._write(value)

    def _write(self, v):
        rt, st = self._st()
        v = 1 if v else 0
        if st["out"] != v or not st["history"]:
            st["history"].append((rt.now_us, v))
            if len(st["history"]) > 2000:
                del st["history"][:1000]
            rt.record("pin_write", pin=self._id, value=v)
        st["out"] = v

    def _read(self):
        rt, st = self._st()
        mode = st["mode"]
        if mode == Pin.OUT:
            return st["out"]
        ext = rt.stim.level_at(self._id, rt.now_us)
        if mode == Pin.OPEN_DRAIN and st["out"] == 0:
            return 0
        if ext is not None:
            return ext
        if st["pull"] == Pin.PULL_UP:
            return 1
        if st["pull"] == Pin.PULL_DOWN:
            return 0
        rt.warn("Pin(%r) read while floating (no pull, no stimulus) -> 0" % (self._id,),
                key="floating%r" % (self._id,))
        return 0

    def value(self, x=None):
        if x is None:
            return self._read()
        self._write(x)
        return None

    def __call__(self, x=None):
        return self.value(x)

    def on(self):
        self._write(1)

    def off(self):
        self._write(0)

    def high(self):
        self._write(1)

    def low(self):
        self._write(0)

    def toggle(self):
        _, st = self._st()
        self._write(1 - st["out"])

    def mode(self, mode=None):
        rt, st = self._st()
        if mode is None:
            return st["mode"]
        st["mode"] = mode
        return None

    def pull(self, pull=None):
        rt, st = self._st()
        if pull is None:
            return st["pull"]
        st["pull"] = pull
        return None

    def drive(self, drive=None):
        rt, st = self._st()
        if drive is None:
            return st.get("drive", Pin.DRIVE_2)
        st["drive"] = drive
        return None

    def irq(self, handler=None, trigger=3, *, priority=1, wake=None, hard=False):
        rt = _rt()
        rt.irqs[self._id] = {"handler": handler, "trigger": trigger, "wake": wake,
                             "pin_obj": self, "hard": hard}
        rt.record("pin_irq_config", pin=self._id, trigger=trigger, wake=wake)
        return _IRQ(self._id)

    def __repr__(self):
        return "Pin(%r)" % (self._id,)

    def __getattr__(self, name):
        raise _r_unsupported("machine.Pin", name)


class _IRQ:
    def __init__(self, pin):
        self._pin = pin

    def trigger(self):
        return current().irqs.get(self._pin, {}).get("trigger", 0)

    def flags(self):
        return 0


class Signal:
    def __init__(self, pin_or_id, *args, invert=False, **kw):
        self._pin = pin_or_id if isinstance(pin_or_id, Pin) else Pin(pin_or_id, *args, **kw)
        self._inv = bool(invert)

    def value(self, x=None):
        if x is None:
            return self._pin.value() ^ self._inv
        self._pin.value((1 if x else 0) ^ self._inv)
        return None

    def __call__(self, x=None):
        return self.value(x)

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)


# ---------------------------------------------------------------- I2C
class I2C:
    def __init__(self, id=0, *, scl=None, sda=None, freq=400000, timeout=50000):
        self._id = id
        self.init(scl=scl, sda=sda, freq=freq)

    def init(self, scl=None, sda=None, *, freq=400000, timeout=None):
        rt = _rt()
        self._freq = freq
        rt.record("i2c_init", bus=self._id, scl=repr(scl), sda=repr(sda), freq=freq)

    def deinit(self):
        _rt().record("i2c_deinit", bus=self._id)

    @staticmethod
    def _devices(rt):
        return rt.i2c_devices

    def _present(self, rt, addr):
        if addr not in rt.i2c_devices:
            rt.record("i2c_nack", addr=addr)
            raise OSError(19, "ENODEV")  # errno 19 = ENODEV (I2C address not acknowledged)

    def _stat(self, rt, addr, key, n):
        s = rt.i2c_stats.setdefault(addr, {"writes": 0, "write_bytes": 0, "reads": 0, "read_bytes": 0})
        s[key + "s"] += 1
        s[key + "_bytes"] += n

    def scan(self):
        rt = _rt()
        res = sorted(a for a in rt.i2c_devices if 0x08 <= a <= 0x77)
        rt.record("i2c_scan", bus=self._id, found=res)
        return res

    def writeto(self, addr, buf, stop=True):
        rt = _rt()
        self._present(rt, addr)
        self._stat(rt, addr, "write", len(buf))
        return len(buf)

    def writevto(self, addr, vector, stop=True):
        rt = _rt()
        self._present(rt, addr)
        n = sum(len(b) for b in vector)
        self._stat(rt, addr, "write", n)
        return n

    def readfrom(self, addr, nbytes, stop=True):
        rt = _rt()
        self._present(rt, addr)
        self._stat(rt, addr, "read", nbytes)
        return bytes(nbytes)

    def readfrom_into(self, addr, buf, stop=True):
        data = self.readfrom(addr, len(buf), stop)
        buf[:] = data

    def _mem(self, rt, addr):
        m = rt.i2c_mem.get(addr)
        if m is None:
            m = rt.i2c_mem[addr] = bytearray(256)
            for reg, val in rt.stim.i2c_registers.get(addr, {}).items():
                m[reg:reg + len(val)] = val
        return m

    def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8):
        rt = _rt()
        self._present(rt, addr)
        self._stat(rt, addr, "read", nbytes)
        m = self._mem(rt, addr)
        a = memaddr & 0xFF
        return bytes(m[a:a + nbytes]).ljust(nbytes, b"\x00")

    def readfrom_mem_into(self, addr, memaddr, buf, *, addrsize=8):
        buf[:] = self.readfrom_mem(addr, memaddr, len(buf), addrsize=addrsize)

    def writeto_mem(self, addr, memaddr, buf, *, addrsize=8):
        rt = _rt()
        self._present(rt, addr)
        self._stat(rt, addr, "write", len(buf))
        m = self._mem(rt, addr)
        a = memaddr & 0xFF
        m[a:a + len(buf)] = bytes(buf)[: 256 - a]

    # primitive operations (SoftI2C): recorded only
    def start(self):
        _rt().record("i2c_start")

    def stop(self):
        _rt().record("i2c_stop")

    def readinto(self, buf, nack=True):
        _rt()
        for i in range(len(buf)):
            buf[i] = 0

    def write(self, buf):
        _rt().record("i2c_raw_write", n=len(buf))
        return len(buf)

    def __getattr__(self, name):
        raise _r_unsupported("machine.I2C", name)


class SoftI2C(I2C):
    def __init__(self, scl=None, sda=None, *, freq=400000, timeout=50000):
        super().__init__(-1, scl=scl, sda=sda, freq=freq, timeout=timeout)


# ---------------------------------------------------------------- SPI
class SPI:
    MSB = 0
    LSB = 1
    CONTROLLER = MASTER = 0

    def __init__(self, id=1, baudrate=1000000, *, polarity=0, phase=0, bits=8, firstbit=0,
                 sck=None, mosi=None, miso=None, **kw):
        self._id = id
        self.init(baudrate=baudrate, polarity=polarity, phase=phase, bits=bits,
                  firstbit=firstbit, sck=sck, mosi=mosi, miso=miso)

    def init(self, baudrate=None, *, polarity=None, phase=None, bits=None, firstbit=None,
             sck=None, mosi=None, miso=None, **kw):
        rt = _rt()
        if baudrate is not None:
            self._baud = baudrate
        rt.spi_stats.setdefault(self._id, {"inits": 0, "write_bytes": 0, "read_bytes": 0})["inits"] += 1

    def deinit(self):
        _rt()

    def _s(self):
        return _rt().spi_stats.setdefault(self._id, {"inits": 0, "write_bytes": 0, "read_bytes": 0})

    def write(self, buf):
        self._s()["write_bytes"] += len(buf)

    def read(self, nbytes, write=0x00):
        self._s()["read_bytes"] += nbytes
        return bytes(nbytes)

    def readinto(self, buf, write=0x00):
        self._s()["read_bytes"] += len(buf)
        for i in range(len(buf)):
            buf[i] = 0

    def write_readinto(self, write_buf, read_buf):
        s = self._s()
        s["write_bytes"] += len(write_buf)
        s["read_bytes"] += len(read_buf)
        for i in range(len(read_buf)):
            read_buf[i] = 0

    def __getattr__(self, name):
        raise _r_unsupported("machine.SPI", name)


class SoftSPI(SPI):
    def __init__(self, baudrate=500000, *, polarity=0, phase=0, bits=8, firstbit=0,
                 sck=None, mosi=None, miso=None):
        super().__init__(-1, baudrate, polarity=polarity, phase=phase, bits=bits,
                         firstbit=firstbit, sck=sck, mosi=mosi, miso=miso)


# ---------------------------------------------------------------- PWM
class PWM:
    def __init__(self, dest, *, freq=None, duty=None, duty_u16=None, duty_ns=None, invert=False, **kw):
        self._pin = _pin_id(dest)
        self._freq = 5000
        self._duty_u16 = 0
        self.init(freq=freq, duty=duty, duty_u16=duty_u16, duty_ns=duty_ns)

    def _log(self):
        rt = _rt()
        rt.pwm[self._pin] = {"freq": self._freq, "duty_u16": self._duty_u16}
        rt.record("pwm", pin=self._pin, freq=self._freq, duty_u16=self._duty_u16)

    def init(self, *, freq=None, duty=None, duty_u16=None, duty_ns=None, **kw):
        if freq is not None:
            self._freq = int(freq)
        if duty is not None:  # esp32 legacy 0..1023
            self._duty_u16 = int(duty) * 65535 // 1023
        if duty_u16 is not None:
            self._duty_u16 = int(duty_u16)
        if duty_ns is not None:
            self._duty_u16 = min(65535, int(duty_ns * self._freq * 65535 // 1_000_000_000))
        self._log()

    def deinit(self):
        self._duty_u16 = 0
        rt = _rt()
        rt.pwm.pop(self._pin, None)
        rt.record("pwm_deinit", pin=self._pin)

    def freq(self, value=None):
        if value is None:
            return self._freq
        self._freq = int(value)
        self._log()

    def duty_u16(self, value=None):
        if value is None:
            return self._duty_u16
        self._duty_u16 = int(value)
        self._log()

    def duty(self, value=None):
        if value is None:
            return self._duty_u16 * 1023 // 65535
        self._duty_u16 = int(value) * 65535 // 1023
        self._log()

    def duty_ns(self, value=None):
        if value is None:
            return self._duty_u16 * 1_000_000_000 // (65535 * self._freq)
        self._duty_u16 = min(65535, int(value) * self._freq * 65535 // 1_000_000_000)
        self._log()


# ---------------------------------------------------------------- ADC
class ADC:
    ATTN_0DB, ATTN_2_5DB, ATTN_6DB, ATTN_11DB = 0, 1, 2, 3
    WIDTH_9BIT, WIDTH_10BIT, WIDTH_11BIT, WIDTH_12BIT = 9, 10, 11, 12
    # Upper end of the approximate linear range per attenuation, from the ESP32
    # quickref ("ATTN_0DB: 100mV - 950mV ... ATTN_11DB: 150mV - 2450mV").  The
    # simulated ADC is LINEAR from 0 V to this value and saturates above it; a
    # real ESP32 ADC is non-linear near both ends.
    _FULL_SCALE_V = {0: 0.95, 1: 1.25, 2: 1.75, 3: 2.45}

    def __init__(self, pin, *, atten=None, sample_ns=None):
        self._pin = _pin_id(pin)
        self._atten = 0 if atten is None else atten
        self._bits = 12
        _rt().record("adc_init", pin=self._pin, atten=self._atten)

    def init(self, *, atten=None, sample_ns=None):
        if atten is not None:
            self._atten = atten

    def atten(self, atten):
        self._atten = atten

    def width(self, bits):
        self._bits = int(bits)

    def block(self):
        return None

    def deinit(self):
        pass

    def _volts(self):
        rt = _rt()
        v = rt.stim.adc_volts(self._pin, rt.now_us)
        if v is None:
            rt.warn("ADC pin %r has no stimulus voltage -> reads 0 V" % (self._pin,), key="adc%r" % (self._pin,))
            v = 0.0
        rt.record("adc_read", pin=self._pin, volts=round(v, 4))
        return v

    def read_uv(self):
        v = max(0.0, min(self._volts(), self._FULL_SCALE_V[self._atten]))
        return int(round(v * 1000)) * 1000  # millivolt resolution, as documented

    def read_u16(self):
        fs = self._FULL_SCALE_V[self._atten]
        frac = max(0.0, min(self._volts() / fs, 1.0))
        return int(round(frac * 65535))

    def read(self):
        fs = self._FULL_SCALE_V[self._atten]
        frac = max(0.0, min(self._volts() / fs, 1.0))
        return int(round(frac * ((1 << self._bits) - 1)))


# ---------------------------------------------------------------- TouchPad
class TouchPad:
    """ESP32 capacitive touch (machine.TouchPad).  Values come from the stimulus.

    Direction depends on the chip: ESP32 reads SMALLER when touched, ESP32-S2/S3
    read LARGER (quickref "Capacitive touch").  The stimulus gives raw values.
    """

    def __init__(self, pin):
        self._pin = _pin_id(pin)
        _rt().record("touch_init", pin=self._pin)

    def read(self):
        rt = _rt()
        v = rt.stim.touch_value(self._pin, rt.now_us)
        if v is None:
            rt.warn("TouchPad(%r) has no stimulus -> reads 20000" % (self._pin,), key="touch%r" % (self._pin,))
            v = 20000
        return v

    def config(self, value):
        rt = _rt()
        rt.touch_threshold[self._pin] = value
        rt.record("touch_config", pin=self._pin, threshold=value)


# ---------------------------------------------------------------- Timer
class Timer:
    ONE_SHOT = 0
    PERIODIC = 1

    def __init__(self, id=-1, *args, **kw):
        self._id = id
        self._gen = 0
        if args or kw:
            self.init(*args, **kw)

    def init(self, mode=PERIODIC, *, freq=-1, period=-1, tick_hz=1000, callback=None, hard=True):
        rt = _rt()
        self._gen += 1
        if freq is not None and freq > 0:
            period_us = int(round(1_000_000 / freq))
        else:
            period_us = int(round(period * 1_000_000 / tick_hz)) if period and period > 0 else 1000
        self._mode = mode
        self._period_us = max(1, period_us)
        self._cb = callback
        rt.timers[id(self)] = self
        rt.record("timer_init", timer=self._id, mode=mode, period_us=self._period_us)
        self._arm(rt, self._gen)

    def _arm(self, rt, gen):
        def fire():
            if gen != self._gen or rt.timers.get(id(self)) is not self:
                return
            if self._mode == Timer.PERIODIC:
                self._arm(rt, gen)
            if self._cb is not None:
                self._cb(self)
        rt.schedule_at(rt.now_us + self._period_us, fire, tag="timer")

    def deinit(self):
        rt = _rt()
        self._gen += 1
        rt.timers.pop(id(self), None)
        rt.record("timer_deinit", timer=self._id)

    def value(self):
        return 0


# ---------------------------------------------------------------- WDT
class WDT:
    def __init__(self, id=0, timeout=5000):
        rt = _rt()
        self._timeout_us = int(timeout) * 1000
        self._gen = 0
        rt.wdt = self
        rt.record("wdt_init", timeout_ms=timeout)
        self.feed()

    def feed(self):
        rt = _rt()
        self._gen += 1
        gen = self._gen

        def expire():
            if gen == self._gen and rt.wdt is self:
                rt.record("wdt_reset")
                raise SimReboot(WDT_RESET)
        rt.schedule_at(rt.now_us + self._timeout_us, expire, tag="wdt")


# ---------------------------------------------------------------- RTC
class RTC:
    ALARM0 = 0

    def __init__(self, id=0, *args, **kw):
        pass

    def datetime(self, dt=None):
        rt = _rt()
        from . import mp_time
        if dt is None:
            secs = mp_time.time()
            y, mo, d, h, mi, s, wd, _yd = mp_time.gmtime(secs)
            sub = (rt.now_us % 1_000_000)
            return (y, mo, d, wd, h, mi, s, sub)
        y, mo, d, _wd, h, mi, s = dt[:7]
        secs = mp_time.mktime((y, mo, d, h, mi, s, 0, 0))
        rt.rtc_offset_s = secs - rt.now_us // 1_000_000
        rt.record("rtc_set", datetime=list(dt[:7]))
        return None

    def init(self, dt):
        self.datetime(dt)

    def memory(self, data=None):
        rt = _rt()
        if data is None:
            return bytes(rt.rtc_memory)
        if len(data) > 2048:
            raise ValueError("data too large")
        rt.rtc_memory = bytes(data)
        return None

    def __getattr__(self, name):
        raise _r_unsupported("machine.RTC", name)


# ---------------------------------------------------------------- UART
class UART:
    def __init__(self, id, baudrate=115200, *args, **kw):
        self._id = id
        self._pos = 0
        _rt().record("uart_init", uart=id, baudrate=baudrate)

    def init(self, *args, **kw):
        pass

    def deinit(self):
        pass

    def write(self, buf):
        rt = _rt()
        data = buf.encode() if isinstance(buf, str) else bytes(buf)
        rt.uart_tx.setdefault(self._id, bytearray()).extend(data)
        rt.record("uart_write", uart=self._id, n=len(data))
        return len(data)

    def _avail(self):
        rt = _rt()
        buf = b"".join(d for t, d in rt.stim.uart_rx if t <= rt.now_us)
        return buf[self._pos:]

    def any(self):
        return len(self._avail())

    def read(self, nbytes=None):
        data = self._avail()
        if not data:
            return None
        if nbytes is not None:
            data = data[:nbytes]
        self._pos += len(data)
        return data

    def readline(self):
        data = self._avail()
        if not data:
            return None
        i = data.find(b"\n")
        data = data if i < 0 else data[: i + 1]
        self._pos += len(data)
        return data

    def readinto(self, buf, nbytes=None):
        data = self.read(nbytes or len(buf))
        if not data:
            return None
        buf[: len(data)] = data
        return len(data)


# ---------------------------------------------------------------- functions
def reset():
    rt = _rt()
    rt.record("machine_reset")
    rt.run_idle_hooks()
    raise SimReboot(HARD_RESET)


def soft_reset():
    rt = _rt()
    rt.record("machine_soft_reset")
    rt.run_idle_hooks()
    raise SimReboot(SOFT_RESET)


def reset_cause():
    return _rt().reset_cause


def wake_reason():
    return _rt().wake_reason


def wake_pins():
    return _rt().wake_pins


def freq(hz=None):
    rt = _rt()
    if hz is None:
        return rt.cpu_freq
    rt.cpu_freq = int(hz)
    rt.record("cpu_freq", hz=int(hz))
    return None


def unique_id():
    return b"\x24\x0a\xc4\x51\x5e\x01"  # fixed fake id


def idle():
    _rt().advance(1000)  # wait for the next system tick (1 ms on esp32, approx.)


def disable_irq():
    return 0


def enable_irq(state=0):
    return None


def _level_wake(rt, pins, cond, after, until):
    """Earliest t in [after, until] where cond(levels) holds."""
    def levels(t):
        out = []
        for p in pins:
            lv = rt.stim.level_at(p, t)
            if lv is None:
                st = rt.pins.get(p, {})
                lv = 1 if st.get("pull") == Pin.PULL_UP else 0
            out.append(lv)
        return out
    if cond(levels(after)):
        return after
    for t in rt.stim.change_times(pins, after, until):
        if cond(levels(t)):
            return t
    return None


def _wake_fn(deep):
    def fn(after, until):
        rt = current()
        best = None

        def offer(t, reason, pins):
            nonlocal best
            if t is not None and (best is None or t < best[0]):
                best = (t, reason, tuple(pins))
        cfg = rt.wake_cfg
        if cfg.get("ext0"):
            pin, level = cfg["ext0"]
            offer(_level_wake(rt, [pin], lambda lv: lv[0] == level, after, until), EXT0_WAKE, [pin])
        if cfg.get("ext1"):
            pins, level = cfg["ext1"]
            if level:
                t = _level_wake(rt, pins, lambda lv: any(lv), after, until)
            else:
                t = _level_wake(rt, pins, lambda lv: not any(lv), after, until)
            offer(t, EXT1_WAKE, pins)
        if cfg.get("gpio"):
            pins, level = cfg["gpio"]
            t = _level_wake(rt, pins, (lambda lv: any(lv)) if level else (lambda lv: not all(lv)), after, until)
            offer(t, _r.WAKE_GPIO, pins)
        mask = DEEPSLEEP if deep else SLEEP
        for pin, irq in rt.irqs.items():
            w = irq.get("wake")
            if w and (w & mask) and irq["trigger"] in (Pin.WAKE_LOW, Pin.WAKE_HIGH):
                level = irq["trigger"] - Pin.WAKE_LOW
                offer(_level_wake(rt, [pin], lambda lv, L=level: lv[0] == L, after, until),
                      EXT0_WAKE if deep else _r.WAKE_GPIO, [pin])
        if cfg.get("touch"):
            for t, pin in rt.stim.touch_starts(after, until):
                offer(t, TOUCHPAD_WAKE, [])
                break
        return best
    return fn


def lightsleep(time_ms=None):
    rt = _rt()
    rt.run_idle_hooks()
    rt.record("lightsleep", ms=time_ms)
    t0 = rt.now_us
    deadline = None if time_ms is None else rt.now_us + int(time_ms) * 1000
    res = rt.advance_until(deadline, _wake_fn(False))
    rt.stats["lightsleep_ms"] += (rt.now_us - t0) / 1000.0
    if res is None:
        rt.wake_reason, rt.wake_pins = TIMER_WAKE, ()
    else:
        rt.wake_reason, rt.wake_pins = res
    rt.record("wake", reason=rt.wake_reason)


sleep = lightsleep  # deprecated alias, see machine docs


def deepsleep(time_ms=None):
    rt = _rt()
    rt.run_idle_hooks()
    rt.record("deepsleep", ms=time_ms)
    # deep sleep stops the CPU: no more IRQ handlers, timers or watchdog
    wake = _wake_fn(True)
    saved_irqs = dict(rt.irqs)
    rt.irqs = {}
    rt.timers = {}
    rt.wdt = None
    rt._events = [e for e in rt._events if e[3] == "edge"]
    t0 = rt.now_us
    deadline = None if time_ms is None else rt.now_us + int(time_ms) * 1000

    def wake_fn(after, until):
        live = rt.irqs
        rt.irqs = saved_irqs
        try:
            return wake(after, until)
        finally:
            rt.irqs = live
    res = rt.advance_until(deadline, wake_fn)
    rt.stats["deepsleep_ms"] += (rt.now_us - t0) / 1000.0
    if res is None:
        raise SimReboot(DEEPSLEEP_RESET, TIMER_WAKE)
    raise SimReboot(DEEPSLEEP_RESET, res[0], res[1])


def time_pulse_us(pin, pulse_level, timeout_us=1000000):
    rt = _rt()
    pid = _pin_id(pin)
    start = rt.now_us
    lv = rt.stim.level_at(pid, start)
    if lv is None:
        rt.advance(timeout_us)
        return -2
    t = start
    if lv != pulse_level:
        ch = [c for c in rt.stim.change_times([pid], start, start + timeout_us)
              if rt.stim.level_at(pid, c) == pulse_level]
        if not ch:
            rt.advance(timeout_us)
            return -2
        t = ch[0]
    ch = [c for c in rt.stim.change_times([pid], t, t + timeout_us)
          if rt.stim.level_at(pid, c) != pulse_level]
    if not ch:
        rt.advance(t + timeout_us - rt.now_us)
        return -1
    rt.advance(ch[0] - rt.now_us)
    return ch[0] - t


def bitstream(pin, encoding, timing, data):
    _rt().record("bitstream", pin=_pin_id(pin), n=len(data))


def __getattr__(name):
    raise _r_unsupported("machine", name)
