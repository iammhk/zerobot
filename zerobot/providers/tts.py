# tts.py - Text-to-Speech providers for zerobot
# This file provides different TTS backends like Sarvam AI and OpenAI.

import base64
import os
from pathlib import Path
from typing import Any

import httpx
from loguru import logger

class SarvamTTSProvider:
    """
    TTS provider using Sarvam AI's Bulbul models.
    """

    def __init__(
        self,
        api_key: str | None = None,
        voice: str = "shubh",
        language: str = "en-IN",
        model: str = "bulbul:v3",
    ):
        self.api_key = api_key or os.environ.get("SARVAM_API_KEY")
        self.api_url = "https://api.sarvam.ai/text-to-speech"
        self.voice = voice or "shubh"
        self.language = language or "en-IN"
        self.model = model

    async def speak(self, text: str, output_path: str | Path) -> bool:
        """
        Convert text to speech and save to output_path.
        """
        if not self.api_key:
            logger.warning("Sarvam AI API key not configured for TTS")
            return False

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "text": text,
                    "target_language_code": self.language,
                    "speaker": self.voice,
                    "model": self.model,
                }
                headers = {
                    "api-subscription-key": self.api_key,
                    "Content-Type": "application/json",
                }

                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )

                response.raise_for_status()
                data = response.json()
                
                # Sarvam returns a list of base64 encoded audio strings
                audios = data.get("audios", [])
                if not audios:
                    logger.error("No audio returned from Sarvam AI")
                    return False
                
                # Combine all audio chunks
                with open(output_path, "wb") as f:
                    for audio_b64 in audios:
                        f.write(base64.b64decode(audio_b64))
                
                return True

        except Exception as e:
            logger.error("Sarvam TTS error: {}", e)
            return False

class OpenAITTSProvider:
    """
    TTS provider using OpenAI's TTS API.
    """

    def __init__(
        self,
        api_key: str | None = None,
        voice: str = "alloy",
        model: str = "tts-1",
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/audio/speech"
        self.voice = voice
        self.model = model

    async def speak(self, text: str, output_path: str | Path) -> bool:
        if not self.api_key:
            logger.warning("OpenAI API key not configured for TTS")
            return False

        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {
                    "model": self.model,
                    "input": text,
                    "voice": self.voice,
                }
                
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                
                response.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                return True
        except Exception as e:
            logger.error("OpenAI TTS error: {}", e)
            return False

def get_tts_provider(config: Any, channel_config: Any | None = None) -> Any:
    """
    Factory to create a TTS provider from config.
    """
    # Prefer settings from channel_config, fallback to global channels config
    provider_name = getattr(channel_config, "tts_provider", None) or config.channels.tts_provider
    voice = getattr(channel_config, "tts_voice", None) or config.channels.tts_voice
    
    if provider_name == "sarvam":
        return SarvamTTSProvider(
            api_key=config.providers.sarvam.api_key,
            voice=voice,
            language=getattr(channel_config, "transcription_language", None) or config.channels.transcription_language
        )
    elif provider_name == "openai":
        return OpenAITTSProvider(
            api_key=config.providers.openai.api_key,
            voice=voice or "alloy"
        )
    else:
        # Default to OpenAI if nothing else matches and key is available
        if config.providers.openai.api_key:
            return OpenAITTSProvider(api_key=config.providers.openai.api_key)
        return None
