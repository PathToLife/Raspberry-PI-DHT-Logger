import Adafruit_SSD1306

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# Note you can change the I2C address by passing an i2c_address parameter like:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

disp.begin()

# Clear display.
disp.clear()
disp.display()
