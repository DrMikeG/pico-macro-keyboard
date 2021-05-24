# *****************************************************************************
# * | File        :	  Pico_ePaper-2.9.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-03-16
# # | Info        :   python demo
# -----------------------------------------------------------------------------
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

from machine import Pin, SPI
import framebuf
import utime


# Display resolution
EPD_WIDTH       = 128
EPD_HEIGHT      = 296

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

WF_PARTIAL_2IN9 = [
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
]

class EPD_2in9(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        self.lut = WF_PARTIAL_2IN9
        
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        # UI state data
        self.ui_page = 0
        self.ui_page_max = 3


        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 1):      #  0: idle, 1: busy
            self.delay_ms(10) 
        print("e-Paper busy release")  

    def TurnOnDisplay(self):
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0xF7)
        self.send_command(0x20) # MASTER_ACTIVATION
        self.ReadBusy()

    def TurnOnDisplay_Partial(self):
        self.send_command(0x22) # DISPLAY_UPDATE_CONTROL_2
        self.send_data(0x0F)
        self.send_command(0x20) # MASTER_ACTIVATION
        self.ReadBusy()

    def SendLut(self):
        self.send_command(0x32)
        for i in range(0, 153):
            self.send_data(self.lut[i])
        self.ReadBusy()

    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data((x_start>>3) & 0xFF)
        self.send_data((x_end>>3) & 0xFF)
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data(x & 0xFF)
        
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        self.ReadBusy()
        
    def init(self):
        # EPD hardware init start     
        self.reset()

        self.ReadBusy();   
        self.send_command(0x12);  #SWRESET
        self.ReadBusy();   

        self.send_command(0x01); #Driver output control      
        self.send_data(0x27);
        self.send_data(0x01);
        self.send_data(0x00);
    
        self.send_command(0x11); #data entry mode       
        self.send_data(0x03);

        self.SetWindow(0, 0, self.width-1, self.height-1);

        self.send_command(0x21); #  Display update control
        self.send_data(0x00);
        self.send_data(0x80);	
    
        self.SetCursor(0, 0);
        self.ReadBusy();
        # EPD hardware init end
        return 0

    def display(self, image):
        if (image == None):
            return            
        self.send_command(0x24) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])   
        self.TurnOnDisplay()

    def display_Base(self, image):
        if (image == None):
            return   
        self.send_command(0x24) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])
                
        self.send_command(0x26) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])   
                
        self.TurnOnDisplay()
        
    def display_Partial(self, image):
        if (image == None):
            return
            
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(2)   
        
        self.SendLut();
        self.send_command(0x37); 
        self.send_data(0x00);  
        self.send_data(0x00);  
        self.send_data(0x00);  
        self.send_data(0x00); 
        self.send_data(0x00);  	
        self.send_data(0x40);  
        self.send_data(0x00);  
        self.send_data(0x00);   
        self.send_data(0x00);  
        self.send_data(0x00);

        self.send_command(0x3C); #BorderWavefrom
        self.send_data(0x80);

        self.send_command(0x22); 
        self.send_data(0xC0);   
        self.send_command(0x20); 
        self.ReadBusy();

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)
        
        self.send_command(0x24) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(image[i + j * int(self.width / 8)])
        self.TurnOnDisplay_Partial()

    def Clear(self, color):
        self.send_command(0x24) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(color)
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10) # DEEP_SLEEP_MODE
        self.send_data(0x01)
        
        self.delay_ms(2000)
        self.module_exit()



def countCycles():
    return 10

def drawOptions(epd):
    epd.text("Option     1.a",5, 20, 0x00)
    epd.text("Option     1.b",5, 60, 0x00)
    epd.text("Option     1.c",5,100, 0x00)
    epd.text("Option     1.d",5,140, 0x00)
    epd.text("Option     1.e",5,180, 0x00)

def drawSelectedOption(epd,oldSelection,newSelection):
    # There are 5 rows
    epd.fill_rect(10, 280, 5, 5, 0x00)
    epd.rect(     30, 280, 5, 5, 0x00)

def drawPageIndicators(epd):
    #epd.fill_rect(10, 280, 5, 5, 0x00)
    xStart = 10
    xStep = 20
    yStart = 280
    yStep = 0
    squareSize = 5
    for i in range(0,epd.ui_page_max):
        if i == epd.ui_page:
            epd.fill_rect(xStart+(i*xStep), yStart+(i*yStep), squareSize, squareSize, 0x00)
        else:
            # file white
            epd.fill_rect(xStart+(i*xStep), yStart+(i*yStep), squareSize, squareSize, 0xff)
            # outline black
            epd.rect(xStart+(i*xStep), yStart+(i*yStep), squareSize, squareSize, 0x00)
    #epd.rect(10, 280, 5, 5, 0x00)
    #epd.rect(30, 280, 5, 5, 0x00)
    #epd.rect(50, 280, 5, 5, 0x00)
    #epd.rect(70, 280, 5, 5, 0x00)

def updateEPDThenSleep(epd):
    drawOptions(epd)
    drawPageIndicators(epd)
    epd.display(epd.buffer)
    #print("sleep")
    #epd.sleep()

def mainTask():

    button0 = Pin(0, Pin.IN, Pin.PULL_DOWN)
    button1 = Pin(1, Pin.IN, Pin.PULL_DOWN)
    button2 = Pin(2, Pin.IN, Pin.PULL_DOWN)
    button3 = Pin(3, Pin.IN, Pin.PULL_DOWN)
    button4 = Pin(4, Pin.IN, Pin.PULL_DOWN)
    button5 = Pin(5, Pin.IN, Pin.PULL_DOWN)

    epd = EPD_2in9()
    epd.Clear(0xff)
    epd.fill(0xff)
    updateEPDThenSleep(epd)

    while True:
        if button0.value():
            print("button 0")
        if button1.value():
            print("button 1")
        if button2.value():
            print("button 2")
        if button3.value():
            print("button 3")
        if button4.value():
            print("button 4")
        if button5.value():
            print("button 5")
            
            epd.ui_page = (epd.ui_page+1) % epd.ui_page_max
            print(epd.ui_page)
            updateEPDThenSleep(epd)

if __name__=='__main__':
    mainTask()
    