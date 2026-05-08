# mvmt_bow.py - Bow sequence matched from official firmware
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Bowing...")
        servo.move_to_home()
        time.sleep(0.2)
        
        # Bowing pose
        servo.set_angle(servo.L1, 0); servo.set_angle(servo.R1, 180)
        servo.set_angle(servo.L3, 0); servo.set_angle(servo.R3, 180)
        servo.set_angle(servo.L2, 180); servo.set_angle(servo.R2, 0)
        servo.set_angle(servo.R4, 0); servo.set_angle(servo.L4, 180)
        time.sleep(0.6)
        
        # Nod
        servo.set_angle(servo.L3, 90); servo.set_angle(servo.R3, 90)
        time.sleep(3.0)
        
        servo.move_to_home()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        servo.release_all()

if __name__ == "__main__":
    run()
