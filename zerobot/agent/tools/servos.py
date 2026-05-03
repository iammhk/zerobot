# servos.py - Servo management tool for zerobot
# This file is used in the actual project to allow the agent to control servos via the Waveshare HAT.

import sys
from typing import Any

from loguru import logger

from zerobot.agent.tools.base import Tool, tool_parameters
from zerobot.agent.tools.schema import IntegerSchema, NumberSchema, StringSchema, tool_parameters_schema
from zerobot.utils.pca9685 import PCA9685, ServoHelper


@tool_parameters(
    tool_parameters_schema(
        action=StringSchema(
            "The servo action to perform",
            enum=["move", "release", "set_pwm", "center", "sequence"],
        ),
        channel=IntegerSchema("The servo channel (0-15)", minimum=0, maximum=15),
        angle=NumberSchema("Angle in degrees (0-180) for 'move' action", nullable=True),
        sequence=StringSchema("The name of the movement sequence (e.g., 'wave', 'dance') for 'sequence' action", nullable=True),
        pulse=IntegerSchema("Raw pulse width in microseconds for 'set_pwm' action", nullable=True),
        required=["action", "channel"],
    )
)
class ServoTool(Tool):
    """Tool to control servos on the Waveshare Servo Driver HAT."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pca = None
        self._helper = None

    @property
    def name(self) -> str:
        return "servos"

    @property
    def description(self) -> str:
        return (
            "Control servos connected to the Waveshare Servo Driver HAT. "
            "Actions: move (to angle), release (stop power), center (move to 90), set_pwm (raw pulse), "
            "sequence (run a pre-defined movement script like 'wave' or 'dance'). "
            "Channels range from 0 to 15 (ignored for 'sequence')."
        )

    def _get_helper(self) -> ServoHelper:
        """Lazy initialization of the driver."""
        if self._helper is None:
            self._pca = PCA9685()
            self._helper = ServoHelper(self._pca)
        return self._helper

    async def execute(
        self,
        action: str,
        channel: int,
        angle: float | None = None,
        pulse: int | None = None,
        sequence: str | None = None,
        **kwargs: Any,
    ) -> str:
        if sys.platform != "linux":
            return f"Error: Servo tool is only supported on Linux (Raspberry Pi), but current OS is {sys.platform}."

        try:
            helper = self._get_helper()
            
            if action == "move":
                if angle is None:
                    return "Error: Action 'move' requires an 'angle'."
                helper.set_angle(channel, angle)
                return f"Moved servo on channel {channel} to {angle} degrees."
            
            elif action == "center":
                helper.set_angle(channel, 90)
                return f"Centered servo on channel {channel} (90 degrees)."
            
            elif action == "release":
                helper.release(channel)
                return f"Released servo on channel {channel} (power off)."
            
            elif action == "set_pwm":
                if pulse is None:
                    return "Error: Action 'set_pwm' requires a 'pulse' (microseconds)."
                helper.set_pulse(channel, pulse)
                return f"Set servo on channel {channel} to raw pulse {pulse}us."
            
            elif action == "sequence":
                if not sequence:
                    return "Error: Action 'sequence' requires a 'sequence' name."
                
                import subprocess
                import os
                
                # Try to find the script
                # We assume the scripts are in a 'scripts' folder in the root of the workspace
                # This is a bit of a hack, we should ideally have a better path discovery
                possible_paths = [
                    os.path.abspath(os.path.join(os.getcwd(), "scripts", f"mvmt_{sequence}.py")),
                    os.path.abspath(os.path.join(os.getcwd(), "..", "scripts", f"mvmt_{sequence}.py")), # If running from zerobot/
                ]
                
                script_path = None
                for p in possible_paths:
                    if os.path.exists(p):
                        script_path = p
                        break
                
                if not script_path:
                    return f"Error: Movement sequence '{sequence}' not found (tried {possible_paths})."
                
                logger.info(f"Running movement sequence: {sequence} via {script_path}")
                # We run this in the background or wait for it? 
                # Benchmarks showed it takes a few seconds. We'll wait.
                try:
                    # We need to make sure the I2C bus is not held by the tool if possible
                    # but our tool uses lazy init and doesn't hold the bus open between calls
                    # unless it's in the middle of this execute call.
                    subprocess.run([sys.executable, script_path], check=True, capture_output=True, text=True)
                    return f"Successfully executed movement sequence '{sequence}'."
                except subprocess.CalledProcessError as e:
                    return f"Error executing movement sequence '{sequence}': {e.stderr}"
            
            else:
                return f"Error: Unknown action '{action}'"

        except Exception as e:
            logger.exception("Servo tool error")
            return f"Error controlling servo: {str(e)}"

    def __del__(self):
        if self._pca:
            try:
                self._pca.close()
            except:
                pass
