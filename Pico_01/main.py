# python3: CircuitPython 3.0

# Author: Gregory P. Smith (@gpshead) <greg@krypto.org>
# Author: Dr Mike Gibbens <github@michaelgibbens.co.uk>
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
 
from third_party.waveshare import epd2in9 as connected_epd

keys_pressed = ["Button 0","Button 1","Button 2","Button 3","Button 4"]

keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)

def pretendToBeKeyboard(button):
    keyboard.release_all()  # ..."Release"!
    key = keys_pressed[button]  # Get the corresponding Keycode or string
    if isinstance(key, str):  # If it's a string...
        keyboard_layout.write(key)  # ...Print the string
        keyboard.release_all()  # ..."Release"!


def main():

    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT

    button0 = digitalio.DigitalInOut(board.GP0)
    button0.switch_to_input(pull=digitalio.Pull.DOWN)
    button1 = digitalio.DigitalInOut(board.GP1)
    button1.switch_to_input(pull=digitalio.Pull.DOWN)
    button2 = digitalio.DigitalInOut(board.GP2)
    button2.switch_to_input(pull=digitalio.Pull.DOWN)
    button3 = digitalio.DigitalInOut(board.GP3)
    button3.switch_to_input(pull=digitalio.Pull.DOWN)
    button4 = digitalio.DigitalInOut(board.GP4)
    button4.switch_to_input(pull=digitalio.Pull.DOWN)

    epd = connected_epd.EPD()
    print("Initializing display...")
    epd.init()

    print("Displaying.")
    epd.clear_frame_memory(0xff)
    epd.display_frame()
    
    #epd.display_bitmap(notFractal.bit_buf, fast_ghosting=True)
    with open("PAGE01.bin", "rb") as binary_file:
        #Read the whole file at once
        PAGE_01 = binary_file.read()
    epd.display_bitmap(PAGE_01, fast_ghosting=True)
  
    print("Done.")
    while True:
        led.value = True
        if button0.value:
            led.value = False
            print("You pressed button 0")
            pretendToBeKeyboard(0)
            time.sleep(0.25)
        if button1.value:
            led.value = False
            print("You pressed button 1")
            pretendToBeKeyboard(1)
            time.sleep(0.25)
        if button2.value:
            led.value = False
            print("You pressed button 2")
            pretendToBeKeyboard(2)
            time.sleep(0.25)
        if button3.value:
            led.value = False
            print("You pressed button 3")
            pretendToBeKeyboard(3)
            time.sleep(0.25)
        if button4.value:
            led.value = False
            print("You pressed button 4")
            pretendToBeKeyboard(4)
            time.sleep(0.25)

if __name__ == '__main__':
    main()
