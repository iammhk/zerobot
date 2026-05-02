# crab_test.py - Hardware verification for the 8-servo Crab-Bot
# This script tests each joint (Shoulders L1-R2, Knees L3-R4) one by one.

import smbus2
import time

# I2C Setup (Waveshare HAT default)
BUS = smbus2.SMBus(1)
ADDR = 0x40

# --- Channel Mapping ---
L1 = 0 # Front Left Shoulder
R1 = 1 # Front Right Shoulder
L2 = 2 # Hind Left Shoulder
R2 = 3 # Hind Right Shoulder
L3 = 4 # Front Left Joint (Knee)
R3 = 5 # Front Right Joint (Knee)
L4 = 6 # Hind Left Joint (Knee)
R4 = 7 # Hind Right Joint (Knee)

ALL_SERVOS = [L1, R1, L2, R2, L3, R3, L4, R4]
NAMES = {0: "L1", 1: "R1", 2: "L2", 3: "R2", 4: "L3", 5: "R3", 6: "L4", 7: "R4"}

def set_pwm(channel, on, off):
    BUS.write_byte_data(ADDR, 0x06 + 4*channel, on & 0xFF)
    BUS.write_byte_data(ADDR, 0x07 + 4*channel, on >> 8)
    BUS.write_byte_data(ADDR, 0x08 + 4*channel, off & 0xFF)
    BUS.write_byte_data(ADDR, 0x09 + 4*channel, off >> 8)

def set_freq(freq):
    prescale = int(25000000.0 / 4096.0 / freq - 1.0)
    old_mode = BUS.read_byte_data(ADDR, 0x00)
    BUS.write_byte_data(ADDR, 0x00, (old_mode & 0x7F) | 0x10)
    BUS.write_byte_data(ADDR, 0xFE, prescale)
    BUS.write_byte_data(ADDR, 0x00, old_mode)
    time.sleep(0.005)
    BUS.write_byte_data(ADDR, 0x00, old_mode | 0x80)

def set_angle(channel, angle):
    pulse_us = 500 + (angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)

# Initialize
try:
    BUS.write_byte_data(ADDR, 0x01, 0x04)
    BUS.write_byte_data(ADDR, 0x00, 0x01)
    time.sleep(0.005)
    set_freq(50)
except Exception as e:
    print(f"Error: Could not initialize I2C. Is the HAT connected? {e}")
    exit(1)

try:
    print("Centering all joints (90°)...")
    for ch in ALL_SERVOS:
        set_angle(ch, 90)
    time.sleep(1)

    # Test Shoulders (L1, R1, L2, R2)
    for ch in [L1, R1, L2, R2]:
        print(f"Testing Shoulder {NAMES[ch]} (Ch {ch})...")
        set_angle(ch, 100)
        time.sleep(0.5)
        set_angle(ch, 90)
        time.sleep(0.5)

    # Test Joints/Knees (L3, R3, L4, R4)
    for ch in [L3, R3, L4, R4]:
        print(f"Testing Knee {NAMES[ch]} (Ch {ch})...")
        set_angle(ch, 100)
        time.sleep(0.5)
        set_angle(ch, 90)
        time.sleep(0.5)

    print("Test Complete.")
except KeyboardInterrupt:
    print("\nAborting... Releasing all servos.")
    for ch in ALL_SERVOS:
        set_pwm(ch, 0, 0)
