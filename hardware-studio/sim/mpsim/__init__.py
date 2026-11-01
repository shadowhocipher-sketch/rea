"""mpsim - run MicroPython display firmware on a desktop with a virtual clock.

See sim/README.md.  Main entry points:

    from mpsim import run
    result = run("firmware.py", display="ssd1306", max_seconds=10, seed=0)
    result.save("sim_out.gif")
"""

from .runtime import SimStop, SimReboot, SimUnsupported, Frame  # noqa: F401
from .sim import run, session, SimResult, SIM_MODULES, UNSUPPORTED_MODULES  # noqa: F401

__all__ = ["run", "session", "SimResult", "SimStop", "SimReboot", "SimUnsupported", "Frame"]
