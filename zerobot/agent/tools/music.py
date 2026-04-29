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
        query=StringSchema("The search query for 'search' action"),
        video_id=StringSchema("The video ID or URL to play for 'play' action"),
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
                return "Error: 'video_id' is required for play action."
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

        # Stop existing playback first
        await self._stop()

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
            return f"Started playing music from YouTube: {url}"
        except Exception as e:
            return f"Error starting playback: {str(e)}"

    async def set_ducking(self, active: bool) -> bool:
        """Lower the volume (ducking) when the agent is listening."""
        if not self._current_process or self._current_process.returncode is not None:
            return False

        volume = 20 if active else 100
        ipc_path = r"\\.\pipe\zerobot-mpv" if sys.platform == "win32" else "/tmp/zerobot-mpv"
        
        import json
        cmd = {"command": ["set_property", "volume", volume]}
        
        try:
            if sys.platform == "win32":
                # Use powershell to write to the named pipe safely
                import subprocess as sp
                payload = json.dumps(cmd).replace('"', '\"')
                ps_cmd = f"echo '{payload}' | Out-File -FilePath {ipc_path} -Encoding ascii"
                # Actually, a simpler way in Python:
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
            logger.debug(f"Failed to set mpv volume via IPC: {e}")
            return False

    async def set_pause(self, pause: bool) -> bool:
        """Pause or resume the current mpv process via IPC."""
        if not self._current_process or self._current_process.returncode is not None:
            return False

        ipc_path = r"\\.\pipe\zerobot-mpv" if sys.platform == "win32" else "/tmp/zerobot-mpv"
        import json
        cmd = {"command": ["set_property", "pause", pause]}
        
        try:
            if sys.platform == "win32":
                with open(ipc_path, 'w', encoding='ascii') as f:
                    f.write(json.dumps(cmd) + "\n")
            else:
                reader, writer = await asyncio.open_unix_connection(ipc_path)
                writer.write((json.dumps(cmd) + "\n").encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            return True
        except Exception as e:
            logger.debug(f"Failed to set mpv pause state via IPC: {e}")
            return False

    async def _stop(self) -> str:
        if self._current_process and self._current_process.returncode is None:
            try:
                if sys.platform == "win32":
                    # On Windows, we use taskkill to ensure the process and its children (like yt-dlp) are stopped
                    import subprocess as sp
                    sp.run(["taskkill", "/F", "/T", "/PID", str(self._current_process.pid)], 
                           stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                else:
                    self._current_process.terminate()
                
                # Wait for the process to actually exit
                try:
                    await asyncio.wait_for(self._current_process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    if self._current_process.returncode is None:
                        self._current_process.kill()
                        await self._current_process.wait()
                
                self._current_process = None
                return "Playback stopped."
            except Exception as e:
                return f"Error stopping playback: {str(e)}"
        
        self._current_process = None
        return "No music is currently playing."
