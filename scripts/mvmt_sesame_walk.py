# mvmt_sesame_walk.py - Ripple gait from Sesame Robot
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

import sys
import argparse

def run(direction=1, cycles=1):
    try:
        def sa(ch, ang):
            if ch in [servo.L1, servo.R1, servo.L2, servo.R2]:
                home_val = servo.HOME[ch]
                servo.set_angle(ch, home_val + (ang - home_val) * direction)
            else:
                servo.set_angle(ch, ang)

        for _ in range(cycles):
            # Initial Step
            sa(servo.R3, 135); sa(servo.L3, 45)
            sa(servo.R2, 100); sa(servo.L1, 25)
            time.sleep(0.1)

            # Core Loop (1 cycle)
            sa(servo.R3, 135); sa(servo.L3, 0); time.sleep(0.1)
            sa(servo.L4, 135); sa(servo.L2, 90); sa(servo.R4, 0); sa(servo.R1, 180); time.sleep(0.1)
            sa(servo.R2, 45); sa(servo.L1, 90); time.sleep(0.1)
            sa(servo.R4, 45); sa(servo.L4, 180); time.sleep(0.1)
            sa(servo.R3, 180); sa(servo.L3, 45); sa(servo.R2, 90); sa(servo.L1, 0); time.sleep(0.1)
            sa(servo.L2, 135); sa(servo.R1, 90); time.sleep(0.1)
            
        # Optional: Return home or stay? Remote usually calls multiple times.
        # But standalone script should probably return home.
        for ch, val in HOME.items(): servo.set_angle(ch, val)
        time.sleep(0.2)
    finally:
        # Release if standalone, but remote might not want release between steps.
        # However, user asked for release in previous turn.
        for i in range(8):
            servo.release(i)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=int, default=1)
    parser.add_argument("--cycles", type=int, default=1)
    args = parser.parse_args()
    run(args.dir, args.cycles)
