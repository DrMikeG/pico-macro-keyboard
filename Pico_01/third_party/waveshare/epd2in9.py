# Ported to CircuitPython 3.0 by Gregory P. Smith

##
 #  @filename   :   epd2in9.py
 #  @brief      :   Implements for e-paper library
 #  @author     :   Yehui from Waveshare
 #
 #  Copyright (C) Waveshare     September 9 2017
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documnetation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to  whom the Software is
 # furished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 #

import time

from . import epdif

# EPD2IN9 commands
DRIVER_OUTPUT_CONTROL                       = 0x01
BOOSTER_SOFT_START_CONTROL                  = 0x0C
GATE_SCAN_START_POSITION                    = 0x0F
DEEP_SLEEP_MODE                             = 0x10
DATA_ENTRY_MODE_SETTING                     = 0x11
SW_RESET                                    = 0x12
TEMPERATURE_SENSOR_CONTROL                  = 0x1A
MASTER_ACTIVATION                           = 0x20
DISPLAY_UPDATE_CONTROL_1                    = 0x21
DISPLAY_UPDATE_CONTROL_2                    = 0x22
WRITE_RAM                                   = 0x24
WRITE_VCOM_REGISTER                         = 0x2C
WRITE_LUT_REGISTER                          = 0x32
SET_DUMMY_LINE_PERIOD                       = 0x3A
SET_GATE_TIME                               = 0x3B
BORDER_WAVEFORM_CONTROL                     = 0x3C
SET_RAM_X_ADDRESS_START_END_POSITION        = 0x44
SET_RAM_Y_ADDRESS_START_END_POSITION        = 0x45
SET_RAM_X_ADDRESS_COUNTER                   = 0x4E
SET_RAM_Y_ADDRESS_COUNTER                   = 0x4F
TERMINATE_FRAME_READ_WRITE                  = 0xFF


class EPD:
    width = 128
    height = 296

    def __init__(self):
        assert not (self.width & 3), "width must be a multiple of 8"
        self.reset_pin = None
        self.dc_pin = None
        self.busy_pin = None
        self.lut = self.WF_PARTIAL_2IN9

    WF_PARTIAL_2IN9 = bytes([
        0x0,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x80,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x40,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0A,0x0,0x0,0x0,0x0,0x0,0x2,  
        0x1,0x0,0x0,0x0,0x0,0x0,0x0,
        0x1,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,
        0x22,0x17,0x41,0xB0,0x32,0x36,
    ])

    def _delay_ms(self, ms):
        time.sleep(ms / 1000.)

    def _send_command(self, command):
        self.dc_pin.value = 0
        epdif.spi_transfer(command.to_bytes(1, 'big'))

    def _send_data(self, data):
        self.dc_pin.value = 1
        if isinstance(data, int):
            epdif.spi_transfer(data.to_bytes(1, 'big'))
        else:
            # The EPD needs CS to cycle hi between every byte so we loop doing
            # one byte transfers to cause that.  Not efficient, but it makes
            # it work.  Data sheets say needs to be at least a 60ns CS pulse.
            for i in range(len(data)):
                epdif.spi_transfer(data[i:i+1])

    @property
    def fb_bytes(self):
        return self.width * self.height // 8

    def init(self, lut=None):
        try:
            epdif.epd_io_bus_init()
        except RuntimeError:
            pass  # It avoids global io bus reinitialization.  Good.
        self.reset_pin = epdif.RST_PIN
        self.dc_pin = epdif.DC_PIN
        self.busy_pin = epdif.BUSY_PIN
        # EPD hardware init start
        self.lut = lut or self.WF_PARTIAL_2IN9
        self.reset()

        self._send_command(0x12);  #SWRESET

        self._send_command(DRIVER_OUTPUT_CONTROL) # 0x01
        #self._send_data((self.height - 1) & 0xFF)
        #self._send_data(((self.height - 1) >> 8) & 0xFF)
        self._send_data(0x27);
        self._send_data(0x01);
        self._send_data(0x00)                     # GD = 0 SM = 0 TB = 0
        
        self._send_command(0x01); #Driver output control
        self._send_data(0x03)                     # X increment Y increment

        #self.SetWindow(0, 0, self.width-1, self.height-1);
        self._set_memory_area(0, 0, self.width-1, self.height-1)

        #DISPLAY_UPDATE_CONTROL_1                    = 0x21
        self._send_command(0x21); #  Display update control
        self._send_data(0x00)
        self._send_data(0x80)

        #self.SetCursor(0, 0);
        self._set_memory_pointer(0, 0)

        #self.SendLut();
        self.set_lut(self.lut)
        self._send_command(0x37); 
        self._send_data(0x00);  
        self._send_data(0x00);  
        self._send_data(0x00);  
        self._send_data(0x00); 
        self._send_data(0x00);  	
        self._send_data(0x40);  
        self._send_data(0x00);  
        self._send_data(0x00);   
        self._send_data(0x00);  
        self._send_data(0x00);

        self._send_command(0x3C); #BorderWavefrom
        self._send_data(0x80);

        self._send_command(0x22); 
        self._send_data(0xC0);   
        self._send_command(0x20); 

    def wait_until_idle(self):
        while self.busy_pin.value == 1:      # 0: idle, 1: busy
            self._delay_ms(10)

##
 #  @brief: module reset.
 #          often used to awaken the module in deep sleep,
 ##
    def reset(self):
        self.reset_pin.value = 0         # module reset
        self._delay_ms(200)
        self.reset_pin.value = 1
        self._delay_ms(200)

