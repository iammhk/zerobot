# crab_lookup.py - Tilt the Crab-Bot to look upwards
import smbus2
import time

# I2C Setup
BUS = smbus2.SMBus(1)
ADDR = 0x40

# --- Channel Mapping ---
L1, R1, L2, R2 = 0, 1, 2, 3
L3, R3, L4, R4 = 4, 5, 6, 7

# --- HARD LIMITS ---
LIMITS = {
    0: (0, 90),   1: (90, 180),
    2: (90, 180), 3: (0, 90),
    4: (0, 180),  5: (0, 180),
    6: (0, 180),  7: (0, 180)
}

# Standing Home Position
HOME = {
    0: 45, 1: 135,
    2: 135, 3: 45,
    4: 45, 5: 135,
    6: 135, 7: 45
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
    print(f"Error: {e}")
    exit(1)

try:
    print("Standing up...")
    for ch, val in HOME.items(): set_angle(ch, val)
    time.sleep(1.0)

    print("Tilting UP (Pitching back)...")
    # Smooth transition for a dramatic tilt
    for i in range(40):
        # Front Left (4) goes 45 -> 5
        # Front Right (5) goes 135 -> 175
        # Hind Left (6) goes 135 -> 175
        # Hind Right (7) goes 45 -> 5
        
        offset = i  # 0 to 40 degrees of offset
        set_angle(4, 45 - offset)
        set_angle(5, 135 + offset)
        set_angle(6, 135 + offset)
        set_angle(7, 45 - offset)
        time.sleep(0.02)
    
    time.sleep(2.0) # Hold the tilt

    print("Returning to Home...")
    for ch, val in HOME.items(): set_angle(ch, val)
    time.sleep(1)
    
    for ch in range(8): set_pwm(ch, 0, 0)

except KeyboardInterrupt:
    for ch in range(8): set_pwm(ch, 0, 0)
