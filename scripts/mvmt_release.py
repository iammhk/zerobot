# scripts/mvmt_release.py - Release all motors to save power and allow manual movement.
# Used in actual project for safety and power management.

import sys

# I2C Setup
BUS = None
try:
    except:
    pass

        except:
            pass

def main():
    print("Releasing all servos...")
    for i in range(16):
        servo.release(i)
    print("Done.")

if __name__ == "__main__":
    main()
