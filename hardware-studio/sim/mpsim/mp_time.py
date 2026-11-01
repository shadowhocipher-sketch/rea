"""Simulated MicroPython ``time`` / ``utime`` on a virtual clock.

Behaviour follows https://docs.micropython.org/en/latest/library/time.html :

* sleep / sleep_ms / sleep_us advance the virtual clock instantly (no real wait).
* ticks_ms / ticks_us / ticks_cpu count from the current boot and wrap at
  TICKS_PERIOD = 2**30 (MICROPY_PY_TIME_TICKS_PERIOD = MP_SMALL_INT_POSITIVE_MASK + 1
  on 32-bit ports, see extmod/modtime.c).  ticks_diff / ticks_add use the same
  ring arithmetic as extmod/modtime.c.
* Each ticks_*() call advances the clock by ``SimRuntime.tick_poll_us``
  (default 50 us) so that busy-wait loops on ticks terminate.  ticks_cpu()
  returns microseconds here (the real esp32 value is a CPU-cycle counter).
* Epoch is 2000-01-01 00:00:00 UTC, as on the esp32 port.  The RTC starts at the
  epoch on power-on unless the stimulus sets "rtc_start" or firmware calls
  machine.RTC().datetime(...).
"""

import datetime as _dt

from .runtime import current

TICKS_PERIOD = 1 << 30
_TICKS_MAX = TICKS_PERIOD - 1
_EPOCH = _dt.datetime(2000, 1, 1)


def _rt():
    rt = current()
    rt.check()
    return rt


def sleep(seconds):
    rt = _rt()
    rt.record("sleep", ms=seconds * 1000)
    rt.advance(int(round(seconds * 1_000_000)))


def sleep_ms(ms):
    rt = _rt()
    rt.advance(int(ms) * 1000)


def sleep_us(us):
    rt = _rt()
    rt.advance(int(us))


def ticks_ms():
    rt = current()
    rt.poll_tick()
    return (rt.ticks_us_raw() // 1000) & _TICKS_MAX


def ticks_us():
    rt = current()
    rt.poll_tick()
    return rt.ticks_us_raw() & _TICKS_MAX


def ticks_cpu():
    return ticks_us()


def ticks_add(ticks, delta):
    if delta + TICKS_PERIOD // 2 - 1 >= TICKS_PERIOD - 1 or delta + TICKS_PERIOD // 2 - 1 < 0:
        raise OverflowError("ticks interval overflow")
    return (ticks + delta) & _TICKS_MAX


def ticks_diff(ticks1, ticks2):
    return ((ticks1 - ticks2 + TICKS_PERIOD // 2) & _TICKS_MAX) - TICKS_PERIOD // 2


def _rtc_seconds_float(rt):
    off = rt.rtc_offset_s or 0
    return off + rt.now_us / 1_000_000


def time():
    rt = _rt()
    return int(_rtc_seconds_float(rt))


def time_ns():
    rt = _rt()
    off = rt.rtc_offset_s or 0
    return off * 1_000_000_000 + rt.now_us * 1000


def gmtime(secs=None):
    if secs is None:
        secs = time()
    d = _EPOCH + _dt.timedelta(seconds=int(secs))
    return (d.year, d.month, d.day, d.hour, d.minute, d.second, d.weekday(),
            d.timetuple().tm_yday)


localtime = gmtime  # the esp32 port has no time zone support


def mktime(t):
    year, month, mday, hour, minute, second = t[:6]
    # normalise out-of-range month/day/hour... fields like C mktime does
    m = int(month) - 1
    d = _dt.datetime(int(year) + m // 12, m % 12 + 1, 1)
    d += _dt.timedelta(days=int(mday) - 1, hours=int(hour), minutes=int(minute), seconds=int(second))
    return int((d - _EPOCH).total_seconds())


def __getattr__(name):
    raise current().unsupported_api("time", name)
