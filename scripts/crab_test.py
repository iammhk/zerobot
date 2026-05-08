# crab_test.py - Hardware verification for the 8-servo Crab-Bot
# This script tests each joint (Shoulders servo.L1-servo.R2, Knees servo.L3-servo.R4) one by one.

import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup (Waveshare HAT default)
# --- Channel Mapping ---
servo.L1 = 0 
servo.L2 = 1 
servo.L3 = 5 
servo.L4 = 4 
servo.R1 = 3 
servo.R2 = 2 
servo.R3 = 7 
servo.R4 = 6 

ALL_SERVOS = [servo.L1, servo.R1, servo.L2, servo.R2, servo.L3, servo.R3, servo.L4, servo.R4]
NAMES = {servo.L1: "servo.L1", servo.R1: "servo.R1", servo.L2: "servo.L2", servo.R2: "servo.R2", servo.L3: "servo.L3", servo.R3: "servo.R3", servo.L4: "servo.L4", servo.R4: "servo.R4"}

# --- HARD LIMITS (Safe Ranges) ---







try:
    print("Moving all joints to safe mid-points...")
    for ch in ALL_SERVOS:
        min_a, max_a = servo.config.LIMITS[ch]
        servo.set_angle(ch, (min_a + max_a) / 2)
    time.sleep(1)

    # Test each joint with a small nudge within its safe range
    for ch in ALL_SERVOS:
        min_a, max_a = servo.config.LIMITS[ch]
        mid = (min_a + max_a) / 2
        print(f"Testing {NAMES[ch]} (Range {min_a}-{max_a}°, Center {mid}°)...")
        
        servo.set_angle(ch, mid + 10)
        time.sleep(0.4)
        servo.set_angle(ch, mid - 10)
        time.sleep(0.4)
        servo.set_angle(ch, mid)
        time.sleep(0.2)

    print("Safety Test Complete.")
except KeyboardInterrupt:
    print("\nAborting...")
finally:
    print("Releasing all servos.")
    for ch in ALL_SERVOS:
        set_pwm(ch, 0, 0)
