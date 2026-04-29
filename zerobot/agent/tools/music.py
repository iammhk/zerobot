# music.py - Music streaming tool for zerobot
# This file is used in the actual project to allow the agent to stream music from YouTube Music.

import asyncio
import shutil
import sys
from typing import Any
from loguru import logger

try:
    from ytmusicapi import YTMusic
except ImportError:
    # Fallback for when dependency is not yet installed
    YTMusic = None

from zerobot.agent.tools.base import Tool, tool_parameters
from zerobot.agent.tools.schema import StringSchema, tool_parameters_schema

@tool_parameters(
    tool_parameters_schema(
        action=StringSchema(
            "The music action to perform",
            enum=["search", "play", "stop", "pause", "resume"],
        ),
        query=StringSchema("The search query for 'search' or 'play' action"),
        video_id=StringSchema("The video ID or URL to play for 'play' action (optional if query is provided)"),
        required=["action"],
    )
)
class MusicTool(Tool):
    """Tool to search and stream music from YouTube Music using ytmusicapi and mpv."""

    def __init__(self):
        super().__init__()
        self._yt = None
        self._current_process = None

    @property
    def name(self) -> str:
        return "music"

    @property
    def description(self) -> str:
        return (
            "Search and stream music from YouTube Music. "
            "Actions: search (returns list of songs), play (starts streaming a video ID), stop (stops current playback). "
            "Requires 'mpv' and 'yt-dlp' to be installed on the system."
        )

    async def execute(
        self,
        action: str,
        query: str | None = None,
        video_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        if action == "search":
            if not query:
                return "Error: 'query' is required for search action."
            return await self._search(query)
        
        elif action == "play":
            if not video_id:
                if not query:
                    return "Error: 'video_id' or 'query' is required for play action."
                
                # Auto-search and play first result
                if self._yt is None:
                    if YTMusic is None:
                        return "Error: 'ytmusicapi' is not installed."
                    try:
                        self._yt = YTMusic()
                    except Exception as e:
                        return f"Error initializing YouTube Music API: {str(e)}"
                
                try:
                    # Using the same logic as _search to ensure it's robust
                    loop = asyncio.get_event_loop()
                    search_results = await loop.run_in_executor(None, lambda: self._yt.search(query, filter="songs"))
                    
                    if not search_results:
                        return f"No songs found for '{query}'"
                    video_id = search_results[0].get("videoId")
                    if not video_id:
                         return f"Could not find a valid video ID for '{query}'"
                except Exception as e:
                    return f"Error searching for '{query}': {str(e)}"
            
            return await self._play(video_id)
        
        elif action == "stop":
            return await self._stop()
        
        elif action == "pause":
            success = await self.set_pause(True)
            return "Music paused." if success else "Error: Could not pause music (is it playing?)"
        
        elif action == "resume":
            success = await self.set_pause(False)
            return "Music resumed." if success else "Error: Could not resume music (is it playing?)"
        
        return f"Error: Unknown action '{action}'"

    async def _search(self, query: str) -> str:
        if YTMusic is None:
            return "Error: 'ytmusicapi' is not installed. Please run 'uv sync' or install it manually."
            
        if self._yt is None:
            try:
                self._yt = YTMusic()
            except Exception as e:
                return f"Error initializing YouTube Music API: {str(e)}"
        
        try:
            # Using loop.run_in_executor since ytmusicapi is synchronous
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, lambda: self._yt.search(query, filter="songs"))
            
            if not results:
                return "No songs found for that query."
            
            lines = []
            for i, r in enumerate(results[:5]):
                title = r.get("title", "Unknown")
                artists = r.get("artists", [])
                artist_names = ", ".join([a.get("name", "Unknown") for a in artists])
                vid = r.get("videoId")
                lines.append(f"{i+1}. {title} by {artist_names} (ID: {vid})")
            
            return "Found the following songs:\n" + "\n".join(lines)
        except Exception as e:
            return f"Error searching YouTube Music: {str(e)}"

    async def _play(self, video_id: str) -> str:
        if not shutil.which("mpv"):
            return "Error: 'mpv' is not installed. Please install it (sudo apt install mpv)."

        # Kill any existing mpv processes (orphans or current)
        await self._cleanup_orphans()

        url = f"https://music.youtube.com/watch?v={video_id}"
        ipc_path = r"\\.\pipe\zerobot-mpv" if sys.platform == "win32" else "/tmp/zerobot-mpv"
        args = ["mpv", url, "--no-video", "--ytdl-format=bestaudio", "--no-terminal", f"--input-ipc-server={ipc_path}"]
        
        # On Windows, CREATE_NO_WINDOW prevents the process from interfering with the console
        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW

        try:
            self._current_process = await asyncio.create_subprocess_exec(
                *args,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                **kwargs
            )
            return f"Started playing music: {url}\n(Note: Buffering may take a few seconds)"
        except Exception as e:
            return f"Error starting playback: {str(e)}"

    async def set_ducking(self, active: bool) -> bool:
        """Lower the volume (ducking) when the agent is listening."""
        volume = 20 if active else 100
        return await self._send_ipc_command({"command": ["set_property", "volume", volume]})

    async def set_pause(self, pause: bool) -> bool:
        """Pause or resume the current mpv process via IPC."""
        return await self._send_ipc_command({"command": ["set_property", "pause", pause]})

    async def _send_ipc_command(self, cmd: dict) -> bool:
        """Send a command to the mpv process via IPC."""
        if not self._current_process or self._current_process.returncode is not None:
            return False

        ipc_path = r"\\.\pipe\zerobot-mpv" if sys.platform == "win32" else "/tmp/zerobot-mpv"
        import json
        
        try:
            if sys.platform == "win32":
                # Writing to named pipes on Windows can be tricky with simple open()
                # especially if mpv is still starting up.
                with open(ipc_path, 'w', encoding='ascii') as f:
                    f.write(json.dumps(cmd) + "\n")
            else:
                # Unix socket
                reader, writer = await asyncio.open_unix_connection(ipc_path)
                writer.write((json.dumps(cmd) + "\n").encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            return True
        except Exception as e:
            logger.debug("Failed to send mpv IPC command: {}", e)
            return False

    async def _stop(self) -> str:
        if self._current_process and self._current_process.returncode is None:
            try:
                await self._cleanup_orphans()
                self._current_process = None
                return "Playback stopped."
            except Exception as e:
                return f"Error stopping playback: {str(e)}"
        
        # Even if we don't have a tracked process, try to cleanup any orphans
        await self._cleanup_orphans()
        self._current_process = None
        return "No music is currently playing."

    async def _cleanup_orphans(self) -> None:
        """Forcefully kill any running mpv processes and their children."""
        try:
            if sys.platform == "win32":
                import subprocess as sp
                # Kill mpv.exe and mpv.com (and all children like yt-dlp)
                for img in ["mpv.exe", "mpv.com"]:
                    sp.run(["taskkill", "/F", "/IM", img, "/T"], 
                           stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            else:
                import subprocess as sp
                sp.run(["pkill", "-9", "mpv"], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        except Exception as e:
            logger.debug("Orphan cleanup failed: {}", e)
