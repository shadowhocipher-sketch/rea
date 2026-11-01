# selftest.py - power-on self test: I2C scan against expected devices, display
#               test patterns, battery voltage via ADC divider, result screen,
#               and a bounded JSON-lines log file on the device filesystem.
#
# Licence: MIT.
#
# Verification status (2026-11-01):
#   - Verified: ONLY in the hardware-studio desktop simulator (sim/, mpsim) with a
#     simulated SSD1306 at 0x3C, a simulated sensor address and scripted ADC
#     voltages (firmware/tests/test_fw_selftest.py).
#   - NOT verified on any real board.  In particular NOT verified: real ADC
#     accuracy (the simulator's ADC is linear; ESP32 ADCs are non-linear near the
#     ends of each attenuation range), divider loading of the ADC input, and
#     flash wear from the log file.
#
# API references:
#   machine.I2C.scan            https://docs.micropython.org/en/latest/library/machine.I2C.html
#   machine.ADC.read_uv / atten  https://docs.micropython.org/en/latest/esp32/quickref.html#adc-analog-to-digital-conversion
#     ESP32 attenuation ranges (quickref): ATTN_0DB 100-950 mV, ATTN_2_5DB 100-1250 mV,
#     ATTN_6DB 150-1750 mV, ATTN_11DB 150-2450 mV; read_uv() uses eFuse calibration.
#   framebuf drawing            https://docs.micropython.org/en/latest/library/framebuf.html
#   ssd1306 driver (micropython-lib)
#       https://github.com/micropython/micropython-lib/tree/master/micropython/drivers/display/ssd1306
#
# All pins, addresses, divider ratio and thresholds come from CONFIG / config.json.
# Battery thresholds below are placeholders for a 1-cell Li-ion and must be set
# from your cell's datasheet (they are not sourced facts).
import time

CONFIG = {
    "i2c_id": 0, "sda": 8, "scl": 9, "i2c_freq": 400000,
    "expected_i2c": {"0x3c": "OLED"},              # address -> name; JSON needs string keys
    "display": {"type": "ssd1306", "width": 128, "height": 64, "addr": 0x3C},  # or None
    "pattern_ms": 300,                             # time per test pattern
    "battery_adc_pin": 1,                          # None to skip
    "battery_divider": 2.0,                        # V_batt = V_pin * divider (e.g. 100k/100k)
    "battery_samples": 8,
    "battery_low_v": 3.5, "battery_min_v": 3.3,    # placeholders, see header
    "log_file": "selftest.log", "log_max_bytes": 4096,
    "result_ms": 1500,
}

PASS, WARN, FAIL, SKIP = "PASS", "WARN", "FAIL", "SKIP"


def load_config(defaults, path="config.json"):
    cfg = dict(defaults)
    try:
        import json
        with open(path) as f:
            cfg.update(json.load(f))
    except (OSError, ValueError):
        pass
    return cfg


def _addr(k):
    return int(k, 0) if isinstance(k, str) else int(k)


def check_i2c(i2c, expected):
    """expected: {addr: name}.  Missing devices FAIL, unexpected ones WARN."""
    try:
        found = i2c.scan()
    except OSError as e:
        return [("i2c bus", FAIL, "scan error %s" % e)], []
    res = []
    exp = {_addr(k): v for k, v in expected.items()}
    for a, name in sorted(exp.items()):
        res.append(("i2c %s 0x%02x" % (name, a), PASS if a in found else FAIL,
                    "found" if a in found else "missing"))
    extra = [a for a in found if a not in exp]
    if extra:
        res.append(("i2c extra", WARN, " ".join("0x%02x" % a for a in extra)))
    return res, found


