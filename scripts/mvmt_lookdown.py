# crab_lookdown.py - Tilt the Crab-Bot to look downwards
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- Channel Mapping ---


# --- HARD LIMITS ---


# Standing Home Position





try:
    BUS.write_byte_data(ADDR, 0x01, 0x04)
    BUS.write_byte_data(ADDR, 0x00, 0x01)
    time.sleep(0.005)
    set_freq(50)
    
    print("Moving all to Home...")
    for ch, val in HOME.items(): servo.set_angle(ch, val)
    time.sleep(1)

    print("Tilting Down (Look Down)...")
    for i in range(35):
        offset = i
        # Front legs flex (crouch)
        servo.set_angle(4, 45 + offset)  # servo.L3 flex
        servo.set_angle(5, 135 - offset) # servo.R3 flex
        # Hind legs stay at Home
        time.sleep(0.03)
    time.sleep(2)

    print("Returning to Home...")
    for ch, val in HOME.items(): servo.set_angle(ch, val)
    time.sleep(1)
    for ch in range(4, 8): set_pwm(ch, 0, 0)
except KeyboardInterrupt:
    for ch in range(4, 8): set_pwm(ch, 0, 0)
