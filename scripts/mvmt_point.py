# mvmt_point.py - Pointing movement sequence
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


def run():
    try:
        print("Pointing...")
        servo.set_angle(servo.L2, 180); servo.set_angle(servo.R1, 135); servo.set_angle(servo.R2, 45); servo.set_angle(servo.L4, 180)
        servo.set_angle(servo.L1, 0); servo.set_angle(servo.L3, 180); servo.set_angle(servo.R4, 0); servo.set_angle(servo.R3, 180)
        time.sleep(2.0)
        for ch, val in HOME.items(): servo.set_angle(ch, val)
        time.sleep(1.0)
    finally:
        print("Releasing servos...")
        for i in range(8):
            servo.release(i)

if __name__ == "__main__":
    run()
