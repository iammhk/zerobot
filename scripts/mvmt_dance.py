# crab_dance.py - Fun movements for the Crab-Bot
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- Channel Mapping ---

ALL_SERVOS = [0, 1, 2, 3, 4, 5, 6, 7]

# --- HARD LIMITS ---


# Standing Home Position





def push_ups(reps=3):
    print("Doing push-ups...")
    for i in range(reps):
        # Down
        for ch in [servo.L3, servo.R3, servo.L4, servo.R4]: servo.set_angle(ch, 10)
        time.sleep(0.6)
        # Up
        for ch in [servo.L3, servo.R3, servo.L4, servo.R4]: servo.set_angle(ch, 80)
        time.sleep(0.6)
    for ch in [servo.L3, servo.R3, servo.L4, servo.R4]: servo.set_angle(ch, servo.HOME[ch])

def wave(reps=4):
    print("Waving!")
    # Lift Front Left leg high
    servo.set_angle(servo.L3, 160) 
    time.sleep(0.4)
    for i in range(reps):
        servo.set_angle(servo.L1, 10)
        time.sleep(0.2)
        servo.set_angle(servo.L1, 80)
        time.sleep(0.2)
    servo.set_angle(servo.L1, servo.HOME[servo.L1])
    servo.set_angle(servo.L3, servo.HOME[servo.L3])



try:
    print("Standing up...")
    for ch, angle in HOME.items(): servo.set_angle(ch, angle)
    time.sleep(1.5)

    push_ups(3)
    time.sleep(1)
    wave(4)
    time.sleep(1)
    
    print("Resting...")
    for ch in range(8): servo.set_angle(ch, 90)
    time.sleep(1)
    for i in range(8): servo.release(i)

except KeyboardInterrupt:
    for i in range(8): servo.release(i)
