# mvmt_point.py - Point sequence matched from official firmware
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Pointing...")
        servo.set_angle(servo.L2, 60); servo.set_angle(servo.R1, 135)
        servo.set_angle(servo.R2, 100); servo.set_angle(servo.L4, 180)
        servo.set_angle(servo.L1, 25); servo.set_angle(servo.L3, 145)
        servo.set_angle(servo.R4, 80); servo.set_angle(servo.R3, 170)
        time.sleep(2.0)
        servo.move_to_home()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        servo.release_all()

if __name__ == "__main__":
    run()
