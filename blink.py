"""Example for Pico. Turns on the built-in LED."""
import board
import digitalio
import time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    print("This is a test")
    time.sleep(1)
    led.value = False
    time.sleep(1)
