"""
scripts/dsply_test.py - Comprehensive display test for Zerobot
Iterates through all PREMIUM expressions in dsply_xprsn.py.
"""

import sys
import os
import time

# Add parent directory to path to import zerobot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.dsply_xprsn import DsplyExpressions

def run_test():
    print("Initializing PREMIUM Expression Test Suite...")
    expr = DsplyExpressions()
    
    test_sequence = [
        ("Booting", expr.loading, "LOADING SYSTEM"),
        ("Happy Pro", expr.happy, None),
        ("Looking Left", lambda: expr.happy(looking="left"), None),
        ("Looking Right", lambda: expr.happy(looking="right"), None),
        ("Blink", expr.blink, None),
        ("Love", expr.love, None),
        ("Matrix", expr.matrix, None),
        ("Scanner", expr.scan, None),
        ("Angry Pro", expr.angry, None)
    ]

    for name, func, arg in test_sequence:
        print(f"Playing Expression: {name}")
        if arg:
            func(arg)
        else:
            func()
        time.sleep(1.5)

    print("Test Complete.")
    expr.happy()

if __name__ == "__main__":
    run_test()
