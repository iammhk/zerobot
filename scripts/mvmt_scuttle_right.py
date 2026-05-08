# crab_scuttle_right.py - Sideways movement for the Crab-Bot
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- Channel Mapping ---
# --- HARD LIMITS ---






try:
    BUS.write_byte_data(ADDR, 0x01, 0x04)
    BUS.write_byte_data(ADDR, 0x00, 0x01)
    time.sleep(servo.config.FRAME_DELAY * 0.0)
    set_freq(50)
    
    print("Moving to Home...")
    for ch, val in HOME.items(): servo.set_angle(ch, val)
    time.sleep(1.5)

    print("Scuttling Right...")
    for _ in range(8):
        # 1. Lift RIGHT side legs (servo.R3, servo.R4)
        servo.set_angle(5, 20)  # Lift servo.R3
        servo.set_angle(7, 160) # Lift servo.R4
        time.sleep(servo.config.FRAME_DELAY * 1.5)
        
        # 2. Reach out with RIGHT shoulders
        servo.set_angle(1, 175) # servo.R1 reach forward
        servo.set_angle(3, 5)   # servo.R2 reach backward
        time.sleep(servo.config.FRAME_DELAY * 1.5)
        
        # 3. Lower RIGHT side
        servo.set_angle(5, servo.HOME[5])
        servo.set_angle(7, servo.HOME[7])
        time.sleep(servo.config.FRAME_DELAY * 1.5)
        
        # 4. Push body (Reset shoulders)
        servo.set_angle(1, servo.HOME[1])
        servo.set_angle(3, servo.HOME[3])
        time.sleep(servo.config.FRAME_DELAY * 3.0)

    print("Resting at Home.")
    for ch, val in HOME.items(): servo.set_angle(ch, val)
    time.sleep(servo.config.FRAME_DELAY * 10.0)
    for ch in range(8): set_pwm(ch, 0, 0)
except KeyboardInterrupt:
    for ch in range(8): set_pwm(ch, 0, 0)
