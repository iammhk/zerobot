# st7735.py - ST7735 TFT display driver for zerobot
# This file is used in the actual project to control the 1.8-inch TFT display.

import sys
from typing import Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
    import ST7735
except ImportError:
    ST7735 = None
    Image = None

class ST7735Display:
    """
    Utility for the ST7735 TFT display (128x160).
    Uses SPI interface.
    """

    def __init__(
        self,
        port: int = 0,
        cs: int = 0,
        dc: int = 24,
        backlight: int = 18,
        rst: int = 25,
        width: int = 128,
        height: int = 160,
        rotation: int = 90,
        invert: bool = False
    ):
        self.width = width
        self.height = height
        self.rotation = rotation
        self._display = None

        if ST7735 is not None:
            try:
                self._display = ST7735.ST7735(
                    port=port,
                    cs=cs,
                    dc=dc,
                    backlight=backlight,
                    rst=rst,
                    width=width,
                    height=height,
                    rotation=rotation,
                    invert=invert,
                    spi_speed_hz=4000000
                )
                self._display.begin()
            except Exception as e:
                print(f"Warning: Could not initialize ST7735 display: {e}")

        # Create drawing buffer
        if Image:
            self.image = Image.new("RGB", (width, height), (0, 0, 0))
            self.draw = ImageDraw.Draw(self.image)
        else:
            self.image = None
            self.draw = None

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)):
        """Clear the display buffer and screen."""
        if self.draw:
            self.draw.rectangle((0, 0, self.width, self.height), fill=color)
        self.update()

    def show_text(
        self,
        text: str,
        x: int = 0,
        y: int = 0,
        color: Tuple[int, int, int] = (255, 255, 255),
        font_size: int = 12
    ):
        """Draw text to the display buffer."""
        if not self.draw:
            return

        try:
            # Try to load a default font
            font = ImageFont.load_default()
            # If we wanted to support custom font sizes, we'd need a .ttf file
        except Exception:
            font = None

        self.draw.text((x, y), text, fill=color, font=font)
        self.update()

    def draw_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: Tuple[int, int, int] = (255, 255, 255)
    ):
        """Draw a line to the display buffer."""
        if self.draw:
            self.draw.line((x1, y1, x2, y2), fill=color)
            self.update()

    def update(self):
        """Push the current buffer to the physical display."""
        if self._display and self.image:
            self._display.display(self.image)

    def close(self):
        """Shutdown the display."""
        if self._display:
            try:
                self._display.set_backlight(0)
            except:
                pass
