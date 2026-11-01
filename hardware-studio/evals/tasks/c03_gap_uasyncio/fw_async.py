# Eval fixture firmware (MIT): two uasyncio tasks - an LED blinker every 250 ms and a counter
# that redraws an SSD1306 once per second, five times, then prints a summary.
import uasyncio as asyncio
from machine import Pin, I2C
import ssd1306

i2c = I2C(0, scl=Pin(9), sda=Pin(8))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
state = {"blink": 0, "count": 0}


async def blinker():
    led = Pin(2, Pin.OUT)
    while True:
        led.toggle()
        state["blink"] += 1
        await asyncio.sleep_ms(250)


async def counter():
    while state["count"] < 5:
        state["count"] += 1
        oled.fill(0)
        oled.text("n=%d" % state["count"], 0, 0, 1)
        oled.show()
        await asyncio.sleep(1)
    print("count", state["count"], "blinks", state["blink"])


async def main():
    asyncio.create_task(blinker())
    await counter()


asyncio.run(main())
