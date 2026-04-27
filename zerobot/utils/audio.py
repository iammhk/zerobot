# audio.py - Audio utilities for zerobot
# This file is used to record and play audio using system commands like ffmpeg, arecord, and aplay.

import asyncio
import os
import shutil
import subprocess
from pathlib import Path
from loguru import logger

async def record_audio(output_path: str | Path, duration: float | None = None, device: str | None = None) -> bool:
    """
    Record audio from the microphone.
    
    Args:
        output_path: Where to save the recording.
        duration: Optional recording duration in seconds. If None, it records until interrupted.
        device: Optional ALSA device name (e.g. 'default' or 'hw:0,0').
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Try ffmpeg first
    if shutil.which("ffmpeg"):
        if os.name == "nt":  # Windows
            # On your machine, the mic is "Microphone Array (Realtek(R) Audio)"
            mic_name = device or "Microphone Array (Realtek(R) Audio)"
            cmd = ["ffmpeg", "-y", "-f", "dshow", "-i", f"audio={mic_name}", "-t", str(duration) if duration else "3600", str(output_path)]
        else:  # Linux/Other
            cmd = ["ffmpeg", "-y", "-f", "alsa", "-i", device or "default", "-t", str(duration) if duration else "3600", str(output_path)]
        logger.debug("Recording with ffmpeg: {}", " ".join(cmd))
    elif shutil.which("arecord"):
        # arecord -d <seconds> -f cd -t wav <file>
        cmd = ["arecord", "-f", "cd", "-t", "wav"]
        if duration:
            cmd.extend(["-d", str(int(duration))])
        if device:
            cmd.extend(["-D", device])
        cmd.append(str(output_path))
        logger.debug("Recording with arecord: {}", " ".join(cmd))
    else:
        logger.error("No recording utility found (ffmpeg or arecord)")
        return False

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE
        )
        
        if duration:
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                err = stderr.decode() if stderr else "Unknown error"
                logger.error("Recording failed (code {}): {}", process.returncode, err)
                return False
        else:
            # For indefinite recording, the caller should terminate the process
            return process
            
        return True
    except Exception as e:
        logger.error("Error during recording: {}", e)
        return False

async def play_system_sound(sound_name: str) -> bool:
    """
    Play a pre-generated system sound from assets/sounds.
    """
    assets_dir = Path(__file__).parent.parent / "assets" / "sounds"
    sound_path = assets_dir / f"{sound_name}.wav"
    
    if not sound_path.exists():
        logger.warning("System sound not found: {}", sound_name)
        return False
        
    return await play_audio(sound_path)

async def play_audio(file_path: str | Path, device: str | None = None) -> bool:
    """
    Play an audio file.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error("Audio file not found: {}", file_path)
        return False
        
    # Try ffplay first
    if shutil.which("ffplay"):
        cmd = ["ffplay", "-nodisp", "-autoexit", str(file_path)]
        logger.debug("Playing with ffplay: {}", " ".join(cmd))
    elif shutil.which("aplay"):
        cmd = ["aplay"]
        if device:
            cmd.extend(["-D", device])
        cmd.append(str(file_path))
        logger.debug("Playing with aplay: {}", " ".join(cmd))
    else:
        logger.error("No playback utility found (ffplay or aplay)")
        return False
        
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE
        )
        await process.wait()
        return process.returncode == 0
    except Exception as e:
        logger.error("Error during playback: {}", e)
        return False
