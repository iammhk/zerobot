# reactive.py - Reactive command routing for zerobot
# This file is used in the actual project to handle simple, high-frequency natural language commands locally.

import re
from typing import Any, Dict, List, Optional, Tuple, Callable, Awaitable
from loguru import logger

from zerobot.bus.events import InboundMessage, OutboundMessage
from zerobot.agent.tools.registry import ToolRegistry

class ReactiveRouter:
    """
    Matches user input against simple patterns to execute tool calls directly,
    bypassing the LLM loop for speed and efficiency on low-power hardware.
    """

    def __init__(self, tools: ToolRegistry):
        self.tools = tools
        # Patterns map to (tool_name, tool_args_factory)
        # tool_args_factory is a callable that takes the match object and returns a dict of args
        self._patterns: List[Tuple[re.Pattern, str, Callable[[re.Match], Dict[str, Any]]]] = []
        self._register_defaults()

    def _register_defaults(self):
        """Register default reactive movement and control patterns."""
        
        # Stop everything
        self.add_pattern(
            r"^(stop|halt|freeze)$",
            "servos",
            lambda m: {"action": "release", "channel": 0} # We'll need a better way to release all
        )
        
        # Center everything
        self.add_pattern(
            r"^(center|reset servos|straighten)$",
            "servos",
            lambda m: {"action": "center", "channel": 0}
        )

        # Simple movement (placeholders for common robot patterns)
        # Note: In a real scenario, these would map to multiple servo calls or a 'drive' tool
        self.add_pattern(
            r"^(move|go) forward$",
            "servos",
            lambda m: {"action": "move", "channel": 0, "angle": 180} # Example: channel 0 is forward
        )
        
        self.add_pattern(
            r"^(move|go) (back|backward|backwards)$",
            "servos",
            lambda m: {"action": "move", "channel": 0, "angle": 0} # Example: channel 0 is backward
        )

        self.add_pattern(
            r"^turn left$",
            "servos",
            lambda m: {"action": "move", "channel": 1, "angle": 0} # Example: channel 1 is steering
        )
        
        self.add_pattern(
            r"^turn right$",
            "servos",
            lambda m: {"action": "move", "channel": 1, "angle": 180}
        )

    def add_pattern(self, pattern: str, tool_name: str, args_factory: Callable[[re.Match], Dict[str, Any]]):
        """Add a new reactive pattern mapping."""
        self._patterns.append((re.compile(pattern, re.IGNORECASE), tool_name, args_factory))

    async def match_and_execute(self, msg: InboundMessage) -> Optional[OutboundMessage]:
        """
        Check if the message matches any reactive pattern.
        If so, execute the tool call and return an OutboundMessage.
        """
        text = msg.content.strip()
        if not text:
            return None

        for pattern, tool_name, args_factory in self._patterns:
            match = pattern.match(text)
            if match:
                logger.info(f"Reactive match found for '{text}': triggering {tool_name}")
                tool = self.tools.get(tool_name)
                if not tool:
                    logger.warning(f"Reactive match triggered tool '{tool_name}' which is not registered.")
                    return None
                
                try:
                    args = args_factory(match)
                    result = await tool.execute(**args)
                    
                    return OutboundMessage(
                        channel=msg.channel,
                        chat_id=msg.chat_id,
                        content=f"⚡ [Reactive] {result}",
                        metadata={**dict(msg.metadata or {}), "reactive": True}
                    )
                except Exception as e:
                    logger.error(f"Error executing reactive tool call '{tool_name}': {e}")
                    return OutboundMessage(
                        channel=msg.channel,
                        chat_id=msg.chat_id,
                        content=f"Error executing reactive command: {e}",
                    )
        
        return None
