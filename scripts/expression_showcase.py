# scripts/expression_showcase.py - Showcase script for all robot expressions
# This file is used to demonstrate and test all programmed display emotions in sequence.

import time
import sys
import os

# Add parent directory to path to import scripts and zerobot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.dsply_xprsn import DsplyExpressions

def main():
    print("--- Zerobot Expression Showcase ---")
    expr = DsplyExpressions()
    
    # List of expressions to showcase (name, method_name, duration)
    showcase = [
        ("Wake Up", "wakeup", 0), # wakeup has its own timing
        ("Happy", "happy", 2),
        ("Angry", "angry", 2),
        ("Surprised", "surprised", 2),
        ("Love / Hearts", "love", 2),
        ("Wink", "wink", 1),
        ("Blink", "blink", 1),
        ("Sleeping", "sleeping", 2),
        ("Pondering", "pondering", 2),
        ("Matrix Rain", "matrix", 0), # matrix has internal loop
        ("Scanner", "scan", 0),      # scan has internal loop
        ("Glitch", "glitch", 0),     # glitch has internal loop
        ("Party Mode", "party", 0),    # party has internal loop
        ("Dead / Error", "dead", 2),
        ("Sad", "sad", 2),
        ("Dizzy", "dizzy", 0),       # dizzy has internal loop
        ("Shake", "shake", 0),       # shake has internal loop
        ("Pulse", "pulse", 0),       # pulse has internal loop
        ("Squint", "squint", 0)      # squint has internal loop
    ]

    try:
        for name, func_name, duration in showcase:
            print(f"Showing: {name}...")
            
            # Get the method
            func = getattr(expr, func_name)
            
            # Execute
            func()
            
            # Wait if needed
            if duration > 0:
                time.sleep(duration)
            else:
                time.sleep(0.5) # Small gap between animations
                
        print("\nShowcase Complete!")
        expr.clear()
        
    except KeyboardInterrupt:
        print("\nShowcase interrupted.")
        expr.clear()

if __name__ == "__main__":
    main()
