"""
scripts/dsply_xprsn.py - High-Quality "Premium" Expression Library for Zerobot
Features layered eyes, pupils, highlights, and complex animations.
"""

import sys
import os
import time
import threading
import random

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

    def _draw_pro_eye(self, draw, x, y, size, base_color="cyan", pupil_color="black", lid_pos=0, looking="center"):
        """Draws a premium eye with highlights and pupils."""
        # 1. Base Eye (The 'iris')
        draw.ellipse((x - size//2, y - size//2, x + size//2, y + size//2), fill=base_color, outline="white")
        
        # 2. Pupil Position
        px, py = x, y
        if looking == "left": px -= size//4
        elif looking == "right": px += size//4
        elif looking == "up": py -= size//4
        elif looking == "down": py += size//4
        
        # 3. Draw Pupil
        draw.ellipse((px - size//4, py - size//4, px + size//4, py + size//4), fill=pupil_color)
        
        # 4. Highlight (Reflection)
        draw.ellipse((x - size//3, y - size//3, x - size//6, y - size//6), fill="white")

        # 5. Eyelid (Masking)
        if lid_pos > 0:
            mask_h = int(size * lid_pos)
            draw.rectangle((x - size//2 - 2, y - size//2 - 2, x + size//2 + 2, y - size//2 + mask_h), fill="black")

    def happy(self, looking="center"):
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 45
                self._draw_pro_eye(draw, self.width//2 - spacing, self.height//2, 45, base_color="#00FFFF", looking=looking)
                self._draw_pro_eye(draw, self.width//2 + spacing, self.height//2, 45, base_color="#00FFFF", looking=looking)

    def blink(self):
        for pos in [0.3, 0.7, 1.0, 0.5, 0.0]:
            with self._lock:
                with canvas(self.disp.device) as draw:
                    spacing = 45
                    self._draw_pro_eye(draw, self.width//2 - spacing, self.height//2, 45, lid_pos=pos)
                    self._draw_pro_eye(draw, self.width//2 + spacing, self.height//2, 45, lid_pos=pos)
            time.sleep(0.04)

    def angry(self):
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 45
                y = self.height//2
                # Red glowing irises
                self._draw_pro_eye(draw, self.width//2 - spacing, y, 45, base_color="#FF0000")
                self._draw_pro_eye(draw, self.width//2 + spacing, y, 45, base_color="#FF0000")
                # Angry Brows (Diagonal rectangles)
                draw.polygon([(self.width//2 - 80, y - 40), (self.width//2 - 10, y - 10), (self.width//2 - 20, y - 5), (self.width//2 - 90, y - 35)], fill="white")
                draw.polygon([(self.width//2 + 80, y - 40), (self.width//2 + 10, y - 10), (self.width//2 + 20, y - 5), (self.width//2 + 90, y - 35)], fill="white")

    def love(self):
        """Heart shaped pink eyes."""
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 45
                for side in [-1, 1]:
                    cx = self.width//2 + (side * spacing)
                    cy = self.height//2
                    # Simple heart shape
                    draw.pieslice((cx-25, cy-25, cx, cy+10), start=180, end=0, fill="#FF69B4")
                    draw.pieslice((cx, cy-25, cx+25, cy+10), start=180, end=0, fill="#FF69B4")
                    draw.polygon([(cx-25, cy-5), (cx+25, cy-5), (cx, cy+25)], fill="#FF69B4")

    def matrix(self):
        """Falling green code effect."""
        cols = self.width // 10
        rows = [random.randint(-20, 0) for _ in range(cols)]
        for _ in range(15):
            with self._lock:
                with canvas(self.disp.device) as draw:
                    for i, r in enumerate(rows):
                        char = random.choice("01ABCDEF")
                        y = r * 10
                        draw.text((i*10, y), char, fill="#00FF00")
                        rows[i] = (r + 1) if y < self.height else 0
            time.sleep(0.05)

    def scan(self):
        """Red Cylon/KITT style scanner."""
        for x in range(0, self.width - 40, 10):
            with self._lock:
                with canvas(self.disp.device) as draw:
                    draw.rectangle((x, self.height//2 - 10, x + 40, self.height//2 + 10), fill="#FF0000", outline="white")
                    # Add a tail effect
                    draw.rectangle((x-20, self.height//2 - 5, x, self.height//2 + 5), fill="#880000")
            time.sleep(0.05)
        for x in range(self.width - 40, 0, -10):
            with self._lock:
                with canvas(self.disp.device) as draw:
                    draw.rectangle((x, self.height//2 - 10, x + 40, self.height//2 + 10), fill="#FF0000", outline="white")
            time.sleep(0.05)

    def loading(self, text="UPDATING"):
        colors = ["#FF00FF", "#00FFFF", "#FFFF00", "#00FF00"]
        for i in range(12):
            with self._lock:
                with canvas(self.disp.device) as draw:
                    draw.text((self.width//2 - 30, self.height - 20), text, fill="white")
                    angle = i * 30
                    draw.pieslice((self.width//2 - 30, self.height//2 - 40, self.width//2 + 30, self.height//2 + 20), 
                                  start=angle, end=angle+60, fill=colors[i%4], outline="white")
            time.sleep(0.08)

    def clear(self):
        self.disp.clear()

if __name__ == "__main__":
    expr = DsplyExpressions()
    print("Happy (Premium)...")
    expr.happy(looking="right")
    time.sleep(2)
    print("Love...")
    expr.love()
    time.sleep(2)
    print("Angry (Aggressive)...")
    expr.angry()
    time.sleep(2)
    print("Scan...")
    expr.scan()
    print("Matrix...")
    expr.matrix()
