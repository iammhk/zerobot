# crab_pushups.py - Front-Leg Only Pushups
import smbus2
import time

# I2C Setup
BUS = smbus2.SMBus(1)
ADDR = 0x40

# --- HARD CHANNEL MAPPING ---
# Shoulders: 0=L1, 1=R1, 2=L2, 3=R2
# Knees:     4=L3 (Front Left), 5=R3 (Front Right)
#            6=L4 (Hind Left), 7=R4 (Hind Right)

ALL_CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7]

# --- HARD LIMITS ---
LIMITS = {
    0: (0, 90),   1: (90, 180), # L1, R1
    2: (90, 180), 3: (0, 90),   # L2, R2
    4: (0, 180),  5: (0, 180),  # L3, R3 (Front Knees)
    6: (0, 180),  7: (0, 180)   # L4, R4 (Hind Knees)
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
    print("Moving all legs to HOME (Standing)...")
    for ch, val in HOME.items():
        set_angle(ch, val)
    time.sleep(1.5)

    print("Starting Front-Leg Pushups (Channels 4 & 5)...")
    for i in range(10):
        print(f"Rep {i+1} / 10")
        
        # PUSH UP (Lift body using Front Knees)
        set_angle(4, 10)  # Front Left Knee
        set_angle(5, 170) # Front Right Knee
        time.sleep(0.5)
        
        # PUSH DOWN
        set_angle(4, 80)  # Return towards home
        set_angle(5, 100) # Return towards home
        time.sleep(0.5)

    print("\nWorkout complete. Returning to Home.")
    for ch, val in HOME.items():
        set_angle(ch, val)
    time.sleep(1)
    
    # Release all
    for ch in ALL_CHANNELS:
        set_pwm(ch, 0, 0)

except KeyboardInterrupt:
    for ch in ALL_CHANNELS:
        set_pwm(ch, 0, 0)
