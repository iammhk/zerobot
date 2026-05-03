"""
zerobot/utils/display.py - LCD Display Controller for ST7735 1.8" TFT
Used in the main project to provide visual feedback and "eyes" for the bot.
"""

from luma.core.interface.serial import spi
from luma.lcd.device import st7735
from luma.core.render import canvas
from PIL import ImageFont, ImageDraw
import time

class ZerobotDisplay:
    def __init__(self, width=160, height=128, rotate=1):
        # Configuration for Pi Zero SPI
        # port=0, device=0 (CE0 / GPIO 8)
        # gpio_DC=24, gpio_RST=25
        try:
            self.serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
            # Standard 1.8" TFT is often 128x160. 
            # rotate=1 or 3 for landscape, 0 or 2 for portrait.
            self.device = st7735(self.serial, width=width, height=height, rotate=rotate)
            self.width = self.device.width
            self.height = self.device.height
            print(f"Display initialized: {self.width}x{self.height}")
        except Exception as e:
            print(f"Failed to initialize display: {e}")
            self.device = None

    def clear(self):
        if self.device:
            with canvas(self.device) as draw:
                draw.rectangle((0, 0, self.width, self.height), outline="black", fill="black")

    def show_text(self, text, title="STATUS"):
        if not self.device: return
        with canvas(self.device) as draw:
            # Draw header
            draw.rectangle((0, 0, self.width, 20), fill="blue")
            draw.text((5, 2), title, fill="white")
            
            # Draw body text
            draw.text((5, 30), text, fill="white")

    def draw_eyes(self, expression="happy"):
        """Draws simple robot eyes on the screen."""
        if not self.device: return
        
        with canvas(self.device) as draw:
            center_y = self.height // 2
            eye_spacing = 40
            eye_size = 30
            
            left_eye_x = (self.width // 2) - eye_spacing
            right_eye_x = (self.width // 2) + eye_spacing

            if expression == "happy":
                # Circular eyes
                draw.ellipse((left_eye_x - eye_size//2, center_y - eye_size//2, 
                              left_eye_x + eye_size//2, center_y + eye_size//2), fill="cyan")
                draw.ellipse((right_eye_x - eye_size//2, center_y - eye_size//2, 
                              right_eye_x + eye_size//2, center_y + eye_size//2), fill="cyan")
            elif expression == "angry":
                # Rectangular slanted eyes
                draw.rectangle((left_eye_x - eye_size//2, center_y - 5, 
                                left_eye_x + eye_size//2, center_y + 5), fill="red")
                draw.rectangle((right_eye_x - eye_size//2, center_y - 5, 
                                right_eye_x + eye_size//2, center_y + 5), fill="red")
            elif expression == "blink":
                # Flat lines
                draw.line((left_eye_x - eye_size//2, center_y, left_eye_x + eye_size//2, center_y), fill="cyan", width=3)
                draw.line((right_eye_x - eye_size//2, center_y, right_eye_x + eye_size//2, center_y), fill="cyan", width=3)

if __name__ == "__main__":
    # Test block
    disp = ZerobotDisplay()
    if disp.device:
        disp.draw_eyes("happy")
        time.sleep(2)
        disp.draw_eyes("blink")
        time.sleep(0.5)
        disp.draw_eyes("happy")
        time.sleep(2)
        disp.show_text("System Online\nBattery: 85%", title="ZEROBOT")
        time.sleep(5)
