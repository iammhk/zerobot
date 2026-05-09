# mvmt_sleep.py - Slow flattening and winding down sequence
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Winding down and going to sleep...")
        # 1. Slow Knee Lowering (Move knees to 90 slowly)
        # We'll step from current state (Stand is 0/180) to 90
        for i in range(10):
            # Front L: 0->90, R: 180->90
            servo.set_angle(servo.L3, 0 + 9*i)
            servo.set_angle(servo.R3, 180 - 9*i)
            # Hind L: 180->90, R: 0->90
            servo.set_angle(servo.L4, 180 - 9*i)
            servo.set_angle(servo.R4, 0 + 9*i)
            time.sleep(servo.config.FRAME_DELAY * 2)
            
        # 2. Slow Shoulder Reset (Move shoulders to 90 slowly)
        # L1: 45->90, R1: 135->90, L2: 135->90, R2: 45->90
        for i in range(10):
            servo.set_angle(servo.L1, 45 + 4.5*i)
            servo.set_angle(servo.R1, 135 - 4.5*i)
            servo.set_angle(servo.L2, 135 - 4.5*i)
            servo.set_angle(servo.R2, 45 + 4.5*i)
            time.sleep(servo.config.FRAME_DELAY * 2)
            
        time.sleep(0.5)
        print("Shutting down motors...")
        servo.release_all()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
