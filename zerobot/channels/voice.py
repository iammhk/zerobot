# voice.py - Voice channel for local hardware interaction
# This channel handles recording audio from a mic and playing back agent responses.

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any

from loguru import logger

from zerobot.bus.events import InboundMessage, OutboundMessage
from zerobot.bus.queue import MessageBus
from zerobot.channels.base import BaseChannel
from zerobot.providers.transcription import SarvamTranscriptionProvider, OpenAITranscriptionProvider, GroqTranscriptionProvider
from zerobot.providers.tts import get_tts_provider
from zerobot.utils.audio import record_audio, play_audio

class VoiceChannel(BaseChannel):
    """
    Channel that uses local microphone and speakers.
    """

    @property
    def name(self) -> str:
        return "voice"

    @property
    def display_name(self) -> str:
        return "Voice"

    def __init__(self, config: Any, bus: MessageBus, **kwargs: Any):
        super().__init__(config, bus)
        self._listen_task: asyncio.Task | None = None
        self._is_listening = False
        self._temp_dir = Path(tempfile.gettempdir()) / "zerobot_voice"
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize STT provider (will be done in start to ensure keys are set)
        self.stt = None
        
        # We need the full config to get provider details
        self._global_config = kwargs.get("global_config")
        self.tts = None

    def _init_stt(self) -> Any:
        provider = self.transcription_provider
        key = self.transcription_api_key
        lang = self.transcription_language
        
        if provider == "sarvam":
            return SarvamTranscriptionProvider(api_key=key, language=lang)
        elif provider == "openai":
            return OpenAITranscriptionProvider(api_key=key, language=lang)
        elif provider == "groq":
            return GroqTranscriptionProvider(api_key=key, language=lang)
        return None

    async def start(self) -> None:
        """Start the voice listening loop."""
        if self._is_running:
            return
            
        self._is_running = True
        self._is_listening = True
        
        self.stt = self._init_stt()
        if self._global_config:
            self.tts = get_tts_provider(self._global_config)
            
        self._listen_task = asyncio.create_task(self._listen_loop())
        logger.info("Voice channel started (Always Listening mode)")

    async def stop(self) -> None:
        """Stop the voice listening loop."""
        self._is_running = False
        self._is_listening = False
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        logger.info("Voice channel stopped")

    async def _listen_loop(self) -> None:
        """
        Continuous listening loop.
        In a real implementation, this would use VAD.
        For this version, we'll use a simplified 'record chunk -> transcribe' approach.
        """
        chunk_idx = 0
        while self._is_listening:
            try:
                chunk_file = self._temp_dir / f"chunk_{chunk_idx}.wav"
                
                # Record a 5-second chunk (simulating VAD or simple interval)
                # In a better version, we'd wait for audio activity
                logger.debug("Listening...")
                success = await record_audio(chunk_file, duration=5)
                
                if success and chunk_file.exists():
                    # Transcribe
                    text = await self.stt.transcribe(chunk_file)
                    if text and text.strip():
                        logger.info("Voice Input: {}", text)
                        
                        # Send to bus
                        msg = InboundMessage(
                            channel=self.name,
                            sender_id="local_user",
                            chat_id="default",
                            content=text
                        )
                        await self.bus.publish_inbound(msg)
                    
                    # Clean up
                    os.remove(chunk_file)
                
                chunk_idx += 1
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in voice listen loop: {}", e)
                await asyncio.sleep(1)

    async def send(self, msg: OutboundMessage) -> None:
        """
        Handle outbound message by speaking it.
        """
        if not self.tts:
            # Try to lazy-init if we didn't have config before
            # This is a bit hacky but manager.py might not pass global_config
            logger.warning("TTS not initialized for voice channel")
            return

        logger.info("Speaking: {}", msg.content)
        
        output_file = self._temp_dir / "response.mp3"
        success = await self.tts.speak(msg.content, output_file)
        
        if success and output_file.exists():
            # Stop listening while playing to avoid feedback
            was_listening = self._is_listening
            self._is_listening = False
            
            await play_audio(output_file)
            
            self._is_listening = was_listening
            os.remove(output_file)
        else:
            logger.error("Failed to synthesize or play response")

    async def send_delta(self, chat_id: str, content: str, metadata: dict[str, Any]) -> None:
        """
        Voice channel doesn't support streaming audio well in this simple version.
        We wait for the end of the stream and play the whole message.
        """
        if metadata.get("_stream_end"):
            # The manager or loop usually sends the full content in the last delta or separately.
            # However, if we only get deltas, we'd need to buffer them.
            # For now, we assume standard 'send' will be used for final responses.
            pass
