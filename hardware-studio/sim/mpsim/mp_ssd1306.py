"""Simulated ``ssd1306`` OLED driver with the micropython-lib API.

API (constructor signatures, method names, ``buffer``/``width``/``height``/
``pages`` attributes, I2C/SPI byte traffic) matches micropython-lib's driver:
https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py
(MIT).  This is an independent re-implementation for the simulator: instead of
driving a panel, ``show()`` records a frame.

Notes on behaviour that matches the real driver:

* The driver's ``init_display()`` configures segment remap and COM scan
  direction exactly like ``rotate(1)``; therefore ``rotate(True)`` is the normal
  orientation and ``rotate(False)`` turns the picture by 180 degrees.
* I2C traffic goes through the simulated ``machine.I2C``: if no device ACKs at
  ``addr`` (default 0x3C), construction raises ``OSError`` as on hardware.
* ``poweroff()``/``poweron()``/``invert()``/``contrast()``/``rotate()`` are
  visible immediately on a real panel, so they also record a frame.
"""

import numpy as np

from . import mp_framebuf as framebuf
from . import mp_time as time
from .runtime import current

SET_CONTRAST = 0x81
SET_ENTIRE_ON = 0xA4
SET_NORM_INV = 0xA6
SET_DISP = 0xAE
SET_MEM_ADDR = 0x20
SET_COL_ADDR = 0x21
SET_PAGE_ADDR = 0x22
SET_DISP_START_LINE = 0x40
SET_SEG_REMAP = 0xA0
SET_MUX_RATIO = 0xA8
SET_IREF_SELECT = 0xAD
SET_COM_OUT_DIR = 0xC0
SET_DISP_OFFSET = 0xD3
SET_COM_PIN_CFG = 0xDA
SET_DISP_CLK_DIV = 0xD5
SET_PRECHARGE = 0xD9
SET_VCOM_DESEL = 0xDB
SET_CHARGE_PUMP = 0x8D


class SSD1306(framebuf.FrameBuffer):
    _sim_kind = "oled"

    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self._sim = {"on": False, "contrast": 0x7F, "invert": False, "normal": True}
        rt = current()
        self._sim_id = "ssd1306#%d" % len(rt.displays)
        rt.register_display(self)
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP, SET_MEM_ADDR, 0x00, SET_DISP_START_LINE, SET_SEG_REMAP | 0x01,
            SET_MUX_RATIO, self.height - 1, SET_COM_OUT_DIR | 0x08, SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.width > 2 * self.height else 0x12,
            SET_DISP_CLK_DIV, 0x80, SET_PRECHARGE, 0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL, 0x30, SET_CONTRAST, 0xFF, SET_ENTIRE_ON, SET_NORM_INV,
            SET_IREF_SELECT, 0x30, SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        ):
            self.write_cmd(cmd)
        self._sim.update(on=True, contrast=0xFF, invert=False, normal=True)
        current().record("ssd1306_init", id=self._sim_id, width=self.width, height=self.height)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP)
        self._sim["on"] = False
        self._sim_capture("poweroff")

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)
        self._sim["on"] = True
        self._sim_capture("poweron")

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)
        self._sim["contrast"] = int(contrast) & 0xFF
        self._sim_capture("contrast")

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))
        self._sim["invert"] = bool(invert & 1)
        self._sim_capture("invert")

    def rotate(self, rotate):
        self.write_cmd(SET_COM_OUT_DIR | ((rotate & 1) << 3))
        self.write_cmd(SET_SEG_REMAP | (rotate & 1))
        self._sim["normal"] = bool(rotate & 1)
        self._sim_capture("rotate")

    def show(self):
        x0 = 0
        x1 = self.width - 1
        if self.width != 128:
            col_offset = (128 - self.width) // 2
            x0 += col_offset
            x1 += col_offset
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)
        self._sim_capture("show")

    # -------------------------------------------------------------- sim
    def _sim_capture(self, event):
        lit = self._sim_pixels() != 0
        s = self._sim
        if s["invert"]:
            lit = ~lit
        if not s["on"]:
            lit = np.zeros_like(lit)
        if not s["normal"]:
            lit = lit[::-1, ::-1]
        gray = np.where(lit, 255, 0).astype(np.uint8)
        rgb = np.repeat(gray[:, :, None], 3, axis=2)
        current().record_frame(self._sim_id, "oled", rgb,
                               {"event": event, "contrast": s["contrast"], "on": s["on"]})


class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)


class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.rate = 10 * 1024 * 1024
        dc.init(dc.OUT, value=0)
        res.init(res.OUT, value=0)
        cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        self.res(1)
        time.sleep_ms(1)
        self.res(0)
        time.sleep_ms(10)
        self.res(1)
        super().__init__(width, height, external_vcc)

    def write_cmd(self, cmd):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.spi.init(baudrate=self.rate, polarity=0, phase=0)
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buf)
        self.cs(1)


def __getattr__(name):
    raise current().unsupported_api("ssd1306", name)
