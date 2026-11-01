"""Simulated MicroPython ``asyncio`` / ``uasyncio`` on the virtual clock.

Behaviour follows the MicroPython asyncio documentation
https://github.com/micropython/micropython/blob/master/docs/library/asyncio.rst
(docs site: https://docs.micropython.org/en/latest/library/asyncio.html) and, where
the documentation is silent, the behaviour of MicroPython's own implementation
(``extmod/asyncio/*.py``, MIT licence) - re-implemented here, not copied:

* ``sleep(t)`` = ``sleep_ms(int(t * 1000))``: millisecond resolution, the wake-up
  time is computed when ``sleep_ms()`` is *called*.  Sleeping advances the
  VIRTUAL clock (``SimRuntime.advance``) - nothing waits in real time, and the
  run's frame / virtual-time limits stop the loop as usual (``SimStop``).
* Tasks that become ready at the same time run in FIFO order.
* ``create_task()`` works before ``run()``; the task runs once a loop runs.
* ``run(coro)`` returns as soon as the main task finishes; other tasks stay
  queued (a later ``run()`` continues them), they are not cancelled.
  ``new_event_loop()`` drops them.
* An exception in the main task propagates out of ``run()``.  An exception in a
  task nobody awaits goes to the loop's exception handler (default: print
  "Task exception wasn't retrieved" + traceback, to the console).
* ``Task.cancel()`` injects ``CancelledError`` (a ``BaseException``); cancelling
  the running task itself raises ``RuntimeError("can't cancel self")``; a task
  that is awaiting another task forwards the cancel to that task.
* ``wait_for`` / ``wait_for_ms``: on timeout the inner task is cancelled, the
  caller waits for it to finish handling the cancel, then gets ``TimeoutError``.
* ``gather(*aws, return_exceptions=False)``: the first exception is raised in the
  caller and the other tasks keep running; cancelling the gather cancels them.
* ``Event.set()`` is documented as not IRQ-safe: it works here but a warning is
  recorded when it is called from an IRQ / timer callback.  ``ThreadSafeFlag``
  is IRQ-safe, self-clearing, and only one task may wait on it.
* When nothing is runnable the loop advances the virtual clock to the next
  simulated event (pin edge, machine.Timer ...).  If nothing at all can wake a
  task, MicroPython would hang; the simulator records a warning and runs out
  the clock (``stop_reason`` = ``sleep_forever`` / ``time_limit``).

Not simulated: TCP streams (``open_connection``, ``start_server``, ``Stream*``)
-> ``SimUnsupported``.  Each scheduling step costs no virtual time, so a task
that loops on ``await sleep_ms(0)`` without reading ``ticks_*`` only ends at
the wall-clock guard.
"""

import heapq
import itertools
import sys
import traceback
import types

from .runtime import current
from .runtime import unsupported as _r_unsupported

__version__ = (3, 0, 0)


class CancelledError(BaseException):
    """Injected into a task by Task.cancel() (BaseException, as in MicroPython)."""


class TimeoutError(Exception):  # noqa: A001 - MicroPython's asyncio.TimeoutError
    """Raised by wait_for / wait_for_ms on timeout."""


_WAIT = object()      # yielded by awaitables that registered the task somewhere else
_TIMEOUT = object()   # wake-up value meaning "the deadline passed"


class _State:
    """Scheduler state of one boot (RAM is lost on reset/deep sleep)."""

    def __init__(self, rt):
        self.rt = rt
        self.heap = []            # (t_us, seq, task|None, token, payload)
        self.seq = itertools.count()
        self.cur = None
        self.running = False
        self.flags_waiting = set()  # ThreadSafeFlag objects with a waiting task
        self.exc_handler = None
        self.stop_task = None
        self.main = None
        self.deadlock_warned = False

    def push(self, t_us, task, token, payload=(None, None)):
        heapq.heappush(self.heap, (int(t_us), next(self.seq), task, token, payload))

    def push_call(self, fn):
        heapq.heappush(self.heap, (self.rt.now_us, next(self.seq), None, 0, fn))

    def ready(self, task, token, value=None, exc=None):
        """Wake ``task`` now if ``token`` still matches its current wait."""
        if not task._done and token == task._token:
            self.push(self.rt.now_us, task, token, (value, exc))

    def require_cur(self, what):
        if self.cur is None:
            raise RuntimeError("%s must be awaited inside a running asyncio task" % what)
        return self.cur


