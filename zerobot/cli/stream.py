"""Streaming renderer for CLI output.

Uses Rich Live with auto_refresh=False for stable, flicker-free
markdown rendering during streaming. Ellipsis mode handles overflow.
"""

from __future__ import annotations

import re
import sys
import time
from typing import Any

from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text

from zerobot import __logo__


def _make_console() -> Console:
    """Create a Console that emits plain text when stdout is not a TTY."""
    return Console(file=sys.stdout, force_terminal=sys.stdout.isatty())


class ThinkingSpinner:
    """Spinner that shows 'Zerobot is thinking...' with pause support."""

    def __init__(self, console: Console | None = None):
        c = console or _make_console()
        self._spinner = c.status("[grey50]Zerobot is thinking...[/grey50]", spinner="dots")
        self._active = False

    def __enter__(self):
        self._spinner.start()
        self._active = True
        return self

    def __exit__(self, *exc):
        self._active = False
        self._spinner.stop()
        return False

    def pause(self):
        """Context manager: temporarily stop spinner for clean output."""
        from contextlib import contextmanager

        @contextmanager
        def _ctx():
            if self._spinner and self._active:
                self._spinner.stop()
            try:
                yield
            finally:
                if self._spinner and self._active:
                    self._spinner.start()

        return _ctx()


class StreamRenderer:
    """Rich Live streaming with markdown. auto_refresh=False avoids render races.

    Deltas arrive pre-filtered (no <think> tags) from the agent loop.

    Flow per round:
      spinner -> first visible delta -> header + Live renders ->
      on_end -> Live stops (content stays on screen)
    """

    def __init__(self, render_markdown: bool = True, show_spinner: bool = True):
        self._md = render_markdown
        self._show_spinner = show_spinner
        self._buf = ""
        self._live: Live | None = None
        self._t = 0.0
        self.streamed = False
        self._spinner: ThinkingSpinner | None = None
        self._start_spinner()

    def _render(self):
        if not self._buf:
            return Text("")

        # Split the buffer into thought blocks and regular content.
        # We handle both closed <think>...</think> and open <think>... streaming blocks.
        parts = re.split(r"(<think>[\s\S]*?</think>|<think>[\s\S]*$)", self._buf)
        renderables = []

        for p in parts:
            if not p:
                continue
            if p.startswith("<think>"):
                content = p[7:]
                if content.endswith("</think>"):
                    content = content[:-8]
                content = content.strip()
                # Always provide at least a placeholder to avoid empty Text objects
                renderables.append(Text(f"💭 {content or '...'}\n", style="grey50 italic"))
            else:
                text_content = p.strip()
                if text_content:
                    renderables.append(Markdown(text_content) if self._md else Text(text_content))

        if not renderables:
            return Text("...", style="dim")
        if len(renderables) == 1:
            return renderables[0]
        return Group(*renderables)

    def _start_spinner(self) -> None:
        if self._show_spinner:
            self._spinner = ThinkingSpinner()
            self._spinner.__enter__()

    def _stop_spinner(self) -> None:
        if self._spinner:
            self._spinner.__exit__(None, None, None)
            self._spinner = None

    async def on_delta(self, delta: str) -> None:
        self.streamed = True
        self._buf += delta
        if self._live is None:
            if not self._buf.strip():
                return
            self._stop_spinner()
            c = _make_console()
            c.print()
            c.print(f"[grey50]{__logo__} Zerobot[/grey50]")
            self._live = Live(self._render(), console=c, auto_refresh=False)
            self._live.start()
        now = time.monotonic()
        if (now - self._t) > 0.1:
            self._live.update(self._render())
            self._live.refresh()
            self._t = now

    async def on_end(self, *, resuming: bool = False) -> None:
        if self._live:
            self._live.update(self._render())
            self._live.refresh()
            self._live.stop()
            self._live = None
        self._stop_spinner()
        if resuming:
            self._buf = ""
            self._start_spinner()
        else:
            _make_console().print()

    def stop_for_input(self) -> None:
        """Stop spinner before user input to avoid prompt_toolkit conflicts."""
        self._stop_spinner()

    async def close(self) -> None:
        """Stop spinner/live without rendering a final streamed round."""
        if self._live:
            self._live.stop()
            self._live = None
        self._stop_spinner()
