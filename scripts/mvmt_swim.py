# mvmt_swim.py - Swim sequence matched from official firmware
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Swimming...")
        # Reset to 90
        for i in range(8): servo.set_angle(i, 90)
        time.sleep(servo.config.FRAME_DELAY * 4.0)
        
        for _ in range(4):
            # Stroke
            servo.set_angle(servo.R1, 135); servo.set_angle(servo.R2, 45)
            servo.set_angle(servo.L1, 45); servo.set_angle(servo.L2, 135)
            time.sleep(servo.config.FRAME_DELAY * 4.0)
            # Reset Shoulders
            servo.set_angle(servo.R1, 90); servo.set_angle(servo.R2, 90)
            servo.set_angle(servo.L1, 90); servo.set_angle(servo.L2, 90)
            time.sleep(servo.config.FRAME_DELAY * 4.0)
            
        servo.move_to_home()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        servo.release_all()

if __name__ == "__main__":
    run()
