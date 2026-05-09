# crab_lookup.py - Tilt the Crab-Bot to look upwards
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
    servo.move_to_home()
    time.sleep(servo.config.FRAME_DELAY * 10.0)

    print("Tilting UP (Pitching back)...")
    # Smooth transition for a dramatic tilt
    for i in range(40):
        # Front Left (4) goes 45 -> 5
        # Front Right (5) goes 135 -> 175
        # Hind Left (6) goes 135 -> 175
        # Hind Right (7) goes 45 -> 5
        
        offset = i  # 0 to 40 degrees of offset
        servo.set_angle(4, 45 - offset)
        servo.set_angle(5, 135 + offset)
        servo.set_angle(6, 135 + offset)
        servo.set_angle(7, 45 - offset)
        time.sleep(servo.config.FRAME_DELAY * 0.2)
    
    time.sleep(2.0) # Hold the tilt

    print("Returning to Home...")
    servo.move_to_home()
    time.sleep(servo.config.FRAME_DELAY * 10.0)
    
    for ch in range(8): set_pwm(ch, 0, 0)

except KeyboardInterrupt:
    for ch in range(8): set_pwm(ch, 0, 0)
