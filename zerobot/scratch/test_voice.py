# test_voice.py - Test script for voice chat components
# This file is used to verify that the new voice-related modules can be imported and initialized.

import asyncio
from zerobot.providers.transcription import SarvamTranscriptionProvider
from zerobot.providers.tts import SarvamTTSProvider
from zerobot.utils.audio import record_audio, play_audio

async def main():
    print("Testing imports and initialization...")
    
    # Test STT
    stt = SarvamTranscriptionProvider(api_key="test_key")
    print(f"STT Provider initialized: {stt.api_url}")
    
    # Test TTS
    tts = SarvamTTSProvider(api_key="test_key")
    print(f"TTS Provider initialized: {tts.api_url}")
    
    print("Testing audio utilities presence...")
    import shutil
    print(f"ffmpeg found: {bool(shutil.which('ffmpeg'))}")
    print(f"ffplay found: {bool(shutil.which('ffplay'))}")
    print(f"arecord found: {bool(shutil.which('arecord'))}")
    print(f"aplay found: {bool(shutil.which('aplay'))}")

if __name__ == "__main__":
    asyncio.run(main())
