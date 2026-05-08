# mvmt_shrug.py - Shrugging movement sequence
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


def run():
    try:
        print("Shrugging...")
        servo.set_angle(servo.L3, 90); servo.set_angle(servo.R3, 90); servo.set_angle(servo.L4, 90); servo.set_angle(servo.R4, 90)
        time.sleep(1)
        servo.set_angle(servo.L3, 180); servo.set_angle(servo.L4, 0); servo.set_angle(servo.R3, 0); servo.set_angle(servo.R4, 180)
        time.sleep(1.5)
        for ch, val in HOME.items(): servo.set_angle(ch, val)
        time.sleep(1.0)
    finally:
        print("Releasing servos...")
        for i in range(8):
            servo.release(i)

if __name__ == "__main__":
    run()
