# crab_flat.py - Lay the Crab-Bot completely flat on the ground
import smbus2
import time

# I2C Setup
BUS = smbus2.SMBus(1)
ADDR = 0x40

# --- Channel Mapping ---
L1, R1, L2, R2 = 0, 1, 2, 3
L3, R3, L4, R4 = 4, 5, 6, 7

# --- HARD LIMITS ---
LIMITS = { 4: (0, 180), 5: (0, 180), 6: (0, 180), 7: (0, 180) }

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
    min_a, max_a = LIMITS.get(channel, (0, 180))
    safe_angle = max(min_a, min(max_a, angle))
    pulse_us = 500 + (safe_angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)

try:
    set_freq(50)
    print("Laying Flat...")
    
    # 1. Center Shoulders
    set_angle(0, 45); set_angle(1, 135)
    set_angle(2, 135); set_angle(3, 45)
    time.sleep(0.5)

    # 2. Maximum Flex (Legs up, Body down)
    # Smoothly lower the body
    for i in range(50):
        set_angle(4, 45 + (i * 2.5))  # L3 45 -> 170
        set_angle(5, 135 - (i * 2.5)) # R3 135 -> 10
        set_angle(6, 135 - (i * 2.5)) # L4 135 -> 10
        set_angle(7, 45 + (i * 2.5))  # R4 45 -> 170
        time.sleep(0.02)

    print("Resting body on the ground.")
    time.sleep(1)
    
    # 3. Release torque
    for i in range(16):
        set_pwm(i, 0, 0)
    print("All motors released. Shutdown complete.")

except KeyboardInterrupt:
    for i in range(16): set_pwm(i, 0, 0)
