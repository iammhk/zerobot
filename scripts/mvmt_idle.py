# scripts/mvmt_idle.py - Subtle idle movements for Zerobot
# This file is used to make the robot feel "alive" while waiting for commands.

import time
import random
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    """Executes a more prominent, noticeabe idle twitch."""
    # Choose 2 or 3 random legs to move more significantly
    legs = random.sample([servo.L3, servo.R3, servo.L4, servo.R4], random.randint(2, 3))
    
    # More prominent offset (25-35 degrees)
    offset = random.randint(25, 40)
    
    for leg in legs:
        if leg in [servo.L3, servo.R4]: # Home 0
            servo.set_angle(leg, offset)
        else: # Home 180
            servo.set_angle(leg, 180 - offset)
            
    time.sleep(0.2)
    
    # Small jitter before returning
    for leg in legs:
        if leg in [servo.L3, servo.R4]:
            servo.set_angle(leg, offset - 10)
        else:
            servo.set_angle(leg, 180 - offset + 10)
    
    time.sleep(0.15)
    
    # Return to home
    servo.move_to_home()
    time.sleep(0.1)

if __name__ == "__main__":
    run()
