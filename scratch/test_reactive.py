# test_reactive.py - Test for Reactive Path logic
# This script verifies that the ReactiveRouter correctly intercepts and executes simple commands.

import asyncio
import sys
from unittest.mock import MagicMock, AsyncMock

# Mock smbus2 and PCA9685 to avoid hardware errors
sys.modules['smbus2'] = MagicMock()

from zerobot.agent.reactive import ReactiveRouter
from zerobot.agent.tools.registry import ToolRegistry
from zerobot.bus.events import InboundMessage
from zerobot.agent.tools.servos import ServoTool

async def test_reactive_path():
    print("Testing Reactive Path...")
    
    # Setup tools with mock ServoTool
    tools = ToolRegistry()
    mock_servo_tool = MagicMock(spec=ServoTool)
    mock_servo_tool.name = "servos"
    mock_servo_tool.execute = AsyncMock(return_value="Mocked servo movement success")
    tools.register(mock_servo_tool)
    
    # Initialize ReactiveRouter
    reactive = ReactiveRouter(tools)
    
    # Test 1: "Move Forward"
    print("Test 1: 'Move Forward'")
    msg = InboundMessage(
        channel="cli",
        chat_id="direct",
        sender_id="user",
        content="Move Forward"
    )
    
    response = await reactive.match_and_execute(msg)
    assert response is not None
    assert "Mocked servo movement success" in response.content
    assert response.metadata.get("reactive") is True
    # Verify the tool was called with expected arguments for 'forward'
    # Default 'forward' mapping in reactive.py: {"action": "move", "channel": 0, "angle": 180}
    mock_servo_tool.execute.assert_called_with(action="move", channel=0, angle=180)
    print("OK: 'Move Forward' intercepted and executed correctly.")
    
    # Test 2: "Stop"
    print("Test 2: 'Stop'")
    msg.content = "Stop"
    mock_servo_tool.execute.reset_mock()
    response = await reactive.match_and_execute(msg)
    assert response is not None
    mock_servo_tool.execute.assert_called_with(action="release", channel=0)
    print("OK: 'Stop' intercepted and executed correctly.")
    
    # Test 3: Complex message (should NOT match)
    print("Test 3: Complex message")
    msg.content = "Can you help me write a python script?"
    response = await reactive.match_and_execute(msg)
    assert response is None
    print("OK: Complex message ignored by Reactive Path.")

    print("\nReactive Path tests passed!")

if __name__ == "__main__":
    asyncio.run(test_reactive_path())
