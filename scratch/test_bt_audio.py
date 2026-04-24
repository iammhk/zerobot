# test_bt_audio.py - Test script for Bluetooth and Audio tools
# This file is used to verify that the tools correctly handle command execution and output.

import asyncio
import sys
from unittest.mock import MagicMock, patch, AsyncMock

# Mock sys.platform to linux so the tools don't error out early
sys.platform = "linux"

from zerobot.agent.tools.bluetooth import BluetoothTool
from zerobot.agent.tools.audio import AudioTool

async def test_bluetooth():
    print("Testing BluetoothTool...")
    tool = BluetoothTool()
    
    # Mock shutil.which to find bluetoothctl
    with patch("shutil.which", return_value="/usr/bin/bluetoothctl"):
        # Mock create_subprocess_shell to return an AsyncMock for the process
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"Device AA:BB:CC:DD:EE:FF Sony Headphones\n", b"")
        mock_process.returncode = 0
        
        with patch("asyncio.create_subprocess_shell", return_value=mock_process):
            # Test 'list'
            result = await tool.execute(action="list")
            print(f"List result: {result}")
            assert "AA:BB:CC:DD:EE:FF" in result

            # Test 'connect'
            mock_process.communicate.return_value = (b"Connection successful\n", b"")
            result = await tool.execute(action="connect", mac_address="AA:BB:CC:DD:EE:FF")
            print(f"Connect result: {result}")
            assert "successful" in result

async def test_audio():
    print("\nTesting AudioTool...")
    tool = AudioTool()
    
    # Mock shutil.which to find pactl
    with patch("shutil.which", return_value="/usr/bin/pactl"):
        # Mock create_subprocess_shell
        mock_process = AsyncMock()
        mock_process.communicate.return_value = (b"0\talsa_output.pci-0000_00_1b.0.analog-stereo\tmodule-alsa-card.c\ts16le 2ch 44100Hz\tSUSPENDED\n", b"")
        mock_process.returncode = 0
        
        with patch("asyncio.create_subprocess_shell", return_value=mock_process):
            # Test 'list_sinks'
            result = await tool.execute(action="list_sinks")
            print(f"List sinks result: {result}")
            assert "alsa_output" in result

            # Test 'set_output'
            mock_process.communicate.return_value = (b"", b"")
            result = await tool.execute(action="set_output", name="0")
            print(f"Set output result: {result}")
            assert "Success" in result

if __name__ == "__main__":
    asyncio.run(test_bluetooth())
    asyncio.run(test_audio())
