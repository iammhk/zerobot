# crab_walk.py - Basic Creep Gait for 8-servo Crab-Bot
import smbus2
import time

# I2C Setup
BUS = smbus2.SMBus(1)
ADDR = 0x40

# --- Channel Mapping ---
L1, R1 = 0, 1 # Shoulders (Front)
L2, R2 = 2, 3 # Shoulders (Hind)
L3, R3 = 4, 5 # Knees (Front)
L4, R4 = 6, 7 # Knees (Hind)

# --- HARD LIMITS (Mirroring your mechanical constraints) ---
LIMITS = {
    L1: (0, 90),   R1: (90, 180),
    L2: (90, 180), R2: (0, 90),
    L3: (0, 180),  R3: (0, 180),
    L4: (0, 180),  R4: (0, 180)
}

def get_mid(ch):
    return (LIMITS[ch][0] + LIMITS[ch][1]) / 2

# Home position (Standing)
HOME = {ch: get_mid(ch) for ch in range(8)}

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

def leg_step(shoulder, knee, swing_offset=30, lift_offset=30):
    """Lift -> Swing -> Lower"""
    mid_s = HOME[shoulder]
    mid_k = HOME[knee]
    
    # 1. Lift Knee
    # If 0 is up for this knee, subtract. If 180 is up, add.
    # Based on your limits, L3/R4 have 0:90 (0 is likely up), R3/L4 have 90:180 (180 is likely up)
    if shoulder in [L1, R2]: # L3 and R4
        set_angle(knee, mid_k - lift_offset)
    else: # R3 and L4
        set_angle(knee, mid_k + lift_offset)
    time.sleep(0.15)
    
    # 2. Swing Shoulder
    # L1 (0:90), R1 (90:180), L2 (90:180), R2 (0:90)
    if shoulder in [L1, R2]:
        set_angle(shoulder, mid_s - swing_offset)
    else:
        set_angle(shoulder, mid_s + swing_offset)
    time.sleep(0.15)
    
    # 3. Lower Knee
    set_angle(knee, mid_k)
    time.sleep(0.15)

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
    for ch, angle in HOME.items():
        set_angle(ch, angle)
    time.sleep(2)

    # Run for exactly 6 cycles
    for cycle in range(6):
        print(f"--- Cycle {cycle + 1} / 6 ---")
        # Step sequence: Front Left -> Hind Right -> Front Right -> Hind Left
        leg_step(L1, L3)
        leg_step(R2, R4)
        leg_step(R1, R3)
        leg_step(L2, L4)
        
        # Shift body forward (Reset all shoulders while feet are down)
        print("Shifting body...")
        for ch in [L1, R1, L2, R2]:
            set_angle(ch, HOME[ch])
        time.sleep(0.4)

    print("\nWalk complete. Returning to resting position (90 degrees)...")
    for ch in range(8):
        set_angle(ch, 90)  # Clipped by safety limits (will stay at 90)
    time.sleep(1)
    
    print("Releasing all servos.")
    for i in range(8):
        set_pwm(i, 0, 0)

except KeyboardInterrupt:
    print("\nStopping... Releasing servos.")
    for i in range(8):
        set_pwm(i, 0, 0)
