"""Driver for a 1602 (16x2) LCD screen with a PCF8574 IO expander
Adapted from the SunFounder library:
https://github.com/sunfounder/esp32-starter-kit
"""

from machine import Pin, I2C
import time

class CharacterDisplay():
    def __init__(self, sda=21, scl=22):
        # Data
        sda = Pin(sda)
        # Clock
        scl = Pin(scl)
        # Initialize I2C bus
        self.bus = I2C(0, sda=sda, scl=scl, freq=400000)

        # Get the address of the display
        self.addr = self.scan_address()

        self.send_command(0x33) # Must initialize to 8-line mode at first
        time.sleep(0.005)
        self.send_command(0x32) # Then initialize to 4-line mode
        time.sleep(0.005)
        self.send_command(0x28) # 2 Lines & 5*7 dots
        time.sleep(0.005)
        self.send_command(0x0C) # Enable display without cursor
        time.sleep(0.005)
        self.send_command(0x01) # Clear Screen
        self.bus.writeto(self.addr, bytearray([0x08]))

    def scan_address(self):
        # Scan the bus for a list of addresses of the other devices on the bus
        addresses = self.bus.scan()
        if not addresses:
            raise Exception("No devices found")

        # My device has an address of 0x27
        if 0x27 in addresses:
            return 0x27

        raise Exception("Device not found with address 0x27")

    def write_word(self, data):
        temp = data
        temp |= 0x08
        self.bus.writeto(self.addr, bytearray([temp]))

    def send_command(self, command):
        # Send top 4 bits
        data = command & 0xF0
        # Set the enable pin (specific to this display)
        data |= 0x04

        self.write_word(data)
        time.sleep(0.002)

        # Clear the enable pin
        data &= 0xFB
        self.write_word(data)

        # Send bottom 4 bits
        data = (command & 0x0F) << 4
        # Set the enable pin (specific to this display)
        data |= 0x04

        self.write_word(data)
        time.sleep(0.002)

        # Clear the enable pin
        data &= 0xFB
        self.write_word(data)

    def send_data(self, data):
        # Send top 4 bits
        buf = data & 0xF0
        # Set RS(100) and EN(001)
        buf |= 0x05
        self.write_word(buf)
        time.sleep(0.002)
        # Clear enable bit
        buf &= 0xFB
        self.write_word(buf)

        # Send lower 4 bits
        buf = (data & 0x0F) << 4
        # Set RS(100) and EN(001)
        buf |= 0x05
        self.write_word(buf)
        time.sleep(0.002)
        # Clear enable bit
        buf &= 0xFB
        self.write_word(buf)

    def clear_screen(self):
        self.send_command(0x01)

    def enable_backlight(self):
        self.bus.writeto(self.addr, bytearray([0x08]))

    def write_letter_to_coordinate(self, col, row, str):
        # Check that the row and column are in bounds
        if col < 0:
            col = 0
        if col > 15:
            col = 15
        if row < 0:
            row = 0
        if row > 1:
            row = 1

        # Move cursor
        addr = 0x80 + 0x40 * row + col
        self.send_command(addr)

        for chr in str:
            self.send_data(ord(chr))

    def write_message(self, text):
        for char in text:
            if char == '\n':
                self.send_command(0xC0) # next line
            else:
                self.send_data(ord(char))