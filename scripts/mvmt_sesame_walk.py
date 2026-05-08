# mvmt_sesame_walk.py - Gait logic matched from official firmware
import time
import sys, os
import argparse

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run(direction=1, cycles=1):
    try:
        # Initial positions
        servo.move_to_home()
        time.sleep(0.2)
        
        # Initial Step
        servo.set_angle(servo.R3, 135); servo.set_angle(servo.L3, 45)
        if direction == 1:
            servo.set_angle(servo.R2, 100); servo.set_angle(servo.L1, 25)
        else:
            servo.set_angle(servo.R2, 90); servo.set_angle(servo.L1, 0)
        time.sleep(0.2)

        for _ in range(cycles):
            if direction == 1:
                # WALK FORWARD
                servo.set_angle(servo.R3, 135); servo.set_angle(servo.L3, 0); time.sleep(0.2)
                servo.set_angle(servo.L4, 135); servo.set_angle(servo.L2, 90)
                servo.set_angle(servo.R4, 0); servo.set_angle(servo.R1, 180); time.sleep(0.2)
                servo.set_angle(servo.R2, 45); servo.set_angle(servo.L1, 90); time.sleep(0.2)
                servo.set_angle(servo.R4, 45); servo.set_angle(servo.L4, 180); time.sleep(0.2)
                servo.set_angle(servo.R3, 180); servo.set_angle(servo.L3, 45)
                servo.set_angle(servo.R2, 90); servo.set_angle(servo.L1, 0); time.sleep(0.2)
                servo.set_angle(servo.L2, 135); servo.set_angle(servo.R1, 90); time.sleep(0.2)
            else:
                # WALK BACKWARD
                servo.set_angle(servo.R3, 135); servo.set_angle(servo.L3, 0); time.sleep(0.2)
                servo.set_angle(servo.L4, 135); servo.set_angle(servo.L2, 135)
                servo.set_angle(servo.R4, 0); servo.set_angle(servo.R1, 90); time.sleep(0.2)
                servo.set_angle(servo.R2, 90); servo.set_angle(servo.L1, 0); time.sleep(0.2)
                servo.set_angle(servo.R4, 45); servo.set_angle(servo.L4, 180); time.sleep(0.2)
                servo.set_angle(servo.R3, 180); servo.set_angle(servo.L3, 45)
                servo.set_angle(servo.R2, 45); servo.set_angle(servo.L1, 90); time.sleep(0.2)
                servo.set_angle(servo.L2, 90); servo.set_angle(servo.R1, 180); time.sleep(0.2)
            
        servo.move_to_home()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        servo.release_all()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=int, default=1)
    parser.add_argument("--cycles", type=int, default=1)
    args = parser.parse_args()
    run(args.dir, args.cycles)
