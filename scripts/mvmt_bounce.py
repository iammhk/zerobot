# mvmt_bounce.py - Bouncy dance movement
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


def run():
    try:
        print("Bouncing...")
        for _ in range(5):
            servo.set_angle(servo.L3, 10); servo.set_angle(servo.L4, 10); servo.set_angle(servo.R3, 170); servo.set_angle(servo.R4, 170)
            time.sleep(0.3)
            servo.set_angle(servo.L3, 65); servo.set_angle(servo.L4, 65); servo.set_angle(servo.R3, 115); servo.set_angle(servo.R4, 115)
            time.sleep(0.3)
        for ch, val in HOME.items(): servo.set_angle(ch, val)
        time.sleep(1.0)
    finally:
        print("Releasing servos...")
        for i in range(8):
            servo.release(i)

if __name__ == "__main__":
    run()
