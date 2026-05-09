# mvmt_wakeup.py - Slow waking up and stretching sequence
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
            # L1: 90->45, R1: 90->135, L2: 90->135, R2: 90->45
            servo.set_angle(servo.L1, 90 - 4.5*i)
            servo.set_angle(servo.R1, 90 + 4.5*i)
            servo.set_angle(servo.L2, 90 + 4.5*i)
            servo.set_angle(servo.R2, 90 - 4.5*i)
            time.sleep(servo.config.FRAME_DELAY * 2)
            
        # 3. Yawn/Stretch Front (Lift front knees)
        for i in range(5):
            servo.set_angle(servo.L3, 0 + 10*i)
            servo.set_angle(servo.R3, 180 - 10*i)
            time.sleep(servo.config.FRAME_DELAY * 3)
        time.sleep(0.5)
        
        # 4. Yawn/Stretch Back (Lift back knees)
        for i in range(5):
            servo.set_angle(servo.L4, 180 - 10*i)
            servo.set_angle(servo.R4, 0 + 10*i)
            time.sleep(servo.config.FRAME_DELAY * 3)
        time.sleep(0.5)
        
        # 5. Full Body Stretch (Flatten out)
        servo.set_angle(servo.L3, 160); servo.set_angle(servo.R3, 20)
        servo.set_angle(servo.L4, 20); servo.set_angle(servo.R4, 160)
        time.sleep(0.8)
        
        # 6. Return to Stand (HOME)
        servo.move_to_home()
        print("Ready!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
