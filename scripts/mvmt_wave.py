# crab_wave.py - Friendly greeting movement for the Crab-Bot
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- Channel Mapping ---
servo.L1 = 0 # Front Left Shoulder
servo.L3 = 4 # Front Left Knee

ALL_SERVOS = [0, 1, 2, 3, 4, 5, 6, 7]

# --- HARD LIMITS ---


# Standing Home Position







try:
    print("Standing up...")
    for ch, val in HOME.items(): servo.set_angle(ch, val)
    time.sleep(1.5)

    print("Shifting body mass back and right for maximum stability...")
    # 1. Shift shoulders to move body frame AWAY from the Front Left leg
    servo.set_angle(0, 90)  # servo.L1 (Front Left) Move back
    servo.set_angle(1, 90)  # servo.R1 (Front Right) Move back
    servo.set_angle(2, 90)  # servo.L2 (Hind Left) Move forward
    servo.set_angle(3, 90)  # servo.R2 (Hind Right) Move forward
    
    # 2. Brace remaining knees (crouch slightly to lower Center of Gravity)
    servo.set_angle(5, 120) # servo.R3 (Front Right)
    servo.set_angle(6, 100) # servo.L4 (Hind Left)
    servo.set_angle(7, 80)  # servo.R4 (Hind Right)
    time.sleep(1.0)

    print("Waving hello! (Lifting Front Left Leg)...")
    # 3. Lift Knee (servo.L3) high into the air
    servo.set_angle(4, 170)
    time.sleep(0.5)
    
    # 3. Wave Shoulder (servo.L1) back and forth
    for i in range(5):
        print(f"Wave {i+1}")
        servo.set_angle(0, 10)
        time.sleep(0.2)
        servo.set_angle(0, 80)
        time.sleep(0.2)

    print("\nReturning to Home.")
    for ch, val in HOME.items():
        servo.set_angle(ch, val)
    time.sleep(1)
    
    # Release
    for ch in ALL_SERVOS: set_pwm(ch, 0, 0)

except KeyboardInterrupt:
    for ch in ALL_SERVOS: set_pwm(ch, 0, 0)
