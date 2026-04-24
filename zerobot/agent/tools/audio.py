# audio.py - Audio management tool for zerobot
# This file is used in the actual project to allow the agent to manage audio sinks and sources.

import asyncio
import shutil
import sys
from typing import Any

from zerobot.agent.tools.base import Tool, tool_parameters
from zerobot.agent.tools.schema import StringSchema, tool_parameters_schema


@tool_parameters(
    tool_parameters_schema(
        action=StringSchema(
            "The audio action to perform",
            enum=["list_sinks", "list_sources", "set_output", "set_input", "volume"],
        ),
        name=StringSchema("The name or index of the sink/source (required for set_output, set_input, volume)"),
        value=StringSchema("The volume level (0-100) or toggle (optional for volume action)"),
        required=["action"],
    )
)
class AudioTool(Tool):
    """Tool to manage audio sinks and sources using pactl (PulseAudio/PipeWire)."""

    @property
    def name(self) -> str:
        return "audio"

    @property
    def description(self) -> str:
        return (
            "Manage audio input and output devices on the Raspberry Pi. "
            "Actions: list_sinks (speakers), list_sources (microphones), set_output (set default speaker), set_input (set default mic), volume (set volume 0-100). "
            "Use the 'name' field from the list results to set or adjust devices."
        )

    async def execute(
        self,
        action: str,
        name: str | None = None,
        value: str | None = None,
        **kwargs: Any,
    ) -> str:
        if sys.platform != "linux":
            return f"Error: Audio tool is only supported on Linux, but current OS is {sys.platform}."

        if not shutil.which("pactl"):
            return "Error: 'pactl' command not found. Please install pulseaudio-utils or pipewire-audio-client-libraries."

        try:
            if action == "list_sinks":
                return await self._run_command("list sinks short")
            elif action == "list_sources":
                return await self._run_command("list sources short")
            elif action == "set_output":
                if not name: return "Error: 'name' is required for set_output."
                return await self._run_command(f"set-default-sink {name}")
            elif action == "set_input":
                if not name: return "Error: 'name' is required for set_input."
                return await self._run_command(f"set-default-source {name}")
            elif action == "volume":
                if not name or not value: return "Error: 'name' and 'value' (0-100) are required for volume."
                return await self._run_command(f"set-sink-volume {name} {value}%")
            else:
                return f"Error: Unknown action '{action}'"
        except Exception as e:
            return f"Error executing audio action: {str(e)}"

    async def _run_command(self, cmd: str) -> str:
        """Run a pactl command and return output."""
        full_cmd = f"pactl {cmd}"
        process = await asyncio.create_subprocess_shell(
            full_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        
        output = stdout.decode().strip()
        err = stderr.decode().strip()
        
        if process.returncode != 0:
            return f"Error: {err or output or 'Command failed'}"
        
        return output or "Success"
