# crab_pushups.py - Dedicated workout for the Crab-Bot
import smbus2
import time

# I2C Setup
BUS = smbus2.SMBus(1)
ADDR = 0x40

# --- Channel Mapping (Knees only for push-ups) ---
L3, R3 = 4, 5 
L4, R4 = 6, 7 
KNEES = [L3, R3, L4, R4]

# --- HARD LIMITS ---
LIMITS = {
    L3: (0, 180), R3: (0, 180),
    L4: (0, 180), R4: (0, 180)
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
    print("Preparing for workout (10 reps)...")
    for ch in KNEES: set_angle(ch, 90)
    time.sleep(1.5)

    for i in range(10):
        print(f"Rep {i+1} / 10")
        # Go Low
        for ch in KNEES: set_angle(ch, 20)
        time.sleep(0.5)
        # Go High
        for ch in KNEES: set_angle(ch, 130)
        time.sleep(0.5)

    print("\nWorkout complete. Resting at 90°.")
    for ch in KNEES: set_angle(ch, 90)
    time.sleep(1)
    
    for ch in KNEES: set_pwm(ch, 0, 0)

except KeyboardInterrupt:
    for ch in KNEES: set_pwm(ch, 0, 0)
