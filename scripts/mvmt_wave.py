# mvmt_wave.py - Wave sequence matched from official firmware
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Waving...")
        servo.move_to_home()
        time.sleep(0.2)
        
        # Initial Wave Pose
        servo.set_angle(servo.R4, 80)
        servo.set_angle(servo.L3, 180)
        servo.set_angle(servo.L2, 60)
        servo.set_angle(servo.R1, 100)
        time.sleep(0.2)
        
        servo.set_angle(servo.L3, 180)
        time.sleep(0.3)
        
        for _ in range(4):
            servo.set_angle(servo.L3, 180)
            time.sleep(0.3)
            servo.set_angle(servo.L3, 100)
            time.sleep(0.3)
            
        servo.move_to_home()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        servo.release_all()

if __name__ == "__main__":
    run()
