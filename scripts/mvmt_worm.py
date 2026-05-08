# mvmt_worm.py - Worm sequence matched from official firmware
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Worming...")
        servo.move_to_home()
        time.sleep(0.2)
        
        # Flatten
        servo.set_angle(servo.R1, 180); servo.set_angle(servo.R2, 0)
        servo.set_angle(servo.L1, 0); servo.set_angle(servo.L2, 180)
        servo.set_angle(servo.R4, 90); servo.set_angle(servo.R3, 90)
        servo.set_angle(servo.L3, 90); servo.set_angle(servo.L4, 90)
        time.sleep(0.2)
        
        for _ in range(5):
            # Squish
            servo.set_angle(servo.R3, 45); servo.set_angle(servo.L3, 135)
            servo.set_angle(servo.R4, 45); servo.set_angle(servo.L4, 135)
            time.sleep(0.3)
            # Stretch
            servo.set_angle(servo.R3, 135); servo.set_angle(servo.L3, 45)
            servo.set_angle(servo.R4, 135); servo.set_angle(servo.L4, 45)
            time.sleep(0.3)
            
        servo.move_to_home()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        servo.release_all()

if __name__ == "__main__":
    run()