def test_patterns(disp, w, h, pattern_ms):
    """Full on, full off, checkerboard, border + text.  The OPERATOR judges the
    screen; the code can only confirm that drawing and show() did not raise."""
    steps = []
    try:
        disp.fill(1)
        disp.show()
        time.sleep_ms(pattern_ms)
        disp.fill(0)
        disp.show()
        time.sleep_ms(pattern_ms)
        for y in range(0, h, 8):
            for x in range(0, w, 8):
                if (x // 8 + y // 8) % 2 == 0:
                    disp.fill_rect(x, y, 8, 8, 1)
        disp.show()
        time.sleep_ms(pattern_ms)
        disp.fill(0)
        disp.rect(0, 0, w, h, 1)
        disp.line(0, 0, w - 1, h - 1, 1)
        disp.line(0, h - 1, w - 1, 0, 1)
        disp.text("SELF TEST", max(0, (w - 72) // 2), max(0, h // 2 - 4), 1)
        disp.show()
        time.sleep_ms(pattern_ms)
        steps.append(("display patterns", PASS, "4 patterns shown (check visually)"))
    except Exception as e:  # noqa: BLE001 - report any driver failure as a test result
        steps.append(("display patterns", FAIL, repr(e)))
    return steps


def read_battery(cfg):
    from machine import ADC, Pin
    adc = ADC(Pin(cfg["battery_adc_pin"]), atten=ADC.ATTN_11DB)
    n = max(1, cfg["battery_samples"])
    total = 0
    for _ in range(n):
        total += adc.read_uv()
        time.sleep_ms(2)
    v_pin = total / n / 1_000_000
    return v_pin * cfg["battery_divider"]


def check_battery(cfg):
    if cfg.get("battery_adc_pin") is None:
        return [("battery", SKIP, "no ADC pin configured")], None
    try:
        v = read_battery(cfg)
    except Exception as e:  # noqa: BLE001
        return [("battery", FAIL, repr(e))], None
    if v < cfg["battery_min_v"]:
        st = FAIL
    elif v < cfg["battery_low_v"]:
        st = WARN
    else:
        st = PASS
    return [("battery", st, "%.2f V" % v)], v


def write_log(cfg, record):
    """Append one JSON line; truncate (start over) when the file grows too big."""
    import json
    path = cfg.get("log_file")
    if not path:
        return False
    line = json.dumps(record) + "\n"
    try:
        import os
        try:
            size = os.stat(path)[6]
        except OSError:
            size = 0
        mode = "w" if size + len(line) > cfg["log_max_bytes"] else "a"
        with open(path, mode) as f:
            f.write(line)
        return True
    except OSError:
        return False


def show_results(disp, results, w, h):
    disp.fill(0)
    bad = sum(1 for r in results if r[1] == FAIL)
    disp.text("SELFTEST %s" % ("OK" if not bad else "FAIL"), 0, 0, 1)
    y = 12
    for name, st, detail in results:
        if y > h - 8:
            break
        disp.text(("%s %s" % (st[0], name))[: w // 8], 0, y, 1)
        y += 9
    disp.show()


def run_selftest(cfg=None):
    """Run all checks; returns (overall, results).  overall is PASS/WARN/FAIL."""
    from machine import Pin, I2C
    cfg = cfg or load_config(CONFIG)
    t0 = time.ticks_ms()
    results = []
    i2c = I2C(cfg["i2c_id"], scl=Pin(cfg["scl"]), sda=Pin(cfg["sda"]), freq=cfg["i2c_freq"])
    r, found = check_i2c(i2c, cfg["expected_i2c"])
    results += r
    disp = None
    dcfg = cfg.get("display")
    if dcfg and dcfg.get("type") == "ssd1306":
        if dcfg["addr"] in found:
            try:
                import ssd1306
                disp = ssd1306.SSD1306_I2C(dcfg["width"], dcfg["height"], i2c, addr=dcfg["addr"])
            except Exception as e:  # noqa: BLE001
                results.append(("display init", FAIL, repr(e)))
        else:
            results.append(("display init", FAIL, "no ACK at 0x%02x" % dcfg["addr"]))
    if disp is not None:
        results += test_patterns(disp, dcfg["width"], dcfg["height"], cfg["pattern_ms"])
    r, v = check_battery(cfg)
    results += r
    overall = FAIL if any(x[1] == FAIL for x in results) else (
        WARN if any(x[1] == WARN for x in results) else PASS)
    for name, st, detail in results:
        print("SELFTEST %-4s %-22s %s" % (st, name, detail))
    print("SELFTEST overall %s in %d ms" % (overall, time.ticks_diff(time.ticks_ms(), t0)))
    write_log(cfg, {"t": time.time(), "overall": overall, "battery_v": v,
                    "results": [list(x) for x in results]})
    if disp is not None:
        show_results(disp, results, dcfg["width"], dcfg["height"])
        time.sleep_ms(cfg["result_ms"])
    return overall, results


if __name__ == "__main__":
    run_selftest()
