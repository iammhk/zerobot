# This file is part of the Zerobot benchmarking suite.
# It aggregates all benchmarks into a single report.

import asyncio
import json
import time
from typing import Any, Dict
from pathlib import Path

from . import sys_bench, llm_bench, tool_bench, task_bench

class BenchmarkSuite:
    """The main benchmarking suite."""

    def __init__(self, bot=None):
        self.bot = bot
        self.sys_bench = sys_bench.SystemBenchmark()
        self.results = {}

    async def run_all(self, output_path: str | Path | None = None) -> Dict[str, Any]:
        """Run all benchmarks."""
        print("Starting Zerobot Benchmark Suite...")
        
        # 1. System Info
        print("Measuring system resources...")
        self.results["system"] = self.sys_bench.run()
        
        # 2. LLM Performance (if bot is provided)
        if self.bot:
            print(f"Benchmarking LLM ({self.bot._loop.model})...")
            lb = llm_bench.LLMBenchmark(self.bot._loop.provider, self.bot._loop.model)
            self.results["llm"] = await lb.run()
            
            # 3. Tool Performance
            print("Benchmarking tools...")
            tb = tool_bench.ToolBenchmark(self.bot._loop.tools)
            self.results["tools"] = await tb.run()

            # 4. Task Performance
            print("Benchmarking complex tasks (this may take a few minutes)...")
            self.results["tasks"] = await task_bench.run_all(self.bot)
        else:
            print("Skipping LLM and Tool benchmarks (no Zerobot instance provided).")

        self.results["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        if output_path:
            self._save_results(output_path)
            
        print("Benchmark complete.")
        return self.results

    def _save_results(self, path: str | Path):
        """Save results to a JSON file."""
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to {path}")

    def print_summary(self):
        """Print a human-readable summary of the results."""
        res = self.results
        print("\n" + "="*40)
        print("       ZEROBOT PERFORMANCE SUMMARY")
        print("="*40)
        
        sys = res.get("system", {})
        print(f"Platform: {sys.get('platform')}")
        print(f"CPU Cores: {sys.get('cpu_count')}")
        
        mem = sys.get("memory", {})
        if "rss_kb" in mem:
            print(f"Process Memory (RSS): {mem['rss_kb']} KB")
        elif "rss_bytes" in mem:
            print(f"Process Memory (RSS): {mem['rss_bytes'] // 1024} KB")

        llm = res.get("llm", {})
        if llm:
            if "error" in llm:
                print(f"LLM Error: {llm['error']}")
            else:
                print(f"LLM Model: {llm.get('model')}")
                print(f"TTFT: {llm.get('ttft_sec')}s")
                print(f"TPS: {llm.get('tps')} tokens/sec")
        
        tools = res.get("tools", {})
        if tools:
            print("\nTool Latencies:")
            for name, data in tools.items():
                print(f"  - {name}: {data.get('latency_sec')}s")

        if "tasks" in res:
            tasks = res["tasks"]
            print("\nTask Performance:")
            if "io_chain" in tasks:
                io = tasks["io_chain"]
                print(f"  - IO Chain: {io.get('total_latency', 0):.2f}s (Success: {io.get('success', 'N/A')})")
            if "code_chain" in tasks:
                code = tasks["code_chain"]
                print(f"  - Code Chain: {code.get('total_latency', 0):.2f}s (Success: {code.get('success', 'N/A')})")
            if "context_stress" in tasks:
                stress = tasks["context_stress"]
                print("  - Context Stress (TTFT): ", end="")
                ttfts = [f"{r.get('ttft', 0):.1f}s" if r.get('ttft') else "N/A" for r in stress]
                print(" -> ".join(ttfts))
        
        print("="*40 + "\n")
