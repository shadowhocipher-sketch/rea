# 替身固件（不是用户 inputs/ 里的案例）。
# 由统筹从零编写，用来在用户案例缺失时验证模拟器和流程。许可证：MIT。
# 目标硬件：ESP32-S3 + SSD1306 0.96 寸 128x64 I2C OLED，MicroPython 1.20 以上（需要 framebuf.ellipse）。
# 状态：未在真机运行。
from machine import Pin, I2C
import ssd1306
import time
import random

W, H = 128, 64
SDA, SCL = 8, 9          # 替身引脚，见同目录 pins.csv

i2c = I2C(0, scl=Pin(SCL), sda=Pin(SDA), freq=400000)
oled = ssd1306.SSD1306_I2C(W, H, i2c)

EYE_W, EYE_H, GAP = 30, 36, 20
CX_L = W // 2 - GAP // 2 - EYE_W // 2
CX_R = W // 2 + GAP // 2 + EYE_W // 2
CY = H // 2


def draw_eye(cx, cy, w, h, px, py):
    """圆角矩形眼睛，h 越小越像闭眼；(px, py) 是瞳孔偏移。"""
    r = min(6, h // 2, w // 2)
    x0, y0 = cx - w // 2, cy - h // 2
    if r > 0:
        oled.fill_rect(x0 + r, y0, w - 2 * r, h, 1)
        oled.fill_rect(x0, y0 + r, w, h - 2 * r, 1)
        for ex, ey in ((x0 + r, y0 + r), (x0 + w - r - 1, y0 + r),
                       (x0 + r, y0 + h - r - 1), (x0 + w - r - 1, y0 + h - r - 1)):
            oled.ellipse(ex, ey, r, r, 1, True)
    else:
        oled.hline(x0, cy, w, 1)
    if h > 16:
        oled.fill_rect(cx - 5 + px, cy - 6 + py, 10, 12, 0)


def frame(h, px, py):
    oled.fill(0)
    draw_eye(CX_L, CY, EYE_W, h, px, py)
    draw_eye(CX_R, CY, EYE_W, h, px, py)
    oled.show()


def blink(px, py):
    for h in (EYE_H, 24, 12, 2, 12, 24, EYE_H):
        frame(h, px, py)
        time.sleep_ms(30)


def main():
    px = py = 0
    next_blink = time.ticks_add(time.ticks_ms(), 2000)
    while True:
        tx, ty = random.randint(-7, 7), random.randint(-5, 5)
        for _ in range(5):                       # 瞳孔平滑移动到目标位置
            px += (tx - px) // 2
            py += (ty - py) // 2
            frame(EYE_H, px, py)
            time.sleep_ms(40)
        if time.ticks_diff(time.ticks_ms(), next_blink) >= 0:
            blink(px, py)
            next_blink = time.ticks_add(time.ticks_ms(), random.randint(1500, 4000))
        time.sleep_ms(random.randint(300, 900))


main()