def _st():
    rt = current()
    rt.check()
    st = getattr(rt, "asyncio_state", None)
    if st is None:
        st = rt.asyncio_state = _State(rt)
    return st


# ------------------------------------------------------------------ Task
class Task:
    """A coroutine scheduled on the loop.  Create with create_task(), not directly."""

    def __init__(self, coro, _state=None):
        if not hasattr(coro, "send"):
            raise TypeError("coroutine expected")
        self.coro = coro
        self._st = _state or _st()
        self._done = False
        self._result = None
        self._exc = None
        # Every wait registration remembers the token; resuming or cancelling the
        # task bumps it, so stale wake-ups (timeouts, other waiters) are ignored.
        self._token = 0
        self._waiters = []        # (task, token) awaiting this task
        self._callbacks = []      # gather() completion callbacks
        self._awaiting = None     # Task this task is awaiting (cancel forwarding)
        self._retrieved = False

    def done(self):
        return self._done

    def cancel(self):
        if self._done:
            return False
        st = self._st
        if self is st.cur:
            raise RuntimeError("can't cancel self")
        t = self
        while t._awaiting is not None and not t._awaiting._done:
            t = t._awaiting           # forward to the task it waits on
        if t is st.cur:
            raise RuntimeError("can't cancel self")
        t._token += 1
        st.push(st.rt.now_us, t, t._token, (None, CancelledError()))
        return True

    def __await__(self):
        if not self._done:
            st = self._st
            cur = st.require_cur("await task")
            self._waiters.append((cur, cur._token))
            cur._awaiting = self
            try:
                yield _WAIT
            finally:
                cur._awaiting = None
        self._retrieved = True
        if self._exc is not None:
            raise self._exc
        return self._result

    __iter__ = __await__

    def __repr__(self):
        name = getattr(self.coro, "__qualname__", None) or getattr(self.coro, "__name__", "?")
        return "<Task %s%s>" % (name, " done" if self._done else "")


def _promote(aw):
    return aw if isinstance(aw, Task) else create_task(aw)


def _finish(st, task, result=None, exc=None):
    task._done = True
    task._result = result
    task._exc = exc
    woke = False
    for t, tok in task._waiters:
        if not t._done and tok == t._token:
            st.push(st.rt.now_us, t, tok)
            woke = True
    task._waiters = []
    for cb in list(task._callbacks):
        cb(task)
        woke = True
    if exc is not None and not woke and task is not st.main and not isinstance(exc, CancelledError):
        # Like MicroPython: report later, unless another task retrieves it first.
        def report():
            if not task._retrieved:
                task._retrieved = True
                _loop.call_exception_handler(
                    {"message": "Task exception wasn't retrieved", "exception": exc, "future": task})
        st.push_call(report)


def _step(st, task, value, exc):
    st.cur = task
    try:
        if exc is not None:
            y = task.coro.throw(exc)
        else:
            y = task.coro.send(value)
    except StopIteration as e:
        _finish(st, task, result=e.value)
        return
    except CancelledError as e:
        _finish(st, task, exc=e)
        return
    except Exception as e:  # noqa: BLE001 - task error, handled like MicroPython
        _finish(st, task, exc=e)
        return
    finally:
        st.cur = None
    if y is _WAIT:
        return
    if y is None:
        # bare ``yield`` in a generator-based coroutine: reschedule now
        st.push(st.rt.now_us, task, task._token)
        return
    _step(st, task, None, RuntimeError("mpsim asyncio: unsupported value yielded to the loop: %r" % (y,)))


