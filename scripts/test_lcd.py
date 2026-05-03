"""
scripts/test_lcd.py - Hardware test for the 1.8" TFT SPI LCD
Used to verify wiring and basic functionality of the ST7735 display.
"""

import sys
import os
import time

# Add parent directory to path to import zerobot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zerobot.utils.display import ZerobotDisplay

def test_display():
    print("Initializing LCD Test...")
    # Standard 1.8" modules are usually 128x160.
    # Note: If your screen is 120x160, you can adjust width/height here.
    disp = ZerobotDisplay(width=160, height=128, rotate=1)
    
    if not disp.device:
        print("ERROR: Could not initialize display. Check your SPI settings and wiring.")
        return

    expressions = ["happy", "blink", "angry", "happy"]
    
    print("Cycling through expressions...")
    for exp in expressions:
        print(f"Showing: {exp}")
        disp.draw_eyes(exp)
        time.sleep(1.5)
    
    print("Testing text rendering...")
    disp.show_text("Hello Mohak!\nDisplay: 1.8\" TFT\nDriver: ST7735\nStatus: OK", title="HARDWARE TEST")
    time.sleep(5)
    
    print("Test complete. Clearing screen.")
    disp.clear()

if __name__ == "__main__":
    test_display()
