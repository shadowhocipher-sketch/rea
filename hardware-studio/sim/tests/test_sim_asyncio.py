"""asyncio / uasyncio on the virtual clock (sim/mpsim/mp_asyncio.py).

Expected behaviour follows the MicroPython asyncio docs
https://github.com/micropython/micropython/blob/master/docs/library/asyncio.rst
"""
import os
import sys
import textwrap
import time as real_time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from mpsim import run  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def fw(tmp_path, body, name="main_fw.py"):
    p = tmp_path / name
    p.write_text(textwrap.dedent(body), encoding="utf-8")
    return p


def lines(r):
    return [ln for ln in r.console.splitlines() if ln.strip()]


def test_c03_fixture_runs_on_virtual_clock():
    t = real_time.monotonic()
    r = run(os.path.join(ROOT, "evals/tasks/c03_gap_uasyncio/fw_async.py"), display="ssd1306",
            max_seconds=8, echo=False)
    assert real_time.monotonic() - t < 10           # 5 s virtual, no real waiting
    assert r.stop_reason == "finished", r.error
    assert "count 5 blinks 20" in r.console or "count 5 blinks 21" in r.console
    assert r.virtual_ms == 5000
    # 1 frame from the driver's init show() (as micropython-lib ssd1306) + 5 counter redraws
    assert len(r.frames) == 6
    assert [round(f.t_ms) for f in r.frames[1:]] == [0, 1000, 2000, 3000, 4000]
    led = [v for _t, v in r.pin_history(2)]
    assert len(led) >= 20 and r.unsupported == []


def test_sleep_order_create_task_gather_and_return_values(tmp_path):
    p = fw(tmp_path, """
        import uasyncio as asyncio, time
        log = []
        async def worker(name, ms, n):
            for i in range(n):
                await asyncio.sleep_ms(ms)
                log.append((time.ticks_ms() // 10 * 10, name))
            return name * 2
        async def main():
            t = asyncio.create_task(worker("a", 30, 3))
            res = await asyncio.gather(worker("b", 50, 2), t)
            print("res", res)
            print("log", log)
            print("t", asyncio.sleep(0.25) is not None)
        asyncio.run(main())
    """)
    r = run(p, max_seconds=5, echo=False)
    assert r.stop_reason == "finished", r.error
    assert "res ['bb', 'aa']" in r.console
    assert "log [(30, 'a'), (50, 'b'), (60, 'a'), (90, 'a'), (100, 'b')]" in r.console


def test_same_time_wakeups_run_fifo_and_sleep_zero_yields(tmp_path):
    p = fw(tmp_path, """
        import asyncio
        out = []
        async def t(name):
            for i in range(2):
                out.append(name + str(i))
                await asyncio.sleep(0)
        async def main():
            asyncio.create_task(t("x"))
            asyncio.create_task(t("y"))
            await asyncio.sleep_ms(1)
            print(out)
        asyncio.run(main())
    """)
    r = run(p, max_seconds=1, echo=False)
    assert "['x0', 'y0', 'x1', 'y1']" in r.console


def test_wait_for_timeout_cancels_task_and_cleanup_runs(tmp_path):
    p = fw(tmp_path, """
        import asyncio, time
        async def slow():
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                print("cleanup at", time.ticks_ms() // 100 * 100)
                raise
        async def fast():
            await asyncio.sleep_ms(100)
            return 42
        async def main():
            try:
                await asyncio.wait_for(slow(), 0.5)
            except asyncio.TimeoutError:
                print("timeout at", time.ticks_ms() // 100 * 100)
            print("fast", await asyncio.wait_for_ms(fast(), 1000))
            print("none", await asyncio.wait_for(fast(), None))
        asyncio.run(main())
    """)
    r = run(p, max_seconds=30, echo=False)
    assert r.stop_reason == "finished", r.error
    assert lines(r) == ["cleanup at 500", "timeout at 500", "fast 42", "none 42"]
    assert r.virtual_ms < 800                      # did not wait for slow()'s 10 s


def test_event_lock_and_cancel(tmp_path):
    p = fw(tmp_path, """
        import asyncio
        ev = asyncio.Event()
        lock = asyncio.Lock()
        out = []
        async def waiter(i):
            await ev.wait()
            out.append("w%d" % i)
        async def critical(i):
            async with lock:
                out.append("in%d" % i)
                await asyncio.sleep_ms(10)
                out.append("out%d" % i)
        async def forever():
            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                out.append("cancelled")
                raise
        async def main():
            ws = [asyncio.create_task(waiter(i)) for i in range(2)]
            await asyncio.sleep_ms(5)
            print("is_set", ev.is_set())
            ev.set()
            await asyncio.gather(*ws)
            await asyncio.gather(critical(1), critical(2))
            print("locked", lock.locked())
            f = asyncio.create_task(forever())
            await asyncio.sleep_ms(1)
            print("cancel", f.cancel(), "done", f.done())
            try:
                await f
            except asyncio.CancelledError:
                out.append("await raised")
            print("again", f.cancel())
            try:
                asyncio.current_task().cancel()
            except RuntimeError as e:
                print("self", e)
            print(out)
        asyncio.run(main())
    """)
    r = run(p, max_seconds=5, echo=False)
    assert r.stop_reason == "finished", r.error
    assert "is_set False" in r.console and "locked False" in r.console
    assert "cancel True done False" in r.console and "again False" in r.console
    assert "self can't cancel self" in r.console
    assert ("['w0', 'w1', 'in1', 'out1', 'in2', 'out2', 'cancelled', 'await raised']"
            in r.console)


