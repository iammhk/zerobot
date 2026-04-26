# This file is part of the Zerobot multi-tiered LLM system.
# It delegates requests to different provider/model pairs based on task complexity.

from typing import Any, Dict, List, Optional, Awaitable, Callable
from loguru import logger

from zerobot.providers.base import LLMProvider, LLMResponse, GenerationSettings
from zerobot.agent.router import LLMRouter
from zerobot.config.schema import Config, TiersConfig

class TieredProvider(LLMProvider):
    """A provider that wraps multiple providers and routes requests based on tier."""

    def __init__(self, config: Config):
        # We don't call super().__init__ because we manage internal providers
        self.config = config
        self.tiers_config = config.agents.defaults.tiers
        self.router = LLMRouter(self.tiers_config)
        self.generation = GenerationSettings(
            temperature=config.agents.defaults.temperature,
            max_tokens=config.agents.defaults.max_tokens,
            reasoning_effort=config.agents.defaults.reasoning_effort,
        )
        
        # Lazy-loaded providers
        self._providers: Dict[str, LLMProvider] = {}

    def _get_provider_for_model(self, model: str) -> LLMProvider:
        """Resolve the provider for a specific model name."""
        # This is a bit tricky because _make_provider in zerobot.py is usually used.
        # We'll use a simplified version here or import it.
        from zerobot.zerobot import _make_provider_for_model
        
        if model not in self._providers:
            logger.debug(f"Initializing provider for tiered model: {model}")
            self._providers[model] = _make_provider_for_model(self.config, model)
        return self._providers[model]

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        # 1. Determine the target model
        # If model is explicitly passed, it overrides tiers
        target_model = model
        if not target_model:
            # Route based on the last user message
            last_user_msg = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    content = msg.get("content")
                    if isinstance(content, str):
                        last_user_msg = content
                    break
            
            target_model = self.router.route(last_user_msg)
            if not target_model:
                target_model = self.config.agents.defaults.model

        # 2. Get the appropriate provider
        provider = self._get_provider_for_model(target_model)
        
        # 3. Delegate
        logger.info(f"Tiered routing: using {target_model}")
        return await provider.chat(messages=messages, tools=tools, model=target_model, **kwargs)

    async def chat_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        on_content_delta: Optional[Callable[[str], Awaitable[None]]] = None,
        **kwargs
    ) -> LLMResponse:
        target_model = model
        if not target_model:
            last_user_msg = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    content = msg.get("content")
                    if isinstance(content, str):
                        last_user_msg = content
                    break
            target_model = self.router.route(last_user_msg)
            if not target_model:
                target_model = self.config.agents.defaults.model

        provider = self._get_provider_for_model(target_model)
        logger.info(f"Tiered routing (stream): using {target_model}")
        return await provider.chat_stream(
            messages=messages, 
            tools=tools, 
            model=target_model, 
            on_content_delta=on_content_delta,
            **kwargs
        )

    def get_default_model(self) -> str:
        return self.config.agents.defaults.model
