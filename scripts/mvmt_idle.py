# scripts/mvmt_idle.py - Subtle idle movements for Zerobot
# This file is used to make the robot feel "alive" while waiting for commands.

import time
import random
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    """Executes a subtle, quick idle jitter."""
    # Choose a random set of legs to twitch
    legs = random.sample([servo.L3, servo.R3, servo.L4, servo.R4], 2)
    
    # Twitch out
    for leg in legs:
        offset = random.randint(5, 12)
        # Knees have different directions for 'up'
        if leg in [servo.L3, servo.R4]: # Home 0
            servo.set_angle(leg, offset)
        else: # Home 180
            servo.set_angle(leg, 180 - offset)
            
    time.sleep(0.15)
    
    # Return to home
    for leg in legs:
        servo.set_angle(leg, servo.HOME[leg])
    
    time.sleep(0.1)

if __name__ == "__main__":
    run()
