# mvmt_wakeup.py - Slow waking up and stretching sequence followed by a wave
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Waking up and stretching...")
        # 1. Start from Rest (all 90)
        for i in range(8): servo.set_angle(i, 90)
        time.sleep(1.0)
        
        # 2. Slow Shoulder Stretch (Move to home shoulders slowly)
        for i in range(10):
            servo.set_angle(servo.L1, 90 - 4.5*i)
            servo.set_angle(servo.R1, 90 + 4.5*i)
            servo.set_angle(servo.L2, 90 + 4.5*i)
            servo.set_angle(servo.R2, 90 - 4.5*i)
            time.sleep(servo.config.FRAME_DELAY * 2)
            
        # 3. Stretch Front (Lift front knees)
        for i in range(5):
            servo.set_angle(servo.L3, 0 + 10*i)
            servo.set_angle(servo.R3, 180 - 10*i)
            time.sleep(servo.config.FRAME_DELAY * 3)
        time.sleep(0.5)
        
        # 4. Stretch Back (Lift back knees)
        for i in range(5):
            servo.set_angle(servo.L4, 180 - 10*i)
            servo.set_angle(servo.R4, 0 + 10*i)
            time.sleep(servo.config.FRAME_DELAY * 3)
        time.sleep(0.5)
        
        # 5. Final Wave (Instead of Full Body Stretch)
        print("Waving hello!")
        servo.set_angle(servo.R4, 80)
        servo.set_angle(servo.L3, 180)
        servo.set_angle(servo.L2, 60)
        servo.set_angle(servo.R1, 100)
        time.sleep(0.2)
        
        for _ in range(3): # Shorter wave for startup
            servo.set_angle(servo.L3, 180)
            time.sleep(0.3)
            servo.set_angle(servo.L3, 100)
            time.sleep(0.3)
            
        # 6. Return to Stand (HOME)
        servo.move_to_home()
        print("Ready!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
