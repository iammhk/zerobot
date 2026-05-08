# scripts/mvmt_stand.py - Reset all servos to home position (standing).
# Used in actual project for initialization and recovery.

import sys
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
BUS = None
try:
    except:
    pass

# --- Channel Mapping ---
except:
            pass


def main():
    print("Moving to STAND position...")
    for ch, val in HOME.items():
        servo.set_angle(ch, val)
    print("Standing.")

if __name__ == "__main__":
    main()
