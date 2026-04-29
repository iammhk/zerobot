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
    
    label = "Listening..." if external else "Sleeping..."
    out += f"  {color}{label}{reset}"
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
    Pulsating animation that uses ANSI colors for external states (like Cloud STT/LLM).
    Works across Windows (VT100) and Linux/macOS.
    """

    FPS = 15

    def __init__(self) -> None:
        self._state = VoiceState.IDLE
        self._external = False
        self._task: asyncio.Task | None = None
        self._last_len = 0
        self._win32_vt100_last_check = 0
        
    def _ensure_win32_vt100(self) -> None:
        """Forcefully enable VT100/ANSI support on Windows 10+ raw handles."""
        if sys.platform != "win32":
            return
            
        # Only check/re-enable every 2 seconds to avoid overhead
        now = time.monotonic()
        if now - self._win32_vt100_last_check < 2.0:
            return
        self._win32_vt100_last_check = now

        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Handles: -11 (stdout), -12 (stderr)
            for handle_id in [-11, -12]:
                h = kernel32.GetStdHandle(handle_id)
                if h and h != -1:
                    mode = ctypes.c_ulong()
                    if kernel32.GetConsoleMode(h, ctypes.byref(mode)):
                        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                        # ENABLE_PROCESSED_OUTPUT = 0x0001
                        new_mode = mode.value | 0x0004 | 0x0001
                        kernel32.SetConsoleMode(h, new_mode)
        except Exception:
            pass

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
                self._ensure_win32_vt100()
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
        # Use sys.__stderr__ to bypass any stdout/stderr patching (e.g. from prompt_toolkit)
        # and write directly to the original terminal stream.
        target = sys.__stderr__ or sys.stderr
        try:
            target.write("\r" + s + " " * max(0, self._last_len - len(s)))
            target.flush()
        except Exception:
            pass
        self._last_len = len(s)
