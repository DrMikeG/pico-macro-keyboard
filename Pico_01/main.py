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

import board
import digitalio
import monobitmap

 
from third_party.waveshare import epd2in9 as connected_epd

def sample_keys():
    """Yields four bools representing the button press state on the 2.7" EPD.
    
    The 2.7 inch EPD rpi hat has four push buttons connected to RPI hat pins.

    Follow the traces to see which pins those are and wire them up to digital
    inputs D2 through D5 on your CircuitPython device.  A button press grounds
    the pin.

    This function samples them all and yields four bools for each button.
    """
    """
    DigitalInOut = digitalio.DigitalInOut
    Pull = digitalio.Pull
    with DigitalInOut(board.D2) as key1, DigitalInOut(board.D3) as key2, \
            DigitalInOut(board.D4) as key3, DigitalInOut(board.D5) as key4:
        key1.switch_to_input(Pull.UP)
        key2.switch_to_input(Pull.UP)
        key3.switch_to_input(Pull.UP)
        key4.switch_to_input(Pull.UP)
        for k in (key1, key2, key3, key4):
            yield not k.value  # False is pressed
     """

class StatusLED:
    """Dumbed down for simple pico LED"""

    def __init__(self):
        self._led = digitalio.DigitalInOut(board.LED)
        self._led.direction = digitalio.Direction.OUTPUT

    def off(self):
        self._led.value = False

    def busy(self):
        self._led.value = True

    def ready(self):
        self._led.value = True
        
def main():
    led = StatusLED()
    led.busy()

    epd = connected_epd.EPD()
    print("Initializing display...")
    epd.init()

    print("Displaying.")
    epd.clear_frame_memory(0xff)
    epd.display_frame()

    # True is white
    # False is black

    
    #epd.display_bitmap(notFractal.bit_buf, fast_ghosting=True)
    with open("PAGE01.bin", "rb") as binary_file:
        #Read the whole file at once
        PAGE_01 = binary_file.read()
        
    notFractal = monobitmap.MonoBitmap(epd.width, epd.height)
    bitIndex = 0
    for y in range(0,epd.height):
        for x in range(0,epd.width):
            byteIndex = (bitIndex // 8)
            bitOffset = (bitIndex % 8)
            bitMask = 1 << bitOffset
            byteI = PAGE_01[byteIndex]
            val = byteI & bitMask
            if (int(val) == 0):
                print(0, end='')
                notFractal.set_pixel(x, y, True)
            else:
                print(1, end='')
                notFractal.set_pixel(x, y, False )
            bitIndex = bitIndex + 1    
        print("")
    epd.display_bitmap(notFractal.bit_buf, fast_ghosting=True)        
  
    print("Done.")


if __name__ == '__main__':
    main()
