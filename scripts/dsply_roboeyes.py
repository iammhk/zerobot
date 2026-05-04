"""
scripts/dsply_roboeyes.py - Python Port of FluxGarage RoboEyes
Provides smoothly animated, rounded-rectangle robot eyes for luma.lcd.
"""

import sys
import os
import time
import threading
import random
import math

# Add parent directory to path to import zerobot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zerobot.utils.display import ZerobotDisplay
from luma.core.render import canvas

class RoboEyes:
    # Moods
    DEFAULT = 0
    TIRED = 1
    ANGRY = 2
    HAPPY = 3

    def __init__(self):
        self.disp = ZerobotDisplay()
        self.width = self.disp.width
        self.height = self.disp.height
        self._lock = threading.Lock()
        
        # State
        self.mood = self.DEFAULT
        self.eye_w = 38
        self.eye_h = 50
        self.eye_r = 10 # Corner radius
        self.spacing = 35
        
        # Positions
        self.offset_x = 0
        self.offset_y = 0
        self.lid_top = 0.0 # 0.0 to 1.0 (closed)
        self.lid_bottom = 0.0
        
    def _draw_robo_eye(self, draw, x, y, w, h, r, mood, lid_top=0.0, lid_bottom=0.0, base_color=None, shape="circle"):
        """Draws a FluxGarage style rounded rectangle eye."""
        # Main Eye Rect
        x1, y1 = x - w//2, y - h//2
        x2, y2 = x + w//2, y + h//2
        
        # Base Color
        color = base_color if base_color else "#00FFFF" # Default Cyan
        if not base_color:
            if mood == self.ANGRY: color = "#FF0000"
            elif mood == self.TIRED: color = "#FFA500"
            elif mood == self.HAPPY: color = "#00FF00"
        
        if shape == "circle":
            # Draw Rounded Rect (if Pillow < 8.2, we fallback to rectangle)
            try:
                draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=color)
            except AttributeError:
                draw.rectangle([x1, y1, x2, y2], fill=color)

            # Pupils / Highlights (Small circles)
            draw.ellipse([x - w//4, y - h//4, x, y], fill="white")
        elif shape == "x":
            # Dead eyes (FluxGarage style X)
            draw.line((x1, y1, x2, y2), fill=color, width=4)
            draw.line((x2, y1, x1, y2), fill=color, width=4)

        # Lid Masking (Simulating eyelids)
        if lid_top > 0:
            mask_h = int(h * lid_top)
            draw.rectangle([x1 - 2, y1 - 2, x2 + 2, y1 + mask_h], fill="black")
        if lid_bottom > 0:
            mask_h = int(h * lid_bottom)
            draw.rectangle([x1 - 2, y2 - mask_h, x2 + 2, y2 + 2], fill="black")
            
        # Mood specific overlays
        if mood == self.ANGRY:
            # Angry brows
            draw.polygon([x1, y1, x2, y1, x, y1 + h//3], fill="black")
        elif mood == self.HAPPY:
            # Happy "squint" from bottom
            draw.pieslice([x1, y2 - h//2, x2, y2 + h//2], start=180, end=0, fill="black")

    def update(self):
        """Renders the current state to the display."""
        with self._lock:
            with canvas(self.disp.device) as draw:
                cx, cy = self.width//2, self.height//2
                lx, rx = cx - self.spacing + self.offset_x, cx + self.spacing + self.offset_x
                ly, ry = cy + self.offset_y, cy + self.offset_y
                
                self._draw_robo_eye(draw, lx, ly, self.eye_w, self.eye_h, self.eye_r, self.mood, self.lid_top, self.lid_bottom)
                self._draw_robo_eye(draw, rx, ry, self.eye_w, self.eye_h, self.eye_r, self.mood, self.lid_top, self.lid_bottom)

    def set_mood(self, mood):
        self.mood = mood
        self.update()

    def blink(self):
        # Smooth blink
        for lid in [0.3, 0.7, 1.0, 0.5, 0.0]:
            self.lid_top = lid
            self.lid_bottom = lid
            self.update()
            time.sleep(0.03)

    def look(self, direction="center"):
        if direction == "left": self.offset_x = -15
        elif direction == "right": self.offset_x = 15
        elif direction == "up": self.offset_y = -10
        elif direction == "down": self.offset_y = 10
        else: self.offset_x, self.offset_y = 0, 0
        self.update()

    def wink(self, side="right"):
        # One eye blinks
        for lid in [0.5, 1.0, 0.5, 0.0]:
            with self._lock:
                with canvas(self.disp.device) as draw:
                    cx, cy = self.width//2, self.height//2
                    lx, rx = cx - self.spacing, cx + self.spacing
                    
                    # Draw left eye normal
                    if side == "right":
                        self._draw_robo_eye(draw, lx, cy, self.eye_w, self.eye_h, self.eye_r, self.mood)
                        self._draw_robo_eye(draw, rx, cy, self.eye_w, self.eye_h, self.eye_r, self.mood, lid, lid)
                    else:
                        self._draw_robo_eye(draw, lx, cy, self.eye_w, self.eye_h, self.eye_r, self.mood, lid, lid)
                        self._draw_robo_eye(draw, rx, cy, self.eye_w, self.eye_h, self.eye_r, self.mood)
            time.sleep(0.05)

    def dizzy(self):
        """Rolls the eyes in a circle."""
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            self.offset_x = int(math.cos(rad) * 15)
            self.offset_y = int(math.sin(rad) * 10)
            self.update()
            time.sleep(0.05)
        self.offset_x, self.offset_y = 0, 0
        self.update()

    def shake(self, duration=1.0):
        """Vibrates the eyes rapidly."""
        start = time.time()
        while time.time() - start < duration:
            self.offset_x = random.randint(-5, 5)
            self.offset_y = random.randint(-3, 3)
            self.update()
            time.sleep(0.02)
        self.offset_x, self.offset_y = 0, 0
        self.update()

    def pulse(self, cycles=3):
        """Eyes 'breathe' by changing size."""
        base_w, base_h = self.eye_w, self.eye_h
        for _ in range(cycles):
            for size in range(0, 8, 2):
                self.eye_w, self.eye_h = base_w + size, base_h + size
                self.update()
                time.sleep(0.05)
            for size in range(8, 0, -2):
                self.eye_w, self.eye_h = base_w + size, base_h + size
                self.update()
                time.sleep(0.05)
        self.eye_w, self.eye_h = base_w, base_h
        self.update()

    def squint(self):
        """Slowly squints both eyes."""
        for lid in [0.1, 0.2, 0.3, 0.4]:
            self.lid_top = lid
            self.lid_bottom = lid
            self.update()
            time.sleep(0.1)
        time.sleep(0.5)
        for lid in [0.3, 0.2, 0.1, 0.0]:
            self.lid_top = lid
            self.lid_bottom = lid
            self.update()
            time.sleep(0.1)

if __name__ == "__main__":
    eyes = RoboEyes()
    print("RoboEyes: Default Blink")
    eyes.update()
    time.sleep(1)
    eyes.blink()
    time.sleep(1)
    
    print("RoboEyes: Happy")
    eyes.set_mood(eyes.HAPPY)
    time.sleep(2)
    
    print("RoboEyes: Angry Look Left")
    eyes.set_mood(eyes.ANGRY)
    eyes.look("left")
    time.sleep(2)
    
    print("RoboEyes: Tired Wink")
    eyes.set_mood(eyes.TIRED)
    eyes.look("center")
    eyes.wink()
    time.sleep(2)
    
    eyes.set_mood(eyes.DEFAULT)
    print("Done.")
