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
    print("Initializing Expression Test Suite...")
    expr = DsplyExpressions()
    
    test_sequence = [
        ("Booting", expr.loading),
        ("Happy", expr.happy),
        ("Blink", expr.blink),
        ("Surprised", expr.surprised),
        ("Thinking", expr.thinking),
        ("Angry", expr.angry),
        ("Sleeping", expr.sleeping),
        ("Blink Again", expr.blink),
        ("Happy Final", expr.happy)
    ]

    for name, func in test_sequence:
        print(f"Playing Expression: {name}")
        if name == "Booting":
            func("SYSTEM START")
        else:
            func()
        time.sleep(2)

    print("Test Complete. Screen will stay on 'Happy'.")

if __name__ == "__main__":
    run_test()
