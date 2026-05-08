# crab_stomp.py - Stomping movement for the Crab-Bot
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- Channel Mapping ---
servo.L3, servo.R3 = 4, 5 # Front Knees

# Standing Home Position





try:
    set_freq(50)
    print("Standing up...")
    servo.set_angle(4, 45); servo.set_angle(5, 135)
    time.sleep(1)

    print("Stomping!")
    for _ in range(5):
        # Stomp Left
        servo.set_angle(4, 160); time.sleep(0.15) # Lift
        servo.set_angle(4, 10); time.sleep(0.1)  # Slam
        servo.set_angle(4, 45); time.sleep(0.1)  # Reset
        
        # Stomp Right
        servo.set_angle(5, 20); time.sleep(0.15)  # Lift
        servo.set_angle(5, 170); time.sleep(0.1) # Slam
        servo.set_angle(5, 135); time.sleep(0.1) # Reset

    time.sleep(0.5)
    for i in range(8): servo.release(i)

except KeyboardInterrupt:
    for i in range(8): servo.release(i)