##
 #  @brief: set the look-up table register
 ##
    def set_lut(self, lut=None):
        self._send_command(WRITE_LUT_REGISTER)
        self._send_data(self.WF_PARTIAL_2IN9)


##
 #  @brief: put an image to the frame memory.
 #          this won't update the display.
 ##
    def set_frame_memory(self, bitmap, x, y):
        """Place bitmap at x (multiple of 8), y in the EPD frame buffer.

        bitmap: A MonoBitmap instance; must be a multiple of 8 wide.
        """
        bitmap_width = 128
        bitmap_height = 296

        if x & 0x7 or bitmap_width & 0x7 or x < 0 or y < 0:
            raise ValueError('bad x, y, or width: %d, %d, %d'
                             % (x, y, bitmap_width))
        image_width = bitmap_width
        image_height = bitmap_height
        if (x + image_width >= self.width):
            x_end = self.width - 1
        else:
            x_end = x + image_width - 1
        if (y + image_height >= self.height):
            y_end = self.height - 1
        else:
            y_end = y + image_height - 1
        self._set_memory_area(x, y, x_end, y_end)
        for j in range(y, y_end + 1):
            # The 2.13" display only likes receiving one row of data per WRITE_RAM.
            # At a guess: Internally it may be bit based and does this to avoid
            # implementing skipping partial end of row bytes given the non
            # multiple of 8 width resolution?
            self._set_memory_pointer(x, j)
            offset = j * self.width // 8
            self._send_command(WRITE_RAM)
            self._send_data(bitmap[offset+x:offset+(x_end//8)+1])

    def clear_frame_memory(self, pattern=0xff):
        """Fill the frame memory with a pattern byte. Does not call update."""
        self._set_memory_area(0, 0, self.width - 1, self.height - 1)
        self._set_memory_pointer(0, 0)
        row = pattern.to_bytes(1, 'big') * ((self.width + 7) // 8)
        for j in range(self.height):
            # Some displays only accept one row of data per WRITE_RAM.
            self._set_memory_pointer(0, j)
            self._send_command(WRITE_RAM)
            self._send_data(row)

##
 #  @brief: update the display
 #          there are 2 memory areas embedded in the e-paper display
 #          but once this function is called,
 #          the the next action of SetFrameMemory or ClearFrame will 
 #          set the other memory area.
 ##
    def display_frame(self):
        """Calling this will swap the display for the other buffer."""
        self._send_command(DISPLAY_UPDATE_CONTROL_2)
        self._send_data(0xF7)
        self._send_command(MASTER_ACTIVATION)
        self._send_command(TERMINATE_FRAME_READ_WRITE)
        self.wait_until_idle()

    def display_frame_buf(self, frame_buffer, fast_ghosting=False):
        assert len(frame_buffer) == self.fb_bytes
        for _ in range(2):
            self._set_memory_area(0, 0, self.width-1, self.height-1)
            for j in range(0, self.height):
                # Some displays only accept one row of data per WRITE_RAM.
                self._set_memory_pointer(0, j)
                offset = j * self.width // 8
                self._send_command(WRITE_RAM)
                self._send_data(frame_buffer[offset:offset + (self.width//8) + 1])
            self.display_frame()
            if fast_ghosting:
                break

    def display_bitmap(self, bitmap, fast_ghosting=False):
        """Render a MonoBitmap onto the display.

        Args:
          bitmap: A MonoBitmap instance
          fast_ghosting: If true the display update is twice as fast by only
              refreshing once; this can leave a ghost of the previous contents.
        """
        # TODO: add partial update support.
        # if bitmap size is full frame size and x/y offsets are 0:
        #     epd.init(epd.lut_full_update)
        # else:
        #     epd.init(epd.lut_partial_update)

        self.clear_frame_memory()

        self.set_frame_memory(bitmap, 0, 0)
        self.display_frame()
        if not fast_ghosting:
            self.set_frame_memory(bitmap, 0, 0)
            self.display_frame()

##
 #  @brief: specify the memory area for data R/W
 ##
    def _set_memory_area(self, x_start, y_start, x_end, y_end):
        if x_start & 0x7:
            raise ValueError('x must be a multiple of 8 (%d)' % (x_start,))
        self._send_command(SET_RAM_X_ADDRESS_START_END_POSITION) # 0x44
        self._send_data((x_start >> 3) & 0xFF)
        self._send_data((x_end >> 3) & 0xFF)
        self._send_command(SET_RAM_Y_ADDRESS_START_END_POSITION) # 0x45
        self._send_data(y_start & 0xFF)
        self._send_data((y_start >> 8) & 0xFF)
        self._send_data(y_end & 0xFF)
        self._send_data((y_end >> 8) & 0xFF)

##
 #  @brief: specify the start point for data R/W
 ##
    def _set_memory_pointer(self, x, y):
        if x & 0x7:
            raise ValueError('x must be a multiple of 8')
        self._send_command(SET_RAM_X_ADDRESS_COUNTER) # 0x4E
        #self._send_data((x >> 3) & 0xFF)
        self._send_data(x & 0xFF)
        self._send_command(SET_RAM_Y_ADDRESS_COUNTER) # 0x4F
        self._send_data(y & 0xFF)
        self._send_data((y >> 8) & 0xFF)
        self.wait_until_idle()

##
 #  @brief: After this command is transmitted, the chip would enter the
 #          deep-sleep mode to save power.
 #          The deep sleep mode would return to standby by hardware reset.
 #          You can use reset() to awaken or init() to initialize
 ##
    def sleep(self):
        self._send_command(DEEP_SLEEP_MODE)
        self.wait_until_idle()

