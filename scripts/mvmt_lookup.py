# scripts/mvmt_lookup.py - Robot tilts its body upwards
# This file is used in the Sesame Remote app to provide a "Look Up" gesture.

import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    """Executes the Look Up pose."""
    # Front Knees at Standing (Home)
    servo.set_angle(servo.L3, 0)
    servo.set_angle(servo.R3, 180)
    
    # Hind Knees partially folded to lower the back
    servo.set_angle(servo.L4, 120)
    servo.set_angle(servo.R4, 60)
    
    # Shoulders at Home
    servo.set_angle(servo.L1, 45)
    servo.set_angle(servo.R1, 135)
    servo.set_angle(servo.L2, 135)
    servo.set_angle(servo.R2, 45)
    
    time.sleep(0.2)

if __name__ == "__main__":
    run()
