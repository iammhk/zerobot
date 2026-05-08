# mvmt_dance.py - Dance sequence matched from official firmware
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Dancing...")
        # Initial positions
        servo.set_angle(servo.R1, 90); servo.set_angle(servo.R2, 90)
        servo.set_angle(servo.L1, 90); servo.set_angle(servo.L2, 90)
        servo.set_angle(servo.R4, 160); servo.set_angle(servo.R3, 160)
        servo.set_angle(servo.L3, 10); servo.set_angle(servo.L4, 10)
        time.sleep(0.3)
        
        for _ in range(5):
            # Move 1
            servo.set_angle(servo.R4, 115); servo.set_angle(servo.R3, 115)
            servo.set_angle(servo.L3, 10); servo.set_angle(servo.L4, 10)
            time.sleep(0.3)
            # Move 2
            servo.set_angle(servo.R4, 160); servo.set_angle(servo.R3, 160)
            servo.set_angle(servo.L3, 65); servo.set_angle(servo.L4, 65)
            time.sleep(0.3)
            
        servo.move_to_home()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        servo.release_all()

if __name__ == "__main__":
    run()
