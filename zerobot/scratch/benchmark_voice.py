# benchmark_voice.py - Latency benchmark for Zerobot voice pipeline
# This script measures STT, LLM, and TTS latencies for comparison.

import asyncio
import time
import os
from pathlib import Path
from loguru import logger

from zerobot.config.loader import load_config
from zerobot.providers.transcription import SarvamTranscriptionProvider
from zerobot.providers.tts import SarvamTTSProvider
from zerobot.agent.loop import AgentLoop
from zerobot.bus.queue import MessageBus
from zerobot.providers.registry import find_by_name
from zerobot.providers.base import GenerationSettings

async def run_benchmark(model_name: str, label: str):
    logger.info(f"=== Starting Benchmark: {label} ({model_name}) ===")
    
    config = load_config()
    bus = MessageBus()
    
    # 1. Initialize STT (Sarvam)
    stt = SarvamTranscriptionProvider(
        api_key=config.providers.sarvam.api_key,
        language="en-IN"
    )
    
    # 2. Initialize Agent
    # Mock the provider based on model_name
    from zerobot.cli.commands import _make_provider
    # Temporarily override config model
    config.agents.defaults.model = model_name
    provider = _make_provider(config)
    
    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=config.workspace_path,
        model=model_name,
        channels_config=config.channels
    )
    from zerobot.agent.tools.registry import ToolRegistry
    agent.tools = ToolRegistry() # Disable all tools for benchmark
    
    # 3. Initialize TTS (Sarvam)
    tts = SarvamTTSProvider(
        api_key=config.providers.sarvam.api_key,
        voice="shubh"
    )
    
    dummy_wav = Path("zerobot/scratch/dummy.wav")
    output_mp3 = Path("zerobot/scratch/benchmark_output.mp3")
    
    # --- STEP 1: STT ---
    start = time.perf_counter()
    text = await stt.transcribe(dummy_wav)
    stt_time = time.perf_counter() - start
    # If dummy is silent, it might return empty. Let's use a fallback text for LLM if STT is empty.
    input_text = text or "Hello, how are you?"
    logger.info(f"STT Latency: {stt_time:.2f}s (Text: '{input_text}')")
    
    # --- STEP 2: LLM ---
    start = time.perf_counter()
    # Process directly without full bus for timing
    resp = await agent.process_direct(
        input_text,
        session_key="benchmark",
        channel="voice",
        chat_id="test"
    )
    llm_time = time.perf_counter() - start
    response_text = resp.content if resp else "Error"
    logger.info(f"LLM Latency: {llm_time:.2f}s")
    
    # --- STEP 3: TTS ---
    start = time.perf_counter()
    success = await tts.speak(response_text, output_mp3)
    tts_time = time.perf_counter() - start
    logger.info(f"TTS Latency: {tts_time:.2f}s")
    
    total = stt_time + llm_time + tts_time
    logger.info(f"TOTAL V2V LATENCY: {total:.2f}s")
    print(f"\nResults for {label}:")
    print(f"  STT: {stt_time:.2f}s")
    print(f"  LLM: {llm_time:.2f}s")
    print(f"  TTS: {tts_time:.2f}s")
    print(f"  TOTAL: {total:.2f}s\n")
    
    return {"stt": stt_time, "llm": llm_time, "tts": tts_time, "total": total}

async def main():
    # Test 1: Ollama
    # res1 = await run_benchmark("ollama/gemma4:e2b", "Ollama LLM")
    res1 = {"stt": 0.83, "llm": 128.92, "tts": 4.26, "total": 134.01}
    
    # Test 2: Sarvam
    res2 = await run_benchmark("sarvam/sarvam-m", "Sarvam LLM")
    
    print("="*40)
    print("FINAL COMPARISON")
    print("="*40)
    print(f"{'Step':<10} | {'Ollama (s)':<12} | {'Sarvam (s)':<12}")
    print("-"*40)
    for step in ["stt", "llm", "tts", "total"]:
        print(f"{step.upper():<10} | {res1[step]:<12.2f} | {res2[step]:<12.2f}")

if __name__ == "__main__":
    asyncio.run(main())
