# crab_flat.py - Lay the Crab-Bot completely flat on the ground
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- Channel Mapping ---
# --- HARD LIMITS ---





try:
    set_freq(50)
    print("Laying Flat...")
    
    # 1. Center Shoulders
    servo.set_angle(0, 45); servo.set_angle(1, 135)
    servo.set_angle(2, 135); servo.set_angle(3, 45)
    time.sleep(0.5)

    # 2. Maximum Flex (Legs up, Body down)
    # Smoothly lower the body
    for i in range(50):
        servo.set_angle(4, 45 + (i * 2.5))  # servo.L3 45 -> 170
        servo.set_angle(5, 135 - (i * 2.5)) # servo.R3 135 -> 10
        servo.set_angle(6, 135 - (i * 2.5)) # servo.L4 135 -> 10
        servo.set_angle(7, 45 + (i * 2.5))  # servo.R4 45 -> 170
        time.sleep(0.02)

    print("Resting body on the ground.")
    time.sleep(1)
    
    # 3. Release torque
    for i in range(16):
        servo.release(i)
    print("All motors released. Shutdown complete.")

except KeyboardInterrupt:
    for i in range(16): servo.release(i)
