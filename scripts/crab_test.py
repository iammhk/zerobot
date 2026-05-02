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

# --- HARD LIMITS (Safe Ranges) ---
LIMITS = {
    L1: (0, 90),
    R1: (90, 180),
    L2: (90, 180),
    R2: (0, 90),
    L3: (0, 90),
    R3: (90, 180),
    L4: (90, 180),
    R4: (0, 90)
}

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
    """Set angle with Hard Limit clipping."""
    min_a, max_a = LIMITS.get(channel, (0, 180))
    safe_angle = max(min_a, min(max_a, angle))
    
    pulse_us = 500 + (safe_angle / 180.0) * 2000
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
    print("Moving all joints to safe mid-points...")
    for ch in ALL_SERVOS:
        min_a, max_a = LIMITS[ch]
        set_angle(ch, (min_a + max_a) / 2)
    time.sleep(1)

    # Test each joint with a small nudge within its safe range
    for ch in ALL_SERVOS:
        min_a, max_a = LIMITS[ch]
        mid = (min_a + max_a) / 2
        print(f"Testing {NAMES[ch]} (Range {min_a}-{max_a}°, Center {mid}°)...")
        
        set_angle(ch, mid + 10)
        time.sleep(0.4)
        set_angle(ch, mid - 10)
        time.sleep(0.4)
        set_angle(ch, mid)
        time.sleep(0.2)

    print("Safety Test Complete.")
except KeyboardInterrupt:
    print("\nAborting... Releasing all servos.")
    for ch in ALL_SERVOS:
        set_pwm(ch, 0, 0)
