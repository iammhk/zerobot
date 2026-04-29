# voice.py - Voice channel for local hardware interaction
# This channel handles recording audio from a mic and playing back agent responses.
# Includes a pulsating terminal animation showing bot state (listening/thinking/speaking).

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
from zerobot.utils.audio import record_audio, play_audio, play_system_sound
from zerobot.utils.voice_animator import VoiceAnimator, VoiceState

try:
    import pyaudio
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False


class VoiceChannel(BaseChannel):
    """
    Channel that uses local microphone and speakers.
    Shows a live pulsating terminal animation for each voice state.
    """

    name = "voice"
    display_name = "Voice"

    def __init__(self, config: Any, bus: MessageBus, **kwargs: Any):
        super().__init__(config, bus)
        self._listen_task: asyncio.Task | None = None
        self._is_listening = False
        self._temp_dir = Path(tempfile.gettempdir()) / "zerobot_voice"
        self._temp_dir.mkdir(parents=True, exist_ok=True)

        self.stt = None
        self._global_config = kwargs.get("global_config")
        self.tts = None
        self._animator = VoiceAnimator()

    def _init_stt(self) -> Any:
        # Helper to get value from dict or object
        def get_val(cfg, key, default=None):
            if cfg is None: return default
            if isinstance(cfg, dict):
                from pydantic.alias_generators import to_camel
                return cfg.get(key, cfg.get(to_camel(key), default))
            return getattr(cfg, key, default)

        provider = get_val(self.config, "transcription_provider", "sarvam")
        key = get_val(self.config, "transcription_api_key", "")
        lang = get_val(self.config, "transcription_language", "en-IN")

        if not key and self._global_config:
            if provider == "sarvam":
                key = self._global_config.providers.sarvam.api_key
            elif provider == "openai":
                key = self._global_config.providers.openai.api_key
            elif provider == "groq":
                key = self._global_config.providers.groq.api_key

        if provider == "sarvam":
            return SarvamTranscriptionProvider(api_key=key, language=lang)
        elif provider == "openai":
            return OpenAITranscriptionProvider(api_key=key, language=lang)
        elif provider == "groq":
            return GroqTranscriptionProvider(api_key=key, language=lang)
        return None

    async def start(self) -> None:
        """Start the voice listening loop."""
        if self._running:
            return

        self._running = True
        self._is_listening = True

        self.stt = self._init_stt()
        if self._global_config:
            self.tts = get_tts_provider(self._global_config, channel_config=self.config)

        await play_system_sound("hello")
        await self._animator.start()
        self._animator.set_state(VoiceState.LISTENING)

        self._listen_task = asyncio.create_task(self._listen_loop())
        wake_word = self.config.get("wake_word")
        if wake_word:
            logger.info(f"Voice channel started (Wake Word: '{wake_word}')")
        else:
            logger.info("Voice channel started (Always Listening mode)")

    async def stop(self) -> None:
        """Stop the voice listening loop."""
        self._running = False
        self._is_listening = False
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        await self._animator.stop()
        await play_system_sound("goodbye")
        logger.info("Voice channel stopped")

    async def _listen_loop(self) -> None:
        """
        Voice listening loop with local wake-word detection (Vosk).
        1. Monitors mic locally for the wake word.
        2. Once detected, records a command and sends it to the cloud STT.
        """
        import time
        import json
        import re

        wake_word = self.config.get("wake_word")
        if wake_word:
            wake_word = wake_word.lower().strip()

        # Check if local wake word detection is possible
        use_local_wake = VOSK_AVAILABLE and wake_word
        model = None
        if use_local_wake:
            model_path = Path("zerobot/assets/models/vosk-model-small-en-us-0.15")
            if not model_path.exists():
                logger.warning("Vosk model not found at {}. Falling back to Always Listening mode.", model_path)
                use_local_wake = False
            else:
                try:
                    model = Model(str(model_path))
                    logger.info("Local wake-word detection enabled (Vosk)")
                except Exception as e:
                    logger.error("Failed to load Vosk model: {}. Falling back.", e)
                    use_local_wake = False

        chunk_idx = 0
        while self._running:
            try:
                if not self._is_listening:
                    await asyncio.sleep(0.5)
                    continue

                if use_local_wake:
                    # --- STAGE 1: LOCAL WAKE WORD DETECTION ---
                    self._animator.set_state(VoiceState.LISTENING)
                    logger.debug("Waiting for wake word: '{}'...", wake_word)
                    
                    p = pyaudio.PyAudio()
                    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
                    rec = KaldiRecognizer(model, 16000, f'["{wake_word}", "[unk]"]')
                    
                    found_wake = False
                    while self._running and self._is_listening:
                        # Non-blocking read (asyncio friendly)
                        data = await asyncio.get_event_loop().run_in_executor(None, stream.read, 4000, False)
                        if len(data) == 0:
                            break
                        if rec.AcceptWaveform(data):
                            res = json.loads(rec.Result())
                            if res.get("text") == wake_word:
                                found_wake = True
                                break
                        else:
                            # Check partial results for faster feedback if needed
                            pass
                        await asyncio.sleep(0.01)

                    stream.stop_stream()
                    stream.close()
                    p.terminate()

                    if not found_wake:
                        continue
                    
                    logger.info("Wake word detected locally!")
                    await play_system_sound("success")

                # --- STAGE 2: COMMAND RECORDING (CLOUD STT) ---
                chunk_file = self._temp_dir / f"chunk_{chunk_idx}.wav"

                # Record a 5-second command chunk
                self._animator.set_state(VoiceState.LISTENING)
                logger.debug("Listening for command...")
                success = await record_audio(chunk_file, duration=5)

                if not self._is_listening:
                    if chunk_file.exists(): os.remove(chunk_file)
                    continue

                if success and chunk_file.exists():
                    self._animator.set_state(VoiceState.THINKING)
                    start_stt = time.perf_counter()
                    text = await self.stt.transcribe(chunk_file) if self.stt else ""
                    stt_duration = time.perf_counter() - start_stt

                    if text and text.strip():
                        logger.info("Voice Command (STT: {:.2f}s): {}", stt_duration, text)
                        await play_system_sound("success")
                        
                        msg = InboundMessage(
                            channel=self.name,
                            sender_id="local_user",
                            chat_id="default",
                            content=text,
                            metadata={
                                "_stt_time": stt_duration,
                                "_input_timestamp": time.perf_counter(),
                            }
                        )
                        await self.bus.publish_inbound(msg)
                    else:
                        logger.debug("No command heard after wake word.")
                        self._animator.set_state(VoiceState.LISTENING)

                    os.remove(chunk_file)

                chunk_idx += 1
                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in voice listen loop")
                self._animator.set_state(VoiceState.LISTENING)
                await play_system_sound("error")
                await asyncio.sleep(1)

    async def send(self, msg: OutboundMessage) -> None:
        """Handle outbound message by speaking it with TTS."""
        import time
        if not self.tts:
            logger.warning("TTS not initialized for voice channel")
            return

        logger.info("Synthesizing: {}", msg.content)
        await play_system_sound("thinking")
        self._animator.set_state(VoiceState.THINKING)

        output_file = self._temp_dir / "response.mp3"
        start_tts = time.perf_counter()
        success = await self.tts.speak(msg.content, output_file)
        tts_duration = time.perf_counter() - start_tts

        if success and output_file.exists():
            # Pause listening during playback to avoid feedback
            was_listening = self._is_listening
            self._is_listening = False
            self._animator.set_state(VoiceState.SPEAKING)

            input_ts = msg.metadata.get("_input_timestamp")
            if input_ts:
                total_latency = time.perf_counter() - input_ts
                logger.info(
                    "Bot Speaking (TTS: {:.2f}s, Total V2V Latency: {:.2f}s)",
                    tts_duration, total_latency,
                )
            else:
                logger.info("Bot Speaking (TTS: {:.2f}s)", tts_duration)

            await play_audio(output_file)

            self._is_listening = was_listening
            self._animator.set_state(VoiceState.LISTENING)
            os.remove(output_file)
        else:
            logger.error("Failed to synthesize or play response")
            self._animator.set_state(VoiceState.LISTENING)

    async def send_delta(self, chat_id: str, content: str, metadata: dict[str, Any]) -> None:
        """Voice channel doesn't support streaming; waits for full message via send()."""
        if metadata.get("_stream_end"):
            pass
