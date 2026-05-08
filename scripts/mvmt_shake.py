# mvmt_shake.py - Shake sequence matched from official firmware
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Shaking...")
        servo.move_to_home()
        time.sleep(servo.config.FRAME_DELAY * 2.0)
        
        servo.set_angle(servo.R1, 135); servo.set_angle(servo.L1, 45)
        servo.set_angle(servo.L3, 90); servo.set_angle(servo.R3, 90)
        servo.set_angle(servo.L2, 90); servo.set_angle(servo.R2, 90)
        time.sleep(servo.config.FRAME_DELAY * 2.0)
        
        for _ in range(5):
            servo.set_angle(servo.R4, 45); servo.set_angle(servo.L4, 135)
            time.sleep(servo.config.FRAME_DELAY * 3.0)
            servo.set_angle(servo.R4, 0); servo.set_angle(servo.L4, 180)
            time.sleep(servo.config.FRAME_DELAY * 3.0)
            
        servo.move_to_home()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        servo.release_all()

if __name__ == "__main__":
    run()
