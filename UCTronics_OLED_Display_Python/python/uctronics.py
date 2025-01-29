# SPDX-License-Identifier: MIT

import os
import fcntl
import time
import numpy as np

I2C_SLAVE_FORCE = 0x0706

ST7735_TFTWIDTH    = 128
ST7735_TFTHEIGHT   = 160

I2C_ADDRESS = 0x18
BURST_MAX_LENGTH  = 160

X_COORDINATE_MAX = 160
X_COORDINATE_MIN = 0
Y_COORDINATE_MAX = 80
Y_COORDINATE_MIN = 0

X_COORDINATE_REG = 0X2A
Y_COORDINATE_REG = 0X2B
CHAR_DATA_REG = 0X2C
SCAN_DIRECTION_REG = 0x36
WRITE_DATA_REG = 0x00
BURST_WRITE_REG = 0X01
SYNC_REG = 0X03

ST7735_MADCTL_MY = 0x80
ST7735_MADCTL_MX = 0x40
ST7735_MADCTL_MV = 0x20
ST7735_MADCTL_ML = 0x10
ST7735_MADCTL_RGB = 0x00
ST7735_MADCTL_BGR = 0x08
ST7735_MADCTL_MH = 0x04

# mini 160x80 display (it's unlikely you want the default orientation)

#ST7735_IS_160X80 = 1
#ST7735_XSTART = 24
#ST7735_YSTART = 0
#ST7735_WIDTH = 80
#ST7735_HEIGHT = 160
##ST7735_ROTATION = (ST7735_MADCTL_MX | ST7735_MADCTL_MY |ST7735_MADCTL_BGR)
#ST7735_ROTATION = (ST7735_MADCTL_BGR)

# mini 160x80, rotate left

#ST7735_IS_160X80 = 1
#ST7735_XSTART = 0
#ST7735_YSTART = 24
#ST7735_WIDTH = 160
#ST7735_HEIGHT = 80
#ST7735_ROTATION = (ST7735_MADCTL_MX | ST7735_MADCTL_MV |ST7735_MADCTL_BGR)


# mini 160x80, rotate right

ST7735_IS_160X80 = 1
ST7735_XSTART = 0
ST7735_YSTART = 24
ST7735_WIDTH = 160
ST7735_HEIGHT = 80
ST7735_ROTATION = (ST7735_MADCTL_MY | ST7735_MADCTL_MV | ST7735_MADCTL_BGR)

#****************************#

ST7735_NOP = 0x00
ST7735_SWRESET = 0x01
ST7735_RDDID = 0x04
ST7735_RDDST = 0x09

ST7735_SLPIN = 0x10
ST7735_SLPOUT = 0x11
ST7735_PTLON = 0x12
ST7735_NORON = 0x13

ST7735_INVOFF = 0x20
ST7735_INVON = 0x21
ST7735_DISPOFF = 0x28
ST7735_DISPON = 0x29
ST7735_CASET = 0x2A
ST7735_RASET = 0x2B
ST7735_RAMWR = 0x2C
ST7735_RAMRD = 0x2E

ST7735_PTLAR = 0x30
ST7735_COLMOD = 0x3A
ST7735_MADCTL = 0x36

ST7735_FRMCTR1 = 0xB1
ST7735_FRMCTR2 = 0xB2
ST7735_FRMCTR3 = 0xB3
ST7735_INVCTR = 0xB4
ST7735_DISSET5 = 0xB6

ST7735_PWCTR1 = 0xC0
ST7735_PWCTR2 = 0xC1
ST7735_PWCTR3 = 0xC2
ST7735_PWCTR4 = 0xC3
ST7735_PWCTR5 = 0xC4
ST7735_VMCTR1 = 0xC5

ST7735_RDID1 = 0xDA
ST7735_RDID2 = 0xDB
ST7735_RDID3 = 0xDC
ST7735_RDID4 = 0xDD

ST7735_PWCTR6 = 0xFC

ST7735_GMCTRP1 = 0xE0
ST7735_GMCTRN1 = 0xE1

# Color definitions
ST7735_BLACK = 0x0000
ST7735_BLUE = 0x001F
ST7735_RED = 0xF800
ST7735_GREEN = 0x07E0
ST7735_CYAN = 0x07FF
ST7735_MAGENTA = 0xF81F
ST7735_YELLOW = 0xFFE0
ST7735_WHITE = 0xFFFF
ST7735_GRAY = 0x8410

