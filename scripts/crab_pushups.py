# crab_pushups.py - Dedicated workout for the Crab-Bot
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

ALL_SERVOS = [0, 1, 2, 3, 4, 5, 6, 7]

# --- HARD LIMITS ---
LIMITS = {
    L1: (0, 90),   R1: (90, 180),
    L2: (90, 180), R2: (0, 90),
    L3: (0, 180),  R3: (0, 180),
    L4: (0, 180),  R4: (0, 180)
}

# Standing Home Position
HOME = {
    L1: 45, R1: 135,
    L2: 135, R2: 45,
    L3: 45, R3: 135,
    L4: 135, R4: 45
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
    print("Preparing for front-leg pushups (10 reps)...")
    # Move all to HOME first
    for ch, val in HOME.items():
        set_angle(ch, val)
    time.sleep(1.5)

    for i in range(10):
        print(f"Rep {i+1} / 10")
        # PUSH UP (L3 and R3 move to lift front body)
        # Assuming lower angles lift the knee
        set_angle(L3, 10)
        set_angle(R3, 170)
        time.sleep(0.5)
        
        # PUSH DOWN (L3 and R3 return or go lower)
        set_angle(L3, 80)
        set_angle(R3, 100)
        time.sleep(0.5)

    print("\nWorkout complete. Returning to Home.")
    for ch, val in HOME.items():
        set_angle(ch, val)
    time.sleep(1)
    
    for ch in ALL_SERVOS:
        set_pwm(ch, 0, 0)

except KeyboardInterrupt:
    for ch in ALL_SERVOS:
        set_pwm(ch, 0, 0)

except KeyboardInterrupt:
    for ch in KNEES: set_pwm(ch, 0, 0)
