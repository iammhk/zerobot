# mvmt_pushups.py - Pushups sequence matched from official firmware
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Doing pushups...")
        servo.move_to_home()
        time.sleep(0.2)
        
        servo.set_angle(servo.L1, 0)
        servo.set_angle(servo.R1, 180)
        servo.set_angle(servo.L3, 90)
        servo.set_angle(servo.R3, 90)
        time.sleep(0.5)
        
        for _ in range(4):
            # Down
            servo.set_angle(servo.L3, 0)
            servo.set_angle(servo.R3, 180)
            time.sleep(0.6)
            # Up
            servo.set_angle(servo.L3, 90)
            servo.set_angle(servo.R3, 90)
            time.sleep(0.5)
            
        servo.move_to_home()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        servo.release_all()

if __name__ == "__main__":
    run()
