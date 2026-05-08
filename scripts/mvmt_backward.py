# crab_backward.py - High-Impact Power Stomp Gait
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- Channel Mapping ---
# --- HARD LIMITS ---






# Initialize
try:
    set_freq(50)
    for ch, val in HOME.items(): servo.set_angle(ch, val)
    time.sleep(1.0)

    print("Executing Power Stomp Backward...")
    for _ in range(10):
        # 1. LIFT HIND
        print("Lifting Hind...")
        servo.set_angle(6, 20)  # servo.L4 lift
        servo.set_angle(7, 160) # servo.R4 lift
        time.sleep(0.15)
        
        # 2. REACH HIND
        servo.set_angle(2, 175) # servo.L2 backward
        servo.set_angle(3, 5)   # servo.R2 backward
        time.sleep(0.15)
        
        # 3. SLAM HIND (Impact!)
        print("SLAM!")
        servo.set_angle(6, 170) # servo.L4 stomp
        servo.set_angle(7, 10)  # servo.R4 stomp
        time.sleep(0.1)
        
        # 4. LIFT & MOVE FRONT
        print("Pushing...")
        servo.set_angle(4, 160) # servo.L3 lift
        servo.set_angle(5, 20)  # servo.R3 lift
        time.sleep(0.1)
        # Reset all shoulders to pull body backward
        for ch in [0, 1, 2, 3]: servo.set_angle(ch, servo.HOME[ch])
        time.sleep(0.15)
        servo.set_angle(4, servo.HOME[4])
        servo.set_angle(5, servo.HOME[5])
        time.sleep(0.15)

    for i in range(8): servo.release(i)
except KeyboardInterrupt:
    for i in range(8): servo.release(i)