def color565(r, g, b):
    """Convert red, green, blue components to a 16-bit 565 RGB value. Components
    should be values 0 to 255.
    """
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def image_to_data(image):
    """Generator function to convert a PIL image to 16-bit 565 RGB bytes."""
    # NumPy is much faster at doing this. NumPy code provided by:
    # Keith (https://www.blogger.com/profile/02555547344016007163)
    pb = np.array(image.convert('RGB')).astype('uint16')
    color = ((pb[:,:,0] & 0xF8) << 8) | ((pb[:,:,1] & 0xFC) << 3) | (pb[:,:,2] >> 3)
    return np.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()

class UCB86(object):
    """Representation of a UC-B86 board with ST7735 LCD"""
    
    def __init__(self, width=ST7735_TFTWIDTH, height=ST7735_TFTHEIGHT, dev='/dev/i2c-1'):
        """Create an instance of the display using SPI communication.  Must
        provide the GPIO pin number for the D/C pin and the SPI driver.  Can
        optionally provide the GPIO pin number for the reset pin as the rst
        parameter.
        """
        self._dev = dev
        self.width = width
        self.height = height
        self.busfd = __openI2C()
        
    def __openI2C(self):
        # I2C Init
        i2cd = os.open(self._dev, os.O_RDWR)
        if i2cd < 0:
            print("Device I2C-1 failed to initialize\n")
            return None
        if fnctl.ioctl(i2cd, I2C_SLAVE_FORCE, I2C_ADDRESS) < 0:
            return None;
        return i2cd;

    def __i2c_write_command(self, command, high, low):
        os.write(self.busfd,bytes([command, high, low]))
        #msg = i2c_msg.write(I2C_ADDRESS,[command, high, low])
        #self._smbus.i2c_rdwr(msg)
        time.sleep(.01)
        
    def __i2c_burst_transfer(self, buff):
        count = 0
        length = len(buff)
        
        self.__i2c_write_command(BURST_WRITE_REG, 0x00, 0x01);
        while length > count:
            if (length - count) > BURST_MAX_LENGTH:
                #write(i2cd, buff + count, BURST_MAX_LENGTH);
                os.write(self.busfd,bytes(buff[count:BURST_MAX_LENGTH]))
                #msg = i2c_msg.write(I2C_ADDRESS,buff[count:BURST_MAX_LENGTH])
                #self._smbus.i2c_rdwr(msg)
                count += BURST_MAX_LENGTH
            else:
                #write(i2cd, buff + count, length - count);
                os.write(self.busfd,bytes(buff[count:]))
                #msg = i2c_msg.write(I2C_ADDRESS,buff[count:])
                #self._smbus.i2c_rdwr(msg)
                count += (length - count)
            time.sleep(0.07);
        self.__i2c_write_command(BURST_WRITE_REG, 0x00, 0x00);
        self.__i2c_write_command(SYNC_REG, 0x00, 0x01);
        
    def __lcd_set_address_window(self, x0, y0, x1, y1):
        """Set display coordinates
        """
        # col address set
        self.__i2c_write_command(X_COORDINATE_REG, x0 + ST7735_XSTART, x1 + ST7735_XSTART)
        # row address set
        self.__i2c_write_command(Y_COORDINATE_REG, y0 + ST7735_YSTART, y1 + ST7735_YSTART)
        # write to RAM
        self.__i2c_write_command(CHAR_DATA_REG, 0x00, 0x00)
        
        self.__i2c_write_command(SYNC_REG, 0x00, 0x01)
        
    def fill_rect(self, x, y, w, h, color):
        buff = [ (color >> 8) & 0xFF, color & 0xFF] * (w*h)
        count = 0
        # clipping
        if (x >= ST7735_WIDTH) or (y >= ST7735_HEIGHT):
            return
        if (x + w - 1) >= ST7735_WIDTH:
            w = ST7735_WIDTH - x
        if (y + h - 1) >= ST7735_HEIGHT:
            h = ST7735_HEIGHT - y
        self.__lcd_set_address_window(x, y, x + w - 1, y + h - 1)

        self.__i2c_burst_transfer(buff)
    
    def fill(self, color):
        self.fill_rect(0, 0, ST7735_WIDTH, ST7735_HEIGHT, color);
        self.__i2c_write_command(SYNC_REG, 0x00, 0x01);
        
    def show(self):
        pass
        
    def image(self, x=0, y=0, w=ST7735_WIDTH, h=ST7735_HEIGHT, data=[]):
        col = h - y
        row = w - x
        formattedData = image_to_data(data)
        self.__lcd_set_address_window(x, y, x + w - 1, y + h - 1)
        self.__i2c_burst_transfer(formattedData)

    def close(self):
        os.close(self.busfd)