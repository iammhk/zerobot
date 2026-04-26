# This file is part of the Zerobot benchmarking suite.
# It measures tool execution latency.

import time
import asyncio
from typing import Any, Dict, List
from zerobot.agent.tools.registry import ToolRegistry

class ToolBenchmark:
    """Benchmark for tool execution."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    async def run(self, tools_to_test: List[str] | None = None) -> Dict[str, Any]:
        """Execute the tool benchmark."""
        if tools_to_test is None:
            tools_to_test = ["list_dir", "read_file", "exec"]

        results = {}
        for tool_name in tools_to_test:
            if self.registry.get(tool_name):
                results[tool_name] = await self._benchmark_tool(tool_name)
            else:
                results[tool_name] = {"error": "Tool not found"}
        
        return results

    async def _benchmark_tool(self, name: str) -> Dict[str, Any]:
        """Measure latency of a specific tool."""
        # Define sample arguments for common tools
        sample_args = {
            "list_dir": {"path": "."},
            "read_file": {"path": "README.md"},
            "exec": {"command": "echo 'bench'"},
        }

        args = sample_args.get(name, {})
        start_time = time.time()
        try:
            # We use a timeout to prevent hanging the benchmark
            result = await asyncio.wait_for(self.registry.execute(name, args), timeout=5.0)
            status = "ok"
        except Exception as e:
            status = f"error: {str(e)}"
        
        end_time = time.time()
        return {
            "latency_sec": round(end_time - start_time, 4),
            "status": status
        }

if __name__ == "__main__":
    pass
