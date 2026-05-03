# crab_backward.py - High-Impact Power Stomp Gait
import smbus2
import time

# I2C Setup
BUS = smbus2.SMBus(1)
ADDR = 0x40

# --- Channel Mapping ---
L1, R1, L2, R2 = 0, 1, 2, 3
L3, R3, L4, R4 = 4, 5, 6, 7

# --- HARD LIMITS ---
LIMITS = { 0: (0, 90), 1: (90, 180), 2: (90, 180), 3: (0, 90), 4: (0, 180), 5: (0, 180), 6: (0, 180), 7: (0, 180) }
HOME = { 0: 45, 1: 135, 2: 135, 3: 45, 4: 45, 5: 135, 6: 135, 7: 45 }

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

# Initialize
try:
    set_freq(50)
    for ch, val in HOME.items(): set_angle(ch, val)
    time.sleep(1.0)

    print("Executing Power Stomp Backward...")
    for _ in range(10):
        # 1. LIFT HIND
        print("Lifting Hind...")
        set_angle(6, 20)  # L4 lift
        set_angle(7, 160) # R4 lift
        time.sleep(0.15)
        
        # 2. REACH HIND
        set_angle(2, 175) # L2 backward
        set_angle(3, 5)   # R2 backward
        time.sleep(0.15)
        
        # 3. SLAM HIND (Impact!)
        print("SLAM!")
        set_angle(6, 170) # L4 stomp
        set_angle(7, 10)  # R4 stomp
        time.sleep(0.1)
        
        # 4. LIFT & MOVE FRONT
        print("Pushing...")
        set_angle(4, 160) # L3 lift
        set_angle(5, 20)  # R3 lift
        time.sleep(0.1)
        # Reset all shoulders to pull body backward
        for ch in [0, 1, 2, 3]: set_angle(ch, HOME[ch])
        time.sleep(0.15)
        set_angle(4, HOME[4])
        set_angle(5, HOME[5])
        time.sleep(0.15)

    for i in range(8): set_pwm(i, 0, 0)
except KeyboardInterrupt:
    for i in range(8): set_pwm(i, 0, 0)
