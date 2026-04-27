# bluetooth.py - Bluetooth management tool for zerobot
# This file is used in the actual project to allow the agent to manage Bluetooth devices.

import asyncio
import re
import shutil
import sys
from typing import Any

from loguru import logger

from zerobot.agent.tools.base import Tool, tool_parameters
from zerobot.agent.tools.schema import StringSchema, tool_parameters_schema


@tool_parameters(
    tool_parameters_schema(
        action=StringSchema(
            "The bluetooth action to perform",
            enum=["scan", "pair", "trust", "connect", "disconnect", "list", "paired", "info"],
        ),
        mac_address=StringSchema("The MAC address of the device (optional for scan/list/paired)"),
        timeout=StringSchema("Scan timeout in seconds (default '10')", nullable=True),
        required=["action"],
    )
)
class BluetoothTool(Tool):
    """Tool to manage bluetooth devices using bluetoothctl."""

    @property
    def name(self) -> str:
        return "bluetooth"

    @property
    def description(self) -> str:
        return (
            "Manage bluetooth devices on the Raspberry Pi. "
            "Use 'scan' to find nearby devices. "
            "Use 'info' with a mac_address to see the device name, pairing status, and signal strength. "
            "Actions: scan, pair, trust, connect, disconnect, list (known), paired, info (details)."
        )

    async def execute(
        self,
        action: str,
        mac_address: str | None = None,
        timeout: str | None = "10",
        **kwargs: Any,
    ) -> str:
        if sys.platform != "linux":
            return f"Error: Bluetooth tool is only supported on Linux (Raspberry Pi), but current OS is {sys.platform}."

        if not shutil.which("bluetoothctl"):
            return "Error: 'bluetoothctl' command not found. Please install bluez."

        if action in ["pair", "trust", "connect", "disconnect", "info"] and not mac_address:
            return f"Error: Action '{action}' requires a mac_address."

        try:
            if action == "scan":
                return await self._run_scan(timeout or "10")
            elif action == "list":
                return await self._run_command("devices")
            elif action == "paired":
                return await self._run_command("paired-devices")
            elif action == "pair":
                return await self._run_command(f"pair {mac_address}")
            elif action == "trust":
                return await self._run_command(f"trust {mac_address}")
            elif action == "connect":
                return await self._run_command(f"connect {mac_address}")
            elif action == "disconnect":
                return await self._run_command(f"disconnect {mac_address}")
            elif action == "info":
                return await self._run_command(f"info {mac_address}")
            else:
                return f"Error: Unknown action '{action}'"
        except Exception as e:
            return f"Error executing bluetooth action: {str(e)}"

    async def _run_command(self, cmd: str) -> str:
        """Run a bluetoothctl command and return output."""
        full_cmd = f"bluetoothctl {cmd}"
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
        
        return output or "Success (no output)"

    async def _run_scan(self, timeout_sec: str) -> str:
        """Run a bluetooth scan for a limited time."""
        # bluetoothctl scan on runs indefinitely, so we must kill it
        logger.info("Starting bluetooth scan for {}s", timeout_sec)
        
        # We use a subshell to run 'scan on' and then 'scan off' after delay
        # But a better way is to run 'scan on' and then cancel the task
        try:
            # We use --timeout which is supported in newer bluez, otherwise we kill it
            cmd = f"bluetoothctl --timeout {timeout_sec} scan on"
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Wait for scan to finish
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=float(timeout_sec) + 5)
            
            # Now list devices - this will include names for discovered devices
            devices = await self._run_command("devices")
            
            if not devices or "No devices found" in devices:
                return "Scan completed, but no devices were found. Ensure your target device is in pairing mode."
                
            return f"Scan completed. Here are the discovered devices (MAC Address followed by Name):\n\n{devices}"
        except asyncio.TimeoutError:
            process.kill()
            return "Error: Scan timed out without returning results."