def test_threadsafeflag_set_from_pin_irq_and_timer(tmp_path):
    p = fw(tmp_path, """
        import asyncio, time
        from machine import Pin, Timer
        flag = asyncio.ThreadSafeFlag()
        tick = asyncio.ThreadSafeFlag()
        btn = Pin(0, Pin.IN, Pin.PULL_UP)
        btn.irq(lambda p: flag.set(), Pin.IRQ_FALLING)
        Timer(0).init(period=300, mode=Timer.PERIODIC, callback=lambda t: tick.set())
        async def on_button():
            for i in range(2):
                await flag.wait()
                print("button at", time.ticks_ms() // 10 * 10)
        async def on_tick():
            n = 0
            while True:
                await tick.wait()
                n += 1
                if n == 3:
                    print("ticks at", time.ticks_ms() // 10 * 10)
        async def main():
            asyncio.create_task(on_tick())
            await on_button()
        asyncio.run(main())
    """)
    stim = {"buttons": [{"pin": 0, "at_ms": 500, "hold_ms": 50, "active_level": 0},
                        {"pin": 0, "at_ms": 1200, "hold_ms": 50, "active_level": 0}]}
    r = run(p, max_seconds=5, inputs=stim, echo=False)
    assert r.stop_reason == "finished", r.error
    assert lines(r) == ["button at 500", "ticks at 900", "button at 1200"]


def test_time_limit_and_frame_limit_stop_async_firmware(tmp_path):
    p = fw(tmp_path, """
        import asyncio
        from machine import Pin, I2C
        import ssd1306
        oled = ssd1306.SSD1306_I2C(128, 64, I2C(0, scl=Pin(9), sda=Pin(8)))
        async def anim():
            n = 0
            while True:
                oled.fill(0); oled.text(str(n), 0, 0, 1); oled.show()
                n += 1
                await asyncio.sleep_ms(100)
        asyncio.run(anim())
    """)
    r = run(p, max_seconds=2, echo=False)
    assert r.stop_reason == "time_limit" and r.virtual_ms == 2000
    r = run(p, max_frames=7, echo=False)
    assert r.stop_reason == "frame_limit" and len(r.frames) == 7


def test_deadlock_runs_out_clock_with_warning(tmp_path):
    p = fw(tmp_path, """
        import asyncio
        async def main():
            await asyncio.Event().wait()
        asyncio.run(main())
    """)
    r = run(p, max_seconds=3, echo=False)
    assert r.stop_reason in ("time_limit", "sleep_forever") and r.virtual_ms == 3000
    assert any("would wait forever" in w for w in r.warnings)


def test_exceptions_main_raises_and_unretrieved_task_is_reported(tmp_path):
    p = fw(tmp_path, """
        import asyncio
        async def bad():
            raise ValueError("boom")
        async def main():
            asyncio.create_task(bad())
            await asyncio.sleep_ms(10)
            try:
                await asyncio.gather(bad(), asyncio.sleep_ms(5))
            except ValueError as e:
                print("gather raised", e)
            print("gathered", await asyncio.gather(bad(), return_exceptions=True))
            raise KeyError("main")
        try:
            asyncio.run(main())
        except KeyError as e:
            print("run raised", e)
    """)
    r = run(p, max_seconds=1, echo=False)
    assert r.stop_reason == "finished", r.error
    assert "Task exception wasn't retrieved" in r.console and "ValueError: boom" in r.console
    assert "gather raised boom" in r.console
    assert "gathered [ValueError('boom')]" in r.console
    assert "run raised 'main'" in r.console


def test_loop_api_run_forever_stop_and_handler(tmp_path):
    p = fw(tmp_path, """
        import asyncio
        loop = asyncio.get_event_loop()
        seen = []
        loop.set_exception_handler(lambda l, ctx: seen.append(str(ctx["exception"])))
        async def stopper():
            await asyncio.sleep(2)
            loop.stop()
        async def bad():
            raise OSError("x")
        loop.create_task(stopper())
        loop.create_task(bad())
        loop.run_forever()
        print("stopped", seen, loop.get_exception_handler() is not None)
        print("ruc", loop.run_until_complete(asyncio.sleep_ms(1)))
        asyncio.new_event_loop()
    """)
    r = run(p, max_seconds=10, echo=False)
    assert r.stop_reason == "finished", r.error
    assert "stopped ['x'] True" in r.console and "ruc None" in r.console
    assert r.virtual_ms == 2001


def test_streams_are_reported_unsupported(tmp_path):
    p = fw(tmp_path, """
        import asyncio
        async def main():
            await asyncio.open_connection("example.com", 80)
        asyncio.run(main())
    """)
    r = run(p, max_seconds=1, echo=False)
    assert r.stop_reason == "exception" and "asyncio.open_connection" in r.unsupported


def test_asyncio_state_is_lost_on_deepsleep_reboot(tmp_path):
    p = fw(tmp_path, """
        import asyncio, machine
        async def main():
            await asyncio.sleep_ms(100)
            if machine.reset_cause() != machine.DEEPSLEEP_RESET:
                asyncio.create_task(asyncio.sleep(100))   # must not survive the reboot
                machine.deepsleep(1000)
            print("woke, boot ok")
        asyncio.run(main())
    """)
    r = run(p, max_seconds=5, echo=False)
    assert r.stop_reason == "finished", r.error
    assert r.boots == 2 and "woke, boot ok" in r.console
