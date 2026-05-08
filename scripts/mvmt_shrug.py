# mvmt_shrug.py - Shrug sequence matched from official firmware
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Shrugging...")
        servo.move_to_home()
        time.sleep(servo.config.FRAME_DELAY * 2.0)
        
        # Lower knees
        servo.set_angle(servo.R3, 90); servo.set_angle(servo.R4, 90)
        servo.set_angle(servo.L3, 90); servo.set_angle(servo.L4, 90)
        time.sleep(servo.config.FRAME_DELAY * 10.0)
        
        # Shrug (Knees up)
        servo.set_angle(servo.R3, 0); servo.set_angle(servo.R4, 180)
        servo.set_angle(servo.L3, 180); servo.set_angle(servo.L4, 0)
        time.sleep(1.5)
        
        servo.move_to_home()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        servo.release_all()

if __name__ == "__main__":
    run()
