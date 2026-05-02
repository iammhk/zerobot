# crab_forward.py - Steady Crawl with CoG Compensation
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

def move_body(x_offset, y_offset):
    # x_offset: + forward, y_offset: + right
    set_angle(0, HOME[0] - x_offset - y_offset)
    set_angle(1, HOME[1] + x_offset - y_offset)
    set_angle(2, HOME[2] + x_offset + y_offset)
    set_angle(3, HOME[3] - x_offset + y_offset)

def balanced_step(s_ch, k_ch, swing_dir):
    # 1. Shift body away from the leg being lifted
    # (e.g. if lifting FL, shift body back and right)
    if s_ch == 0: move_body(-15, 15)  # FL
    elif s_ch == 1: move_body(-15, -15) # FR
    elif s_ch == 2: move_body(15, 15)  # HL
    elif s_ch == 3: move_body(15, -15) # HR
    time.sleep(0.2)
    
    # 2. Lift
    lift = 25
    cur_k = HOME[k_ch]
    set_angle(k_ch, cur_k + (lift if k_ch in [4, 7] else -lift))
    time.sleep(0.1)
    
    # 3. Swing Shoulder
    swing = 20 * swing_dir
    if s_ch in [0, 3]: set_angle(s_ch, HOME[s_ch] - swing)
    else: set_angle(s_ch, HOME[s_ch] + swing)
    time.sleep(0.1)
    
    # 4. Lower
    set_angle(k_ch, cur_k)
    time.sleep(0.1)

# Initialize
try:
    set_freq(50)
    for ch, val in HOME.items(): set_angle(ch, val)
    time.sleep(1.0)

    print("Steady Forward Walk with CoG Balancing...")
    for _ in range(8):
        balanced_step(0, 4, 1) # FL
        balanced_step(1, 5, 1) # FR
        balanced_step(2, 6, 1) # HL
        balanced_step(3, 7, 1) # HR
        
        # PULL body forward
        move_body(0, 0)
        time.sleep(0.3)

    for i in range(8): set_pwm(i, 0, 0)
except KeyboardInterrupt:
    for i in range(8): set_pwm(i, 0, 0)