def _run_until(st, main):
    rt = st.rt
    if st.running:
        raise RuntimeError("asyncio loop is already running")
    st.running = True
    prev_main, st.main = st.main, main
    try:
        while not main._done:
            rt.check()
            while st.heap and st.heap[0][2] is not None and (
                    st.heap[0][2]._done or st.heap[0][3] != st.heap[0][2]._token):
                heapq.heappop(st.heap)       # drop stale wake-ups (e.g. finished wait_for timers)
            if st.heap:
                t_next = st.heap[0][0]
                if t_next > rt.now_us:
                    target = t_next
                    if rt._events and rt._events[0][0] < target:
                        target = rt._events[0][0]   # let IRQs / timers fire first
                    rt.advance(target - rt.now_us)
                    continue
                _t, _s, task, token, payload = heapq.heappop(st.heap)
                if task is None:
                    payload()
                    continue
                if task._done or token != task._token:
                    continue          # stale wake-up
                task._token += 1
                _step(st, task, payload[0], payload[1])
                continue
            # nothing runnable: only simulated events (IRQ, Timer) can wake a task
            if not st.flags_waiting and not st.deadlock_warned:
                st.deadlock_warned = True
                rt.warn("asyncio: no task is scheduled and none waits on a ThreadSafeFlag; "
                        "on MicroPython the loop would wait forever here")
            if rt._events:
                rt.advance(max(0, rt._events[0][0] - rt.now_us))
            else:
                rt.advance_until(None)      # stops the run (sleep_forever / time_limit)
    finally:
        st.running = False
        st.main = prev_main
        st.cur = None
    main._retrieved = True
    if main._exc is not None:
        raise main._exc
    return main._result


# ------------------------------------------------------------------ core functions
def create_task(coro):
    st = _st()
    t = Task(coro, st)
    st.push(st.rt.now_us, t, t._token)
    return t


def current_task():
    st = _st()
    if st.cur is None:
        raise RuntimeError("no running event loop")
    return st.cur


def run(coro):
    st = _st()
    st.rt.record("asyncio_run")
    return _run_until(st, create_task(coro))


@types.coroutine
def _sleep_until(t_us):
    st = _st()
    cur = st.require_cur("sleep")
    st.push(t_us, cur, cur._token)
    yield _WAIT


def sleep_ms(t):
    st = _st()
    return _sleep_until(st.rt.now_us + max(0, int(t)) * 1000)


def sleep(t):
    return sleep_ms(int(t * 1000))


@types.coroutine
def _wait_done_or_deadline(task, t_us):
    """Wait until ``task`` is done or the virtual time reaches ``t_us``; True on timeout."""
    st = _st()
    if task._done:
        return False
    cur = st.require_cur("wait_for")
    task._waiters.append((cur, cur._token))
    st.push(t_us, cur, cur._token, (_TIMEOUT, None))
    v = yield _WAIT
    return v is _TIMEOUT and not task._done


async def _wait_for(aw, deadline_us):
    task = _promote(aw)
    if deadline_us is None:
        return await task
    try:
        timed_out = await _wait_done_or_deadline(task, deadline_us)
    except CancelledError:
        task.cancel()                 # wait_for itself was cancelled
        raise
    if not timed_out:
        return await task
    task.cancel()
    try:
        await task                    # let the task run its cancel handling
    except (CancelledError, Exception):  # noqa: BLE001
        pass
    raise TimeoutError()


def wait_for(aw, timeout):
    st = _st()
    dl = None if timeout is None else st.rt.now_us + max(0, int(timeout * 1000)) * 1000
    return _wait_for(aw, dl)


def wait_for_ms(aw, timeout):
    st = _st()
    dl = None if timeout is None else st.rt.now_us + max(0, int(timeout)) * 1000
    return _wait_for(aw, dl)


@types.coroutine
def _gather(aws, return_exceptions):
    st = _st()
    ts = [_promote(a) for a in aws]
    failed = [None]

    def first_error():
        if return_exceptions:
            return None
        for t in ts:
            if t._done and t._exc is not None:
                return t
        return None

    pending = [t for t in ts if not t._done]
    if pending and first_error() is None:
        cur = st.require_cur("gather")
        tok = cur._token

        def on_done(t):
            if t._exc is not None and not return_exceptions:
                if failed[0] is None:
                    failed[0] = t
                st.ready(cur, tok)
            elif all(x._done for x in ts):
                st.ready(cur, tok)

        for t in pending:
            t._callbacks.append(on_done)
        try:
            yield _WAIT
        except CancelledError:
            for t in ts:
                if not t._done:
                    t.cancel()
            raise
        finally:
            for t in pending:
                if on_done in t._callbacks:
                    t._callbacks.remove(on_done)
    err = failed[0] or first_error()
    if err is not None:
        err._retrieved = True
        raise err._exc
    out = []
    for t in ts:
        t._retrieved = True
        out.append(t._exc if t._exc is not None else t._result)
    return out


def gather(*aws, return_exceptions=False):
    return _gather(aws, return_exceptions)


