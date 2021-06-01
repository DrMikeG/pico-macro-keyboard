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
        
def main():

    button0 = digitalio.DigitalInOut(board.GP0)
    button0.switch_to_input(pull=digitalio.Pull.DOWN)
    button1 = digitalio.DigitalInOut(board.GP1)
    button1.switch_to_input(pull=digitalio.Pull.DOWN)

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
        if button0.value:
            print("You pressed button 0")
            time.sleep(0.1)
        if button1.value:
            print("You pressed button 1")
            time.sleep(0.1)

if __name__ == '__main__':
    main()
