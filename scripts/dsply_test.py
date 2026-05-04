"""
scripts/dsply_test.py - Comprehensive display test for Zerobot
Iterates through all expressions in dsply_xprsn.py.
"""

import sys
import os
import time

# Add parent directory to path to import zerobot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.dsply_xprsn import DsplyExpressions

def run_test():
    print("Initializing HUGE Expression Test Suite...")
    expr = DsplyExpressions()
    
    test_sequence = [
        ("Waking Up", expr.wakeup, None),
        ("Happy", expr.happy, None),
        ("Wink", expr.wink, None),
        ("Pondering", expr.pondering, None),
        ("Love", expr.love, None),
        ("Party", expr.party, None),
        ("Glitch", expr.glitch, None),
        ("Matrix", expr.matrix, None),
        ("Scanner", expr.scan, None),
        ("Angry", expr.angry, None),
        ("Sad", expr.sad, None),
        ("Dead", expr.dead, None),
        ("Dizzy", expr.dizzy, None),
        ("Shake", expr.shake, None),
        ("Pulse", expr.pulse, None),
        ("Squint", expr.squint, None)
    ]

    for name, func, arg in test_sequence:
        print(f"Playing Expression: {name}")
        if arg:
            func(arg)
        else:
            func()
        time.sleep(1.0)

    print("Test Complete.")
    expr.happy()

if __name__ == "__main__":
    run_test()