# ------------------------------------------------------------------ Event / Flag / Lock
class Event:
    def __init__(self):
        self.state = False
        self._waiting = []

    def is_set(self):
        return self.state

    def set(self):
        st = _st()
        if st.rt._in_irq:
            st.rt.warn("asyncio.Event.set() called from an IRQ/timer callback: not safe on "
                       "MicroPython (use asyncio.ThreadSafeFlag)", "asyncio_event_irq")
        for t, tok in self._waiting:
            st.ready(t, tok)
        self._waiting = []
        self.state = True

    def clear(self):
        self.state = False

    @types.coroutine
    def wait(self):
        if not self.state:
            st = _st()
            cur = st.require_cur("Event.wait")
            self._waiting.append((cur, cur._token))
            yield _WAIT
        return True


class ThreadSafeFlag:
    """IRQ-safe flag: set() may be called from IRQs, Timer callbacks, micropython.schedule."""

    def __init__(self):
        self.state = 0
        self._waiter = None

    def set(self):
        self.state = 1
        w = self._waiter
        if w is not None:
            st = _st()
            st.ready(w[0], w[1])

    def clear(self):
        self.state = 0

    @types.coroutine
    def wait(self):
        if not self.state:
            st = _st()
            cur = st.require_cur("ThreadSafeFlag.wait")
            w = self._waiter
            if w is not None and not w[0]._done and w[1] == w[0]._token:
                raise RuntimeError("ThreadSafeFlag: only one task may wait at a time")
            self._waiter = (cur, cur._token)
            st.flags_waiting.add(self)
            try:
                yield _WAIT
            finally:
                self._waiter = None
                st.flags_waiting.discard(self)
        self.state = 0


class Lock:
    def __init__(self):
        self._locked = False
        self._handoff = None      # task the lock was handed to by release()
        self._waiting = []

    def locked(self):
        return self._locked

    def release(self):
        if not self._locked or self._handoff is not None:
            raise RuntimeError("Lock not acquired")
        st = _st()
        while self._waiting:
            t, tok = self._waiting.pop(0)
            if not t._done and tok == t._token:
                self._handoff = t          # stays locked, ownership passes on
                st.ready(t, tok)
                return
        self._locked = False

    @types.coroutine
    def acquire(self):
        if self._locked:
            st = _st()
            cur = st.require_cur("Lock.acquire")
            self._waiting.append((cur, cur._token))
            try:
                yield _WAIT
            except CancelledError:
                if self._handoff is cur:      # handed over but cancelled before running
                    self._handoff = None
                    self.release()
                raise
            self._handoff = None
        self._locked = True
        return True

    async def __aenter__(self):
        return await self.acquire()

    async def __aexit__(self, exc_type, exc, tb):
        self.release()
        return None


# ------------------------------------------------------------------ event loop object
async def _stopper():
    pass


class Loop:
    """The single event loop (get_event_loop() / new_event_loop())."""

    def create_task(self, coro):
        return create_task(coro)

    def run_forever(self):
        st = _st()
        st.stop_task = Task(_stopper(), st)   # not queued until stop()
        _run_until(st, st.stop_task)

    def run_until_complete(self, aw):
        st = _st()
        return _run_until(st, _promote(aw))

    def stop(self):
        st = _st()
        if st.stop_task is not None:
            st.push(st.rt.now_us, st.stop_task, st.stop_task._token)
            st.stop_task = None

    def close(self):
        pass

    def set_exception_handler(self, handler):
        _st().exc_handler = handler

    def get_exception_handler(self):
        return _st().exc_handler

    def default_exception_handler(self, *args):
        context = args[-1]   # (context) as documented, or (loop, context) as MicroPython calls it
        st = _st()
        exc = context.get("exception")
        st.rt.warn("asyncio: %s: %r" % (context.get("message"), exc))
        out = sys.stdout   # MicroPython prints to stderr, which is the same REPL/UART stream
        print(context.get("message"), file=out)
        fut = context.get("future")
        print("future:", fut, "coro=", getattr(fut, "coro", None), file=out)
        if exc is not None:
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=out)

    def call_exception_handler(self, context):
        h = _st().exc_handler
        if h is not None:
            h(self, context)
        else:
            self.default_exception_handler(self, context)


_loop = Loop()


def get_event_loop(runq_len=0, waitq_len=0):
    return _loop


def new_event_loop():
    rt = current()
    rt.check()
    rt.asyncio_state = _State(rt)
    return _loop


def __getattr__(name):
    raise _r_unsupported("asyncio", name)
