# display.py - TFT display management tool for zerobot
# This file is used in the actual project to allow the agent to control the ST7735 display.

import sys
from typing import Any, List, Optional

from loguru import logger

from zerobot.agent.tools.base import Tool, tool_parameters
from zerobot.agent.tools.schema import IntegerSchema, StringSchema, tool_parameters_schema
from zerobot.utils.st7735 import ST7735Display


@tool_parameters(
    tool_parameters_schema(
        action=StringSchema(
            "The display action to perform",
            enum=["show_text", "clear", "draw_line"],
        ),
        text=StringSchema("The text to display (for 'show_text')", nullable=True),
        x=IntegerSchema("X coordinate (0-127)", minimum=0, maximum=127, nullable=True),
        y=IntegerSchema("Y coordinate (0-159)", minimum=0, maximum=159, nullable=True),
        x2=IntegerSchema("End X coordinate (for 'draw_line')", minimum=0, maximum=127, nullable=True),
        y2=IntegerSchema("End Y coordinate (for 'draw_line')", minimum=0, maximum=159, nullable=True),
        color=StringSchema("Color in R,G,B format (e.g. '255,255,255')", nullable=True),
        required=["action"],
    )
)
class DisplayTool(Tool):
    """Tool to control the ST7735 TFT display."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._display = None

    @property
    def name(self) -> str:
        return "display"

    @property
    def description(self) -> str:
        return (
            "Control the attached ST7735 TFT display. "
            "Actions: show_text (at x,y), clear (black screen), draw_line (from x,y to x2,y2). "
            "The display resolution is 128x160."
        )

    def _get_display(self) -> ST7735Display:
        """Lazy initialization of the display driver."""
        if self._display is None:
            self._display = ST7735Display()
        return self._display

    def _parse_color(self, color_str: Optional[str]) -> tuple[int, int, int]:
        if not color_str:
            return (255, 255, 255)
        try:
            r, g, b = map(int, color_str.split(","))
            return (r, g, b)
        except Exception:
            return (255, 255, 255)

    async def execute(
        self,
        action: str,
        text: str | None = None,
        x: int = 0,
        y: int = 0,
        x2: int | None = None,
        y2: int | None = None,
        color: str | None = None,
        **kwargs: Any,
    ) -> str:
        if sys.platform != "linux":
            return f"Error: Display tool is only supported on Linux (Raspberry Pi), but current OS is {sys.platform}."

        try:
            display = self._get_display()
            rgb = self._parse_color(color)
            
            if action == "show_text":
                if text is None:
                    return "Error: Action 'show_text' requires 'text'."
                display.show_text(text, x=x, y=y, color=rgb)
                return f"Displayed text '{text}' at ({x}, {y})."
            
            elif action == "clear":
                display.clear(color=rgb if color else (0,0,0))
                return "Cleared the display."
            
            elif action == "draw_line":
                if x2 is None or y2 is None:
                    return "Error: Action 'draw_line' requires 'x2' and 'y2'."
                display.draw_line(x, y, x2, y2, color=rgb)
                return f"Drew line from ({x}, {y}) to ({x2}, {y2})."
            
            else:
                return f"Error: Unknown action '{action}'"

        except Exception as e:
            logger.exception("Display tool error")
            return f"Error controlling display: {str(e)}"

    def __del__(self):
        if self._display:
            try:
                self._display.close()
            except:
                pass
