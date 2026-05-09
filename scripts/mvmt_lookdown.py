# scripts/mvmt_lookdown.py - Robot tilts its body downwards
# This file is used in the Sesame Remote app to provide a "Look Down" gesture.

import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run(offset=30):
    """Executes the Look Down pose with a variable offset."""
    # Front Knees partially folded to lower the front
    servo.set_angle(servo.L3, 0 + offset)
    servo.set_angle(servo.R3, 180 - offset)
    
    # Hind Knees at Standing (Home)
    servo.set_angle(servo.L4, 180)
    servo.set_angle(servo.R4, 0)
    
    # Shoulders at Home
    servo.set_angle(servo.L1, 45)
    servo.set_angle(servo.R1, 135)
    servo.set_angle(servo.L2, 135)
    servo.set_angle(servo.R2, 45)
    
    time.sleep(0.2)

if __name__ == "__main__":
    run()
