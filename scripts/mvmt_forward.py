# crab_forward.py - High-Impact Power Stomp Gait
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

    print("Executing Power Stomp Forward...")
    for _ in range(10):
        # 1. LIFT FRONT
        print("Lifting Front...")
        servo.set_angle(4, 160) # servo.L3 lift
        servo.set_angle(5, 20)  # servo.R3 lift
        time.sleep(0.15)
        
        # 2. REACH FRONT
        servo.set_angle(0, 5)   # servo.L1 forward
        servo.set_angle(1, 175) # servo.R1 forward
        time.sleep(0.15)
        
        # 3. SLAM FRONT (Impact!)
        print("SLAM!")
        servo.set_angle(4, 10)  # servo.L3 stomp
        servo.set_angle(5, 170) # servo.R3 stomp
        time.sleep(0.1)
        
        # 4. LIFT & MOVE HIND
        print("Pushing...")
        servo.set_angle(6, 20)  # servo.L4 lift
        servo.set_angle(7, 160) # servo.R4 lift
        time.sleep(0.1)
        # Reset all shoulders to pull body
        for ch in [0, 1, 2, 3]: servo.set_angle(ch, servo.HOME[ch])
        time.sleep(0.15)
        servo.set_angle(6, servo.HOME[6])
        servo.set_angle(7, servo.HOME[7])
        time.sleep(0.15)

    for i in range(8): servo.release(i)
except KeyboardInterrupt:
    for i in range(8): servo.release(i)
