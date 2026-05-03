"""
scripts/dsply_xprsn.py - Expression library for Zerobot LCD
Provides various eye animations and status displays for the 1.8" TFT.
Can be called from sesame_remote.py or main zerobot logic.
"""

import sys
import os
import time
import threading

# Add parent directory to path to import zerobot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zerobot.utils.display import ZerobotDisplay
from luma.core.render import canvas

class DsplyExpressions:
    def __init__(self):
        self.disp = ZerobotDisplay()
        self.width = self.disp.width
        self.height = self.disp.height
        self._lock = threading.Lock()

    def _draw_eye(self, draw, x, y, size, color="cyan", shape="circle", lid_pos=0):
        """Helper to draw a single eye with optional eyelid masking."""
        if shape == "circle":
            draw.ellipse((x - size//2, y - size//2, x + size//2, y + size//2), fill=color)
        elif shape == "rect":
            draw.rectangle((x - size//2, y - size//4, x + size//2, y + size//4), fill=color)
        
        # Eyelid masking (lid_pos 0.0 to 1.0)
        if lid_pos > 0:
            mask_height = int(size * lid_pos)
            draw.rectangle((x - size//2 - 2, y - size//2 - 2, 
                            x + size//2 + 2, y - size//2 + mask_height), fill="black")

    def happy(self):
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 45
                self._draw_eye(draw, self.width//2 - spacing, self.height//2, 40)
                self._draw_eye(draw, self.width//2 + spacing, self.height//2, 40)

    def blink(self):
        # Quick blink animation
        for pos in [0.2, 0.5, 0.8, 1.0, 0.5, 0.0]:
            with self._lock:
                with canvas(self.disp.device) as draw:
                    spacing = 45
                    self._draw_eye(draw, self.width//2 - spacing, self.height//2, 40, lid_pos=pos)
                    self._draw_eye(draw, self.width//2 + spacing, self.height//2, 40, lid_pos=pos)
            time.sleep(0.05)

    def angry(self):
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 45
                y = self.height//2
                # Slanted eyes
                draw.pieslice((self.width//2 - spacing - 25, y - 25, self.width//2 - spacing + 25, y + 25), 
                              start=30, end=330, fill="red")
                draw.pieslice((self.width//2 + spacing - 25, y - 25, self.width//2 + spacing + 25, y + 25), 
                              start=210, end=150, fill="red")

    def thinking(self):
        # Eyes looking up and moving left to right
        for offset in [-10, 0, 10, 0]:
            with self._lock:
                with canvas(self.disp.device) as draw:
                    spacing = 45
                    y = self.height//2 - 10
                    self._draw_eye(draw, self.width//2 - spacing + offset, y, 35, color="yellow")
                    self._draw_eye(draw, self.width//2 + spacing + offset, y, 35, color="yellow")
            time.sleep(0.3)

    def surprised(self):
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 50
                self._draw_eye(draw, self.width//2 - spacing, self.height//2, 55, color="white")
                self._draw_eye(draw, self.width//2 + spacing, self.height//2, 55, color="white")

    def sleeping(self):
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 45
                draw.line((self.width//2 - spacing - 15, self.height//2, 
                           self.width//2 - spacing + 15, self.height//2), fill="blue", width=4)
                draw.line((self.width//2 + spacing - 15, self.height//2, 
                           self.width//2 + spacing + 15, self.height//2), fill="blue", width=4)
                draw.text((self.width - 30, 20), "Zzz...", fill="white")

    def loading(self, text="UPDATING"):
        # Spinning circle animation
        for i in range(8):
            with self._lock:
                with canvas(self.disp.device) as draw:
                    draw.text((self.width//2 - 30, self.height - 30), text, fill="white")
                    # Draw a simple spinner
                    angle = i * 45
                    draw.pieslice((self.width//2 - 20, self.height//2 - 30, 
                                   self.width//2 + 20, self.height//2 + 10), 
                                  start=angle, end=angle+90, fill="magenta")
            time.sleep(0.1)

    def clear(self):
        self.disp.clear()

if __name__ == "__main__":
    # Test all expressions
    expr = DsplyExpressions()
    print("Testing Happy...")
    expr.happy()
    time.sleep(2)
    print("Blinking...")
    expr.blink()
    time.sleep(1)
    print("Angry...")
    expr.angry()
    time.sleep(2)
    print("Thinking...")
    expr.thinking()
    print("Surprised...")
    expr.surprised()
    time.sleep(2)
    print("Sleeping...")
    expr.sleeping()
    time.sleep(3)
    print("Loading...")
    expr.loading("BOOTING...")
    expr.clear()
