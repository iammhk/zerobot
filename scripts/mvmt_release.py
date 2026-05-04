# scripts/mvmt_release.py - Release all motors to save power and allow manual movement.
# Used in actual project for safety and power management.

import smbus2
import sys

# I2C Setup
BUS = None
ADDR = 0x40
try:
    BUS = smbus2.SMBus(1)
except:
    pass

def set_pwm(channel, on, off):
    if BUS:
        try:
            BUS.write_byte_data(ADDR, 0x06 + 4*channel, on & 0xFF)
            BUS.write_byte_data(ADDR, 0x07 + 4*channel, on >> 8)
            BUS.write_byte_data(ADDR, 0x08 + 4*channel, off & 0xFF)
            BUS.write_byte_data(ADDR, 0x09 + 4*channel, off >> 8)
        except:
            pass

def main():
    print("Releasing all servos...")
    for i in range(16):
        set_pwm(i, 0, 0)
    print("Done.")

if __name__ == "__main__":
    main()
