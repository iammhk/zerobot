# mvmt_sesame_turn.py - Turn logic from Sesame Robot
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

import sys
import argparse

def run(direction=1, cycles=2):
    try:
        for _ in range(cycles):
            if direction > 0: # Left
                servo.set_angle(servo.R3, 135); servo.set_angle(servo.L4, 135); time.sleep(0.1)
                servo.set_angle(servo.R1, 180); servo.set_angle(servo.L2, 180); time.sleep(0.1)
                servo.set_angle(servo.R3, 180); servo.set_angle(servo.L4, 180); time.sleep(0.1)
                servo.set_angle(servo.R1, 135); servo.set_angle(servo.L2, 135); time.sleep(0.1)
            else: # Right
                servo.set_angle(servo.R4, 45); servo.set_angle(servo.L3, 45); time.sleep(0.1)
                servo.set_angle(servo.R2, 0); servo.set_angle(servo.L1, 0); time.sleep(0.1)
                servo.set_angle(servo.R4, 0); servo.set_angle(servo.L3, 0); time.sleep(0.1)
                servo.set_angle(servo.R2, 45); servo.set_angle(servo.L1, 45); time.sleep(0.1)
        
        for ch, val in HOME.items(): servo.set_angle(ch, val)
        time.sleep(0.2)
    finally:
        for i in range(8):
            servo.release(i)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=int, default=1)
    parser.add_argument("--cycles", type=int, default=2)
    args = parser.parse_args()
    run(args.dir, args.cycles)
