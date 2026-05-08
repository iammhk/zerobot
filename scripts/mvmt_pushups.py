# crab_pushups.py - Front-Leg Only Pushups
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- HARD CHANNEL MAPPING ---
# Shoulders: 0=servo.L1, 1=servo.R1, 2=servo.L2, 3=servo.R2
# Knees:     4=servo.L3 (Front Left), 5=servo.R3 (Front Right)
#            6=servo.L4 (Hind Left), 7=servo.R4 (Hind Right)

ALL_CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7]

# --- HARD LIMITS ---


# Standing Home Position







try:
    print("Moving all legs to HOME (Standing)...")
    for ch, val in HOME.items():
        servo.set_angle(ch, val)
    time.sleep(1.5)

    print("Starting Front-Leg Pushups (Channels 4 & 5)...")
    for i in range(10):
        print(f"Rep {i+1} / 10")
        
        # PUSH UP (Lift body using Front Knees)
        servo.set_angle(4, 10)  # Front Left Knee
        servo.set_angle(5, 170) # Front Right Knee
        time.sleep(0.5)
        
        # PUSH DOWN
        servo.set_angle(4, 80)  # Return towards home
        servo.set_angle(5, 100) # Return towards home
        time.sleep(0.5)

    print("\nWorkout complete. Returning to Home.")
    for ch, val in HOME.items():
        servo.set_angle(ch, val)
    time.sleep(1)
    
    # Release all
    for ch in ALL_CHANNELS:
        set_pwm(ch, 0, 0)

except KeyboardInterrupt:
    for ch in ALL_CHANNELS:
        set_pwm(ch, 0, 0)
