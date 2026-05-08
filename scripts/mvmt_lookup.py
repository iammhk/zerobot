# crab_lookup.py - Curious tilt-up movement for the Crab-Bot
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- Channel Mapping ---
# --- HARD LIMITS ---


# Standing Home Position







try:
    print("Standing up...")
    for ch, val in HOME.items(): servo.set_angle(ch, val)
    time.sleep(servo.config.FRAME_DELAY * 10.0)

    print("Curious Tilt (Look Up)...")
    # Pivot around the back legs.
    # Front legs extend to tilt the body up.
    # Hind legs stay at HOME to act as the pivot point.
    for i in range(35):
        offset = i
        servo.set_angle(4, 45 - offset)  # servo.L3 Front Left extend
        servo.set_angle(5, 135 + offset) # servo.R3 Front Right extend
        time.sleep(servo.config.FRAME_DELAY * 0.3)
    
    time.sleep(2.5)

    print("Returning to Home...")
    for ch, val in HOME.items(): servo.set_angle(ch, val)
    time.sleep(servo.config.FRAME_DELAY * 10.0)
    
    for ch in range(8): set_pwm(ch, 0, 0)

except KeyboardInterrupt:
    for ch in range(8): set_pwm(ch, 0, 0)
