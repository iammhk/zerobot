# mvmt_rest.py - Smooth transition to Rest pose
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Moving to Rest pose...")
        # 75% speed relative to standard movements
        # Standard delay is FRAME_DELAY. 75% speed = 1.33 * delay
        rest_delay = servo.config.FRAME_DELAY * 1.33
        
        # We'll assume we are coming from Stand or a Gesture
        # Step-wise transition for smoothness
        for i in range(10):
            # Target is 90 for all servos
            # L3 (Knee Front L): 0->90, R3 (Knee Front R): 180->90
            # L4 (Knee Hind L): 180->90, R4 (Knee Hind R): 0->90
            # Shoulders are already at 45/135
            
            # Simplified transition: Move each servo towards 90 by 10% each step
            # Note: This doesn't know the current angle exactly, so we'll just 
            # execute a fixed 10-step move from Stand to Rest.
            
            servo.set_angle(servo.L3, 0 + 9*i)
            servo.set_angle(servo.R3, 180 - 9*i)
            servo.set_angle(servo.L4, 180 - 9*i)
            servo.set_angle(servo.R4, 0 + 9*i)
            
            # Shoulders
            servo.set_angle(servo.L1, 45 + 4.5*i)
            servo.set_angle(servo.R1, 135 - 4.5*i)
            servo.set_angle(servo.L2, 135 - 4.5*i)
            servo.set_angle(servo.R2, 45 + 4.5*i)
            
            time.sleep(rest_delay)
            
        # Final set to exactly 90
        for i in range(8): servo.set_angle(i, 90)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
