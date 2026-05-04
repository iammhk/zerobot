"""
scripts/dsply_xprsn.py - High-Quality "RoboEyes" Expression Library for Zerobot
Uses the FluxGarage style (rounded rectangles) for all expressions.
"""

import sys
import os
import time
import threading
import random

# Add parent directory to path to import zerobot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.dsply_roboeyes import RoboEyes
from luma.core.render import canvas

class DsplyExpressions:
    def __init__(self):
        self.eyes = RoboEyes()
        self.width = self.eyes.width
        self.height = self.eyes.height

    def wakeup(self):
        """Classic waking up sequence with RoboEyes."""
        self.eyes.set_mood(self.eyes.TIRED)
        self.eyes.lid_top = 1.0
        self.eyes.update()
        time.sleep(1.0)
        
        for lid in [0.8, 0.6, 0.4, 0.2, 0.0]:
            self.eyes.lid_top = lid
            self.eyes.update()
            time.sleep(0.2)
            
        self.eyes.blink()
        self.eyes.set_mood(self.eyes.DEFAULT)
        self.eyes.look("left")
        time.sleep(0.5)
        self.eyes.look("right")
        time.sleep(0.5)
        self.eyes.look("center")

    def happy(self, looking="center"):
        self.eyes.set_mood(self.eyes.HAPPY)
        self.eyes.look(looking)

    def angry(self):
        self.eyes.set_mood(self.eyes.ANGRY)

    def surprised(self):
        self.eyes.set_mood(self.eyes.DEFAULT)
        old_w, old_h = self.eyes.eye_w, self.eyes.eye_h
        self.eyes.eye_w, self.eyes.eye_h = 48, 55
        self.eyes.update()
        time.sleep(1)
        self.eyes.eye_w, self.eyes.eye_h = old_w, old_h

    def love(self):
        with self.eyes._lock:
            with canvas(self.eyes.disp.device) as draw:
                spacing = self.eyes.spacing
                for side in [-1, 1]:
                    cx, cy = self.width//2 + (side * spacing), self.height//2
                    draw.pieslice((cx-20, cy-20, cx, cy+8), start=180, end=0, fill="#FF69B4")
                    draw.pieslice((cx, cy-20, cx+20, cy+8), start=180, end=0, fill="#FF69B4")
                    draw.polygon([(cx-20, cy-4), (cx+20, cy-4), (cx, cy+20)], fill="#FF69B4")

    def wink(self):
        self.eyes.wink()

    def blink(self):
        self.eyes.blink()

    def sleeping(self):
        self.eyes.set_mood(self.eyes.TIRED)
        self.eyes.lid_top = 0.95
        self.eyes.update()

    def pondering(self):
        self.eyes.set_mood(self.eyes.DEFAULT)
        self.eyes.look("up")
        with self.eyes._lock:
            with canvas(self.eyes.disp.device) as draw:
                cx, cy = self.width//2, self.height//2
                self.eyes._draw_robo_eye(draw, cx-self.eyes.spacing, cy-10, self.eyes.eye_w, self.eyes.eye_h, self.eyes.eye_r, self.eyes.mood)
                self.eyes._draw_robo_eye(draw, cx+self.eyes.spacing, cy-10, self.eyes.eye_w, self.eyes.eye_h, self.eyes.eye_r, self.eyes.mood)
                draw.text((cx + 60, cy - 40), "?", fill="white")

    def matrix(self):
        cols = self.width // 10
        rows = [random.randint(-20, 0) for _ in range(cols)]
        for _ in range(15):
            with canvas(self.eyes.disp.device) as draw:
                for i, r in enumerate(rows):
                    char = random.choice("01ABCDEF")
                    y = r * 10
                    draw.text((i*10, y), char, fill="#00FF00")
                    rows[i] = (r + 1) if y < self.height else 0
            time.sleep(0.05)

    def scan(self):
        for x in range(0, self.width - 40, 10):
            with canvas(self.eyes.disp.device) as draw:
                draw.rectangle((x, self.height//2 - 10, x + 40, self.height//2 + 10), fill="#FF0000", outline="white")
            time.sleep(0.05)

    def glitch(self):
        for _ in range(10):
            with canvas(self.eyes.disp.device) as draw:
                offset = random.randint(-5, 5)
                self.eyes._draw_robo_eye(draw, self.width//2 - self.eyes.spacing + offset, self.height//2, 45, 50, 10, self.eyes.DEFAULT)
                self.eyes._draw_robo_eye(draw, self.width//2 + self.eyes.spacing - offset, self.height//2, 45, 50, 10, self.eyes.DEFAULT)
                for _ in range(3):
                    gy = random.randint(0, self.height)
                    draw.rectangle((0, gy, self.width, gy+2), fill=random.choice(["#FF00FF", "#00FFFF"]))
            time.sleep(0.05)

    def party(self):
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]
        for _ in range(20):
            with canvas(self.eyes.disp.device) as draw:
                c1, c2 = random.sample(colors, 2)
                self.eyes._draw_robo_eye(draw, self.width//2 - self.eyes.spacing, self.height//2, 50, 55, 10, self.eyes.DEFAULT, base_color=c1)
                self.eyes._draw_robo_eye(draw, self.width//2 + self.eyes.spacing, self.height//2, 50, 55, 10, self.eyes.DEFAULT, base_color=c2)
                for _ in range(15):
                    draw.point((random.randint(0, self.width), random.randint(0, self.height)), fill=random.choice(colors))
            time.sleep(0.05)

    def dead(self):
        """X-eyes for errors or shutdown."""
        with canvas(self.eyes.disp.device) as draw:
            spacing = self.eyes.spacing
            self.eyes._draw_robo_eye(draw, self.width//2 - spacing, self.height//2, 45, 50, 10, self.eyes.DEFAULT, base_color="white", shape="x")
            self.eyes._draw_robo_eye(draw, self.width//2 + spacing, self.height//2, 45, 50, 10, self.eyes.DEFAULT, base_color="white", shape="x")

    def sad(self):
        self.eyes.set_mood(self.eyes.TIRED)
        self.eyes.look("down")

    def dizzy(self):
        self.eyes.dizzy()

    def shake(self):
        self.eyes.shake()

    def pulse(self):
        self.eyes.pulse()

    def squint(self):
        self.eyes.squint()

    def clear(self):
        self.eyes.disp.clear()

if __name__ == "__main__":
    expr = DsplyExpressions()
    expr.wakeup()
    expr.party()
    expr.clear()
