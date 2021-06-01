# ported to CircuitPython 3.0.0-beta0 by Gregory P. Smith

##
 #  @filename   :   epdif.py
 #  @brief      :   EPD hardware interface implements (GPIO, SPI)
 #  @author     :   Yehui from Waveshare
 #
 #  Copyright (C) Waveshare     July 4 2017
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

import adafruit_bus_device.spi_device
import board
import digitalio
import busio

# Pin definition as hooked up on my Metro M4 (reassigned to instances in init)
# These pins are also present on the ItsyBitsy M4
RST_PIN = board.GP12
DC_PIN = board.GP8
CS_PIN = board.GP9
BUSY_PIN = board.GP13

# SPI1_MOSI Pin 11
# SPI1_MISO Pin 8

# We want SPI 1 on PICO
# SPI 1 RX = GP8     Data/Command control pin (High: Data; Low: Command)
# SPI 1 CSn = GP9    CLK SCK pin of SPI interface, clock input
# SPI 1 SCK = GP10    SCK pin of SPI interface, clock input
# SPI 1 Tx = GP11    MOSI pin of SPI interface, data transmitted from Master to Slave.
# SPI 1 Rx = GP12    Reset pin, low active
# SPI 1 CSn? = GP13    Busy pin


#_SPI_MOSI = board.MOSI
#_SPI_CLK = board.SCK
_SPI_MOSI = board.GP11
_SPI_MISO = board.GP12
_SPI_CLK = board.GP10
_SPI_BUS = None
_init = False


def spi_transfer(data):
    with _SPI_BUS as device:
        device.write(data)

def epd_io_bus_init():
    global _init
    if _init:
        raise RuntimeError("epd_io_bus_init() called twice")
    _init = True
    global RST_PIN, DC_PIN, CS_PIN, BUSY_PIN
    DInOut = digitalio.DigitalInOut
    OUTPUT = digitalio.Direction.OUTPUT
    INPUT = digitalio.Direction.INPUT
    RST_PIN = DInOut(RST_PIN)
    RST_PIN.direction = OUTPUT
    DC_PIN = DInOut(DC_PIN)
    DC_PIN.direction = OUTPUT
    CS_PIN = DInOut(CS_PIN)
    CS_PIN.direction = OUTPUT
    BUSY_PIN = DInOut(BUSY_PIN)
    BUSY_PIN.direction = INPUT
    global _SPI_BUS

    """
    # bus vs bitbang isn't really important for slow displays, detecting
    # when to use one vs the other is overkill...
    if (_SPI_CLK == getattr(board, 'SCK', None) and
        _SPI_MOSI == getattr(board, 'MOSI', None)):
        import busio as io_module
    else:
        import bitbangio as io_module
    _SPI_BUS = adafruit_bus_device.spi_device.SPIDevice(
            io_module.SPI(_SPI_CLK, _SPI_MOSI), CS_PIN,
            baudrate=2000000)
    """

    # To setup a SPI bus, you specify the SCK, MOSI (microcontroller out, sensor in), and MISO (microcontroller in, sensor out) pins.
    # The Pico uses a different naming convention for these:
    # SPIx_SCK = SCK
    # SPIx_TX = MOSI
    # SPIx_RX = MISO

    #with busio.SPI(_SPI_CLK, _SPI_MOSI, _SPI_MISO) as spi_bus:
    #   _SPI_BUS = SPIDevice(spi_bus, CS_PIN)
    #_SPI_BUS = busio.SPI(_SPI_CLK, _SPI_MOSI, _SPI_MISO)
    #adafruit_bus_device.spi_device.SPIDevice(spi, chip_select=None, *, baudrate=100000, polarity=0, phase=0, extra_clocks=0)
    _SPI_BUS = adafruit_bus_device.spi_device.SPIDevice(busio.SPI(_SPI_CLK, _SPI_MOSI),CS_PIN ,baudrate=4000_000)

### END OF FILE ###
