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

    def _draw_pro_eye(self, draw, x, y, size, base_color="cyan", pupil_color="black", lid_pos=0, looking="center", shape="circle"):
        """Draws a premium eye with highlights and pupils."""
        if shape == "circle":
            draw.ellipse((x - size//2, y - size//2, x + size//2, y + size//2), fill=base_color, outline="white")
            px, py = x, y
            if looking == "left": px -= size//4
            elif looking == "right": px += size//4
            elif looking == "up": py -= size//4
            elif looking == "down": py += size//4
            draw.ellipse((px - size//4, py - size//4, px + size//4, py + size//4), fill=pupil_color)
            draw.ellipse((x - size//3, y - size//3, x - size//6, y - size//6), fill="white")
        elif shape == "x":
            draw.line((x-15, y-15, x+15, y+15), fill=base_color, width=4)
            draw.line((x+15, y-15, x-15, y+15), fill=base_color, width=4)
        elif shape == "flat":
            draw.line((x-size//2, y, x+size//2, y), fill=base_color, width=4)

        if lid_pos > 0:
            mask_h = int(size * lid_pos)
            draw.rectangle((x - size//2 - 2, y - size//2 - 2, x + size//2 + 2, y - size//2 + mask_h), fill="black")

    def wakeup(self):
        """Animation: Closed eyes -> Slowly open -> Blink -> Happy."""
        spacing = 45
        y = self.height//2
        
        # 1. Start with closed eyes (flat lines)
        with self._lock:
            with canvas(self.disp.device) as draw:
                self._draw_pro_eye(draw, self.width//2 - spacing, y, 45, base_color="#00FFFF", shape="flat")
                self._draw_pro_eye(draw, self.width//2 + spacing, y, 45, base_color="#00FFFF", shape="flat")
        time.sleep(1.5)

        # 2. Slowly open (lids moving up)
        for lid in [0.8, 0.6, 0.4, 0.2, 0.0]:
            with self._lock:
                with canvas(self.disp.device) as draw:
                    self._draw_pro_eye(draw, self.width//2 - spacing, y, 45, base_color="#00FFFF", lid_pos=lid)
                    self._draw_pro_eye(draw, self.width//2 + spacing, y, 45, base_color="#00FFFF", lid_pos=lid)
            time.sleep(0.2)

        # 3. Quick blink
        self.blink()
        
        # 4. Look around
        self.happy(looking="left")
        time.sleep(0.5)
        self.happy(looking="right")
        time.sleep(0.5)
        self.happy()

    def happy(self, looking="center"):
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 45
                self._draw_pro_eye(draw, self.width//2 - spacing, self.height//2, 45, base_color="#00FFFF", looking=looking)
                self._draw_pro_eye(draw, self.width//2 + spacing, self.height//2, 45, base_color="#00FFFF", looking=looking)

    def wink(self):
        for pos in [0.5, 1.0, 0.5, 0.0]:
            with self._lock:
                with canvas(self.disp.device) as draw:
                    spacing = 45
                    self._draw_pro_eye(draw, self.width//2 - spacing, self.height//2, 45)
                    self._draw_pro_eye(draw, self.width//2 + spacing, self.height//2, 45, lid_pos=pos)
            time.sleep(0.08)

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
                self._draw_pro_eye(draw, self.width//2 - spacing, y, 45, base_color="#FF0000")
                self._draw_pro_eye(draw, self.width//2 + spacing, y, 45, base_color="#FF0000")
                draw.polygon([(self.width//2 - 80, y - 40), (self.width//2 - 10, y - 10), (self.width//2 - 20, y - 5), (self.width//2 - 90, y - 35)], fill="white")
                draw.polygon([(self.width//2 + 80, y - 40), (self.width//2 + 10, y - 10), (self.width//2 + 20, y - 5), (self.width//2 + 90, y - 35)], fill="white")

    def sad(self):
        for i in range(5):
            with self._lock:
                with canvas(self.disp.device) as draw:
                    spacing = 45
                    y = self.height//2
                    self._draw_pro_eye(draw, self.width//2 - spacing, y, 45, base_color="#4169E1", looking="down")
                    self._draw_pro_eye(draw, self.width//2 + spacing, y, 45, base_color="#4169E1", looking="down")
                    draw.ellipse((self.width//2 + spacing + 5, y + 10 + (i*5), self.width//2 + spacing + 15, y + 25 + (i*5)), fill="#0000FF")
            time.sleep(0.1)

    def dead(self):
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 45
                self._draw_pro_eye(draw, self.width//2 - spacing, self.height//2, 45, base_color="white", shape="x")
                self._draw_pro_eye(draw, self.width//2 + spacing, self.height//2, 45, base_color="white", shape="x")

    def party(self):
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]
        for _ in range(20):
            with self._lock:
                with canvas(self.disp.device) as draw:
                    c1, c2 = random.sample(colors, 2)
                    spacing = 45
                    self._draw_pro_eye(draw, self.width//2 - spacing, self.height//2, 50, base_color=c1)
                    self._draw_pro_eye(draw, self.width//2 + spacing, self.height//2, 50, base_color=c2)
                    for _ in range(15):
                        draw.point((random.randint(0, self.width), random.randint(0, self.height)), fill=random.choice(colors))
            time.sleep(0.05)

    def glitch(self):
        for _ in range(10):
            with self._lock:
                with canvas(self.disp.device) as draw:
                    offset = random.randint(-5, 5)
                    spacing = 45
                    self._draw_pro_eye(draw, self.width//2 - spacing + offset, self.height//2, 45, base_color="#00FF00")
                    self._draw_pro_eye(draw, self.width//2 + spacing - offset, self.height//2, 45, base_color="#00FF00")
                    for _ in range(3):
                        gy = random.randint(0, self.height)
                        draw.rectangle((0, gy, self.width, gy+2), fill=random.choice(["#FF00FF", "#00FFFF"]))
            time.sleep(0.05)

    def pondering(self):
        for _ in range(4):
            with self._lock:
                with canvas(self.disp.device) as draw:
                    spacing = 45
                    self._draw_pro_eye(draw, self.width//2 - spacing, self.height//2, 45, looking="up")
                    self._draw_pro_eye(draw, self.width//2 + spacing, self.height//2, 45, looking="up")
                    draw.text((self.width//2 + 60, self.height//2 - 40), "?", fill="white")
            time.sleep(0.5)

    def sleeping(self):
        """Flat lines with a Zzz animation."""
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 45
                self._draw_pro_eye(draw, self.width//2 - spacing, self.height//2, 45, base_color="#4169E1", shape="flat")
                self._draw_pro_eye(draw, self.width//2 + spacing, self.height//2, 45, base_color="#4169E1", shape="flat")
                draw.text((self.width - 35, 20), "Zzz...", fill="white")

    def love(self):
        with self._lock:
            with canvas(self.disp.device) as draw:
                spacing = 45
                for side in [-1, 1]:
                    cx = self.width//2 + (side * spacing)
                    cy = self.height//2
                    draw.pieslice((cx-25, cy-25, cx, cy+10), start=180, end=0, fill="#FF69B4")
                    draw.pieslice((cx, cy-25, cx+25, cy+10), start=180, end=0, fill="#FF69B4")
                    draw.polygon([(cx-25, cy-5), (cx+25, cy-5), (cx, cy+25)], fill="#FF69B4")

    def matrix(self):
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
        for x in range(0, self.width - 40, 10):
            with self._lock:
                with canvas(self.disp.device) as draw:
                    draw.rectangle((x, self.height//2 - 10, x + 40, self.height//2 + 10), fill="#FF0000", outline="white")
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
    print("Waking up...")
    expr.wakeup()
    time.sleep(2)
    expr.party()
