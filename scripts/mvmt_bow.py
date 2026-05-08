# mvmt_bow.py - Bowing movement sequence
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


def run():
    try:
        print("Bowing...")
        servo.set_angle(servo.L1, 0); servo.set_angle(servo.R1, 180)
        servo.set_angle(servo.L3, 10); servo.set_angle(servo.R3, 170)
        servo.set_angle(servo.L2, 180); servo.set_angle(servo.R2, 0)
        servo.set_angle(servo.L4, 180); servo.set_angle(servo.R4, 0)
        time.sleep(1)
        servo.set_angle(servo.L3, 90); servo.set_angle(servo.R3, 90)
        time.sleep(2)
        # Return to home (approximate)
        for ch, val in {0:45, 1:135, 2:135, 3:45, 4:45, 5:135, 6:135, 7:45}.items():
            servo.set_angle(ch, val)
        time.sleep(1.0)
    finally:
        print("Releasing servos...")
        for i in range(8):
            servo.release(i)

if __name__ == "__main__":
    run()
