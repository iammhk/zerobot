# crab_backward.py - Reverse Crawl for Crab-Bot
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

# Neutral Home Position
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

def step_leg(s_ch, k_ch, swing_dir):
    mid_k = HOME[k_ch]
    lift_val = 40 if k_ch in [4, 7] else -40
    set_angle(k_ch, mid_k + lift_val)
    time.sleep(0.12)
    mid_s = HOME[s_ch]
    offset = 30
    if s_ch in [0, 3]: set_angle(s_ch, mid_s - (offset * swing_dir))
    else: set_angle(s_ch, mid_s + (offset * swing_dir))
    time.sleep(0.12)
    set_angle(k_ch, mid_k)
    time.sleep(0.12)

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
    print("Moving to Home...")
    for ch, val in HOME.items(): set_angle(ch, val)
    time.sleep(1.5)

    print("Walking Backward...")
    for _ in range(8):
        # Sequence: HL -> FR -> HR -> FL (Moving backward)
        step_leg(L2, L4, -1)
        step_leg(R1, R3, -1)
        step_leg(R2, R4, -1)
        step_leg(L1, L3, -1)
        
        print("Pushing...")
        for ch in [0, 1, 2, 3]: set_angle(ch, HOME[ch])
        time.sleep(0.4)

    print("Resting at Home.")
    for ch, val in HOME.items(): set_angle(ch, val)
    time.sleep(1)
    for ch in range(8): set_pwm(ch, 0, 0)
except KeyboardInterrupt:
    for ch in range(8): set_pwm(ch, 0, 0)
