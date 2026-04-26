# This file is part of the Zerobot benchmarking suite.
# It measures LLM inference latency and throughput.

import time
import asyncio
from typing import Any, Dict, List
from zerobot.providers.base import LLMProvider

class LLMBenchmark:
    """Benchmark for LLM inference."""

    def __init__(self, provider: LLMProvider, model: str | None = None):
        self.provider = provider
        self.model = model or provider.get_default_model()

    async def run(self, prompt: str = "Hello, who are you?") -> Dict[str, Any]:
        """Execute the LLM benchmark."""
        start_time = time.time()
        first_token_time = None
        token_count = 0
        full_content = ""

        async def on_delta(delta: str):
            nonlocal first_token_time, token_count, full_content
            if first_token_time is None:
                first_token_time = time.time()
            token_count += 1 # Rough estimate if not using tiktoken
            full_content += delta

        try:
            await self.provider.chat_stream_with_retry(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                on_content_delta=on_delta
            )
        except Exception as e:
            return {"error": str(e)}

        end_time = time.time()
        total_time = end_time - start_time
        ttft = (first_token_time - start_time) if first_token_time else None
        
        # Better token counting if tiktoken is available
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            token_count = len(encoding.encode(full_content))
        except Exception:
            # Fallback to rough estimate: 4 chars per token
            token_count = len(full_content) // 4

        tps = token_count / (end_time - first_token_time) if first_token_time and (end_time > first_token_time) else 0

        return {
            "model": self.model,
            "total_time_sec": round(total_time, 3),
            "ttft_sec": round(ttft, 3) if ttft else None,
            "tokens": token_count,
            "tps": round(tps, 2),
            "content_length": len(full_content)
        }

from zerobot.agent.hook import AgentHook, AgentHookContext

class LLMBenchmarkHook(AgentHook):
    """Hook to capture LLM performance metrics during an agent run."""
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.first_token_time = None
        self.token_count = 0
        self.ttft = None
        self.tps = None
        self._last_time = None

    async def on_turn_start(self, context: AgentHookContext) -> None:
        self.start_time = time.perf_counter()

    async def on_stream(self, context: AgentHookContext, delta: str) -> None:
        if self.first_token_time is None:
            self.first_token_time = time.perf_counter()
            if self.start_time:
                self.ttft = self.first_token_time - self.start_time
            
        self.token_count += 1
        self._last_time = time.perf_counter()

    async def on_stream_end(self, context: AgentHookContext, *, resuming: bool) -> None:
        if self.first_token_time and self._last_time:
            duration = self._last_time - self.first_token_time
            if duration > 0:
                self.tps = self.token_count / duration

if __name__ == "__main__":
    # Example usage would require a provider
    pass
