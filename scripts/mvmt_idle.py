# scripts/mvmt_idle.py - High-variety idle movements for Zerobot
# This file provides multiple random "life-like" gestures for the robot.

import time
import random
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def leg_twitch():
    """Twitches 2-3 random legs."""
    legs = random.sample([servo.L3, servo.R3, servo.L4, servo.R4], random.randint(2, 3))
    offset = random.randint(25, 45)
    for leg in legs:
        if leg in [servo.L3, servo.R4]: # Home 0
            servo.set_angle(leg, offset)
        else: # Home 180
            servo.set_angle(leg, 180 - offset)
    time.sleep(0.2)
    servo.move_to_home()

def body_shift():
    """Shifts body weight left or right using shoulders."""
    side = random.choice([-1, 1])
    offset = 20 * side
    # L1, L2 are on one side; R1, R2 on the other
    # Home: L1=45, R1=135, L2=135, R2=45
    servo.set_angle(servo.L1, 45 + offset)
    servo.set_angle(servo.L2, 135 + offset)
    servo.set_angle(servo.R1, 135 + offset)
    servo.set_angle(servo.R2, 45 + offset)
    time.sleep(0.3)
    servo.move_to_home()

def shoulder_shrug():
    """Small shrug with all shoulder servos."""
    offset = 15
    servo.set_angle(servo.L1, 45 + offset)
    servo.set_angle(servo.R1, 135 - offset)
    servo.set_angle(servo.L2, 135 - offset)
    servo.set_angle(servo.R2, 45 + offset)
    time.sleep(0.2)
    servo.move_to_home()

def knee_bounce():
    """Quick micro-bounce on all legs."""
    offset = 20
    for leg in [servo.L3, servo.R3, servo.L4, servo.R4]:
        if leg in [servo.L3, servo.R4]: servo.set_angle(leg, offset)
        else: servo.set_angle(leg, 180 - offset)
    time.sleep(0.15)
    servo.move_to_home()

def run():
    """Randomly selects one of the idle variations."""
    choice = random.choice([leg_twitch, body_shift, shoulder_shrug, knee_bounce])
    choice()
    time.sleep(0.1)

if __name__ == "__main__":
    run()
