# This file is part of the Zerobot benchmarking suite.
# It measures complex agent tasks involving multi-turn tool use.

import time
import asyncio
from typing import Any, Dict, List
from zerobot.zerobot import Zerobot
from .llm_bench import LLMBenchmarkHook

async def run_io_chain(bot: Zerobot) -> Dict[str, Any]:
    """Benchmark a task involving searching, reading, and summarizing."""
    prompt = "List the files in the current directory, read README.md, and tell me how many lines it has."
    
    start_time = time.perf_counter()
    hook = LLMBenchmarkHook()
    result = await bot.run(prompt, hooks=[hook])
    end_time = time.perf_counter()
    
    success = "README.md" in result.content or "README" in result.content
    if not success:
        print(f"IO Chain Failed. Response: {result.content[:200]}...")

    return {
        "task": "io_chain",
        "total_latency": end_time - start_time,
        "ttft": hook.ttft,
        "tps": hook.tps,
        "success": success
    }

async def run_code_chain(bot: Zerobot) -> Dict[str, Any]:
    """Benchmark a task involving code generation and execution."""
    prompt = "Write a python script that calculates the sum of numbers from 1 to 100, save it as 'bench_sum.py', and run it. Afterwards, delete the file."
    
    start_time = time.perf_counter()
    hook = LLMBenchmarkHook()
    result = await bot.run(prompt, hooks=[hook])
    end_time = time.perf_counter()
    
    # Cleanup just in case the bot didn't
    try:
        if Path("bench_sum.py").exists():
            Path("bench_sum.py").unlink()
    except Exception:
        pass
    
    success = "5050" in result.content
    if not success:
        print(f"Code Chain Failed. Response: {result.content[:200]}...")

    return {
        "task": "code_chain",
        "total_latency": end_time - start_time,
        "ttft": hook.ttft,
        "tps": hook.tps,
        "success": success
    }

async def run_context_stress(bot: Zerobot, rounds: int = 5) -> List[Dict[str, Any]]:
    """Measure performance degradation as context grows."""
    results = []
    session_key = f"stress_{int(time.time())}"
    
    for i in range(rounds):
        prompt = f"Tell me a short unique fact about the number {i}."
        hook = LLMBenchmarkHook()
        
        start_time = time.perf_counter()
        await bot.run(prompt, session_key=session_key, hooks=[hook])
        end_time = time.perf_counter()
        
        results.append({
            "round": i + 1,
            "total_latency": end_time - start_time,
            "ttft": hook.ttft,
            "tps": hook.tps
        })
        
    return results

async def run_all(bot: Zerobot) -> Dict[str, Any]:
    """Run all task benchmarks."""
    if not bot:
        return {"error": "Zerobot instance required for task benchmarks."}
        
    print("Running IO Chain benchmark...")
    io_result = await run_io_chain(bot)
    
    print("Running Code Chain benchmark...")
    code_result = await run_code_chain(bot)
    
    print("Running Context Stress benchmark (5 rounds)...")
    stress_results = await run_context_stress(bot)
    
    return {
        "io_chain": io_result,
        "code_chain": code_result,
        "context_stress": stress_results
    }
