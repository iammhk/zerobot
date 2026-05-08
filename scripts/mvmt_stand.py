# mvmt_stand.py - Official Stand Pose
import time
import sys, os

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

def run():
    try:
        print("Standing up...")
        servo.move_to_home()
        time.sleep(servo.config.FRAME_DELAY * 10.0)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
