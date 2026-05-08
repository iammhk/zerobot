# crab_scuttle_left.py - Sideways movement for the Crab-Bot
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

    print("Scuttling Left...")
    for _ in range(8):
        # 1. Lift LEFT side legs (servo.L3, servo.L4)
        servo.set_angle(4, 160) # Lift servo.L3
        servo.set_angle(6, 20)  # Lift servo.L4
        time.sleep(servo.config.FRAME_DELAY * 1.5)
        
        # 2. Reach out with LEFT shoulders
        servo.set_angle(0, 5)   # servo.L1 reach forward
        servo.set_angle(2, 175) # servo.L2 reach backward
        time.sleep(servo.config.FRAME_DELAY * 1.5)
        
        # 3. Lower LEFT side
        servo.set_angle(4, servo.HOME[4])
        servo.set_angle(6, servo.HOME[6])
        time.sleep(servo.config.FRAME_DELAY * 1.5)
        
        # 4. Push body (Reset shoulders)
        servo.set_angle(0, servo.HOME[0])
        servo.set_angle(2, servo.HOME[2])
        time.sleep(servo.config.FRAME_DELAY * 3.0)

    print("Resting at Home.")
    for ch, val in HOME.items(): servo.set_angle(ch, val)
    time.sleep(servo.config.FRAME_DELAY * 10.0)
    for ch in range(8): set_pwm(ch, 0, 0)
except KeyboardInterrupt:
    for ch in range(8): set_pwm(ch, 0, 0)
