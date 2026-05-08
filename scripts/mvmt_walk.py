# crab_walk.py - Basic Creep Gait for 8-servo Crab-Bot
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- Channel Mapping ---

# --- HARD LIMITS (Mirroring your mechanical constraints) ---


def get_mid(ch):
    return (servo.config.LIMITS[ch][0] + servo.config.LIMITS[ch][1]) / 2

# Home position (Standing) - Restoring previous "sweet spots"





def leg_step(shoulder, knee, swing_offset=30, lift_offset=30):
    """Lift -> Swing -> Lower"""
    mid_s = servo.HOME[shoulder]
    mid_k = servo.HOME[knee]
    
    # 1. Lift Knee
    # If 0 is up for this knee, subtract. If 180 is up, add.
    # Based on your limits, servo.L3/servo.R4 have 0:90 (0 is likely up), servo.R3/servo.L4 have 90:180 (180 is likely up)
    if shoulder in [servo.L1, servo.R2]: # servo.L3 and servo.R4
        servo.set_angle(knee, mid_k - lift_offset)
    else: # servo.R3 and servo.L4
        servo.set_angle(knee, mid_k + lift_offset)
    time.sleep(0.15)
    
    # 2. Swing Shoulder
    # servo.L1 (0:90), servo.R1 (90:180), servo.L2 (90:180), servo.R2 (0:90)
    if shoulder in [servo.L1, servo.R2]:
        servo.set_angle(shoulder, mid_s - swing_offset)
    else:
        servo.set_angle(shoulder, mid_s + swing_offset)
    time.sleep(0.15)
    
    # 3. Lower Knee
    servo.set_angle(knee, mid_k)
    time.sleep(0.15)



try:
    print("Standing up...")
    for ch, angle in HOME.items():
        servo.set_angle(ch, angle)
    time.sleep(2)

    # Run for exactly 6 cycles
    for cycle in range(6):
        print(f"--- Cycle {cycle + 1} / 6 ---")
        # Step sequence: Front Left -> Hind Right -> Front Right -> Hind Left
        leg_step(servo.L1, servo.L3)
        leg_step(servo.R2, servo.R4)
        leg_step(servo.R1, servo.R3)
        leg_step(servo.L2, servo.L4)
        
        # Shift body forward (Reset all shoulders while feet are down)
        print("Shifting body...")
        for ch in [servo.L1, servo.R1, servo.L2, servo.R2]:
            servo.set_angle(ch, servo.HOME[ch])
        time.sleep(0.4)

    print("\nWalk complete. Returning to resting position (90 degrees)...")
    for ch in range(8):
        servo.set_angle(ch, 90)  # Clipped by safety limits (will stay at 90)
    time.sleep(1)
    
    print("Releasing all servos.")
    for i in range(8):
        servo.release(i)

except KeyboardInterrupt:
    print("\nStopping... Releasing servos.")
    for i in range(8):
        servo.release(i)
