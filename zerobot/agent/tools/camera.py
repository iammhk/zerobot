# camera.py - Camera tool for zerobot
# Purpose: Allows the agent to take photos using the Pi Camera.
# Used in: Actual project (Agent tool integration).

import os
import sys
import datetime
from typing import Any

from loguru import logger

from zerobot.agent.tools.base import Tool, tool_parameters
from zerobot.agent.tools.schema import StringSchema, tool_parameters_schema
from zerobot.camera import ZerobotCamera, HAS_PICAMERA2

@tool_parameters(
    tool_parameters_schema(
        action=StringSchema(
            "The camera action to perform",
            enum=["capture"],
        ),
        filename=StringSchema("Optional filename to save the image to", nullable=True),
        required=["action"],
    )
)
class CameraTool(Tool):
    """Tool to capture images using the Raspberry Pi Camera."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera = None

    @property
    def name(self) -> str:
        return "camera"

    @property
    def description(self) -> str:
        return "Capture images using the Raspberry Pi Camera Module. Action 'capture' takes a photo."

    def _get_camera(self) -> ZerobotCamera:
        if self._camera is None:
            self._camera = ZerobotCamera()
        return self._camera

    async def execute(
        self,
        action: str,
        filename: str | None = None,
        **kwargs: Any,
    ) -> str:
        if sys.platform != "linux":
            return f"Error: Camera tool is only supported on Linux (Raspberry Pi), but current OS is {sys.platform}."

        if not HAS_PICAMERA2:
            return "Error: 'python3-picamera2' library not found. Please install it with 'sudo apt install python3-picamera2'."

        try:
            cam = self._get_camera()
            
            if action == "capture":
                if not filename:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"capture_{timestamp}.jpg"
                
                # Ensure the filename has an extension
                if not filename.endswith((".jpg", ".png", ".jpeg")):
                    filename += ".jpg"

                if cam.capture_image(filename):
                    return f"Successfully captured image and saved to {filename}."
                else:
                    return "Failed to capture image."
            
            else:
                return f"Error: Unknown action '{action}'"

        except Exception as e:
            logger.exception("Camera tool error")
            return f"Error using camera: {str(e)}"

    def __del__(self):
        if self._camera:
            try:
                self._camera.close()
            except:
                pass
