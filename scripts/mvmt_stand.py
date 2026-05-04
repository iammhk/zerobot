# scripts/mvmt_stand.py - Reset all servos to home position (standing).
# Used in actual project for initialization and recovery.

import smbus2
import sys
import time

# I2C Setup
BUS = None
ADDR = 0x40
try:
    BUS = smbus2.SMBus(1)
except:
    pass

# --- Channel Mapping ---
L1, R1, L2, R2 = 0, 1, 2, 3
L3, R3, L4, R4 = 4, 5, 6, 7
HOME = { L1: 45, R1: 135, L2: 135, R2: 45, L3: 45, R3: 135, L4: 135, R4: 45 }

def set_pwm(channel, on, off):
    if BUS:
        try:
            BUS.write_byte_data(ADDR, 0x06 + 4*channel, on & 0xFF)
            BUS.write_byte_data(ADDR, 0x07 + 4*channel, on >> 8)
            BUS.write_byte_data(ADDR, 0x08 + 4*channel, off & 0xFF)
            BUS.write_byte_data(ADDR, 0x09 + 4*channel, off >> 8)
        except:
            pass

def set_angle(channel, angle):
    pulse_us = 500 + (angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)

def main():
    print("Moving to STAND position...")
    for ch, val in HOME.items():
        set_angle(ch, val)
    print("Standing.")

if __name__ == "__main__":
    main()
