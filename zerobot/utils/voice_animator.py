# voice_animator.py - High-compatibility monochrome voice animation for Zerobot.
# Bypasses all color codes to ensure zero "garbage text" in older Windows terminals.

import asyncio
import math
import sys
import time
from enum import Enum

_BLUE = "\033[94m"
_RESET = "\033[0m"

class VoiceState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"


# ── Frame renderers (Monochrome) ────────────────────────────────────────────

_BARS = " ▁▂▃▄▅▆▇█"

def _listening_frame(t: float, external: bool = False) -> str:
    bars = 13
    center = bars // 2
    out = "🎤  "
    color = _BLUE if external else ""
    reset = _RESET if external else ""
    for i in range(bars):
        dist = abs(i - center)
        phase = (t * 4) - dist * 0.5
        raw = (math.sin(phase) + 1) / 2
        amplitude = max(0.0, 1.0 - dist / (center + 1)) ** 1.2
        idx = int(raw * amplitude * (len(_BARS) - 1))
        out += _BARS[idx]
    out += f"  {color}Listening...{reset}"
    return out


def _thinking_frame(t: float, external: bool = False) -> str:
    out = "🧠  "
    color = _BLUE if external else ""
    reset = _RESET if external else ""
    for i in range(5):
        phase = (t * 3) + i * (math.pi / 2.5)
        val = (math.sin(phase) + 1) / 2
        out += "● " if val > 0.5 else "○ "
    out += f" {color}Thinking...{reset}"
    return out


_WAVE_CHARS = "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁ "

def _speaking_frame(t: float) -> str:
    width = 17
    out = "🔊  "
    for i in range(width):
        phase = (t * 5) + i * 0.6
        val = (math.sin(phase) + 1) / 2
        idx = int(val * (len(_WAVE_CHARS) - 1))
        out += _WAVE_CHARS[idx]
    out += "  Speaking..."
    return out


# ── VoiceAnimator ────────────────────────────────────────────────────────────

class VoiceAnimator:
    """
    Monochrome pulsating animation that works in any terminal.
    Uses only \r and spaces to overwrite lines — zero ANSI escape codes.
    """

    FPS = 15

    def __init__(self) -> None:
        self._state = VoiceState.IDLE
        self._external = False
        self._task: asyncio.Task | None = None
        self._last_len = 0
        
        # Enable ANSI escape codes on Windows (VT100 support)
        if sys.platform == "win32":
            try:
                import os
                import ctypes
                # Attempt to enable VT100 processing on Windows 10+
                kernel32 = ctypes.windll.kernel32
                # -11 is STD_OUTPUT_HANDLE, 7 is ENABLE_PROCESSED_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                # Also try -12 (STD_ERROR_HANDLE) since we write to stderr
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-12), 7)
            except Exception:
                # Fallback to os.system trick
                os.system('color')

    def set_state(self, state: VoiceState, external: bool = False) -> None:
        self._state = state
        self._external = external

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._state = VoiceState.IDLE
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        # Clear the line one last time
        self._write("")

    async def _run(self) -> None:
        while True:
            try:
                t = time.perf_counter()
                frame = self._render(t)
                self._write(frame)
                await asyncio.sleep(1 / self.FPS)
            except asyncio.CancelledError:
                break

    def _render(self, t: float) -> str:
        if self._state == VoiceState.LISTENING:
            return _listening_frame(t, self._external)
        elif self._state == VoiceState.THINKING:
            return _thinking_frame(t, self._external)
        elif self._state == VoiceState.SPEAKING:
            return _speaking_frame(t)
        return "💤  Voice idle"

    def _write(self, s: str) -> None:
        # 1. Start with \r to return to line beginning
        # 2. Pad with enough spaces to overwrite the previous line
        # 3. Write the new string
        # We use stderr to bypass prompt_toolkit's stdout interception
        sys.stderr.write("\r" + s + " " * max(0, self._last_len - len(s)))
        sys.stderr.flush()
        self._last_len = len(s)
