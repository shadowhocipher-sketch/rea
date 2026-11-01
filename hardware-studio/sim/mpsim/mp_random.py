"""Simulated MicroPython ``random`` / ``urandom`` (reproducible with a seed).

API per https://docs.micropython.org/en/latest/library/random.html :
getrandbits, randint, randrange, random, uniform, seed, choice.

The generator is CPython's Mersenne Twister seeded from the run's ``--seed``,
so a run is reproducible, but the NUMBERS DIFFER from a real board (MicroPython
uses the Yasmarang PRNG and, on esp32, seeds it from the hardware RNG at boot).
"""

import random as _pyrandom

from .runtime import current

_gen = _pyrandom.Random(0)


def _reseed_for_run(seed):
    _gen.seed(seed)


def getrandbits(n):
    if not 0 <= n <= 32:
        raise ValueError("bits must be 32 or less")
    return _gen.getrandbits(n) if n else 0


def randint(a, b):
    return _gen.randint(a, b)


def randrange(start, stop=None, step=1):
    if stop is None:
        return _gen.randrange(start)
    return _gen.randrange(start, stop, step)


def random():
    return _gen.random()


def uniform(a, b):
    return _gen.uniform(a, b)


def seed(n=None):
    # Firmware-provided seeds are honoured (still reproducible).  seed(None) on a
    # real board reseeds from hardware entropy; here it reseeds from the run seed.
    current().record("random_seed", n=n)
    _gen.seed(current().seed if n is None else n)


def choice(seq):
    return _gen.choice(seq)


def __getattr__(name):
    raise current().unsupported_api("random", name)
