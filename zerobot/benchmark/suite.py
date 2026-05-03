# This file is part of the Zerobot benchmarking suite.
# It aggregates all benchmarks into a single report.

import asyncio
import json
import time
from typing import Any, Dict
from pathlib import Path

from . import sys_bench, llm_bench, tool_bench, task_bench, servo_bench

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
        
        # 1.5. Servo Performance
        print("Benchmarking servo movement sequences...")
        sb = servo_bench.ServoBenchmark()
        self.results["servos"] = await sb.run()
        
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
        """Print a human-readable summary of the results using Rich."""
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.columns import Columns
        from rich import box

        console = Console()
        res = self.results
        
        console.print("\n")
        console.print(Panel(
            "[bold cyan]ZEROBOT PERFORMANCE REPORT[/bold cyan]",
            expand=False,
            border_style="bright_blue",
            box=box.DOUBLE
        ))

        # 1. System Info
        sys = res.get("system", {})
        console.print(f"[bold blue]Platform:[/bold blue] {sys.get('platform')}")
        console.print(f"[bold blue]CPU Cores:[/bold blue] {sys.get('cpu_count')}")
        
        mem = sys.get("memory", {})
        if "rss_kb" in mem:
            console.print(f"[bold blue]Process Memory:[/bold blue] [yellow]{mem['rss_kb']}[/yellow] KB")

        # 2. LLM Performance
        llm = res.get("llm", {})
        if llm:
            table = Table(title="LLM Performance", box=box.SIMPLE, header_style="bold magenta")
            table.add_column("Metric", style="dim")
            table.add_column("Value", style="bold yellow")
            
            if "error" in llm:
                table.add_row("Error", f"[red]{llm['error']}[/red]")
            else:
                table.add_row("Model", llm.get("model", "Unknown"))
                table.add_row("TTFT", f"{llm.get('ttft_sec', 0):.3f}s")
                table.add_row("TPS", f"{llm.get('tps', 0):.2f} tok/s")
            console.print(table)
        
        # 3. Tool Performance
        tools = res.get("tools", {})
        if tools:
            table = Table(title="Tool Latencies", box=box.SIMPLE, header_style="bold green")
            table.add_column("Tool", style="dim")
            table.add_column("Latency", style="bold yellow")
            table.add_column("Status")
            
            for name, data in tools.items():
                status = data.get("status", "ok")
                status_fmt = f"[green]{status}[/green]" if status == "ok" else f"[red]{status}[/red]"
                table.add_row(name, f"{data.get('latency_sec', 0):.4f}s", status_fmt)
            console.print(table)

        # 4. Task Performance
        tasks = res.get("tasks", {})
        if tasks:
            table = Table(title="Task Reasoning & Stress Test", box=box.ROUNDED, border_style="bright_cyan")
            table.add_column("Task / Round", style="cyan")
            table.add_column("Latency", style="bold yellow")
            table.add_column("Success / TTFT", justify="center")

            if "io_chain" in tasks:
                io = tasks["io_chain"]
                success = "[green]PASS[/green]" if io.get("success") else "[red]FAIL[/red]"
                table.add_row("IO Chain", f"{io.get('total_latency', 0):.2f}s", success)
            
            if "code_chain" in tasks:
                code = tasks["code_chain"]
                success = "[green]PASS[/green]" if code.get("success") else "[red]FAIL[/red]"
                table.add_row("Code Chain", f"{code.get('total_latency', 0):.2f}s", success)
            
            if "context_stress" in tasks:
                table.add_section()
                for r in tasks["context_stress"]:
                    ttft = f"{r.get('ttft', 0):.2f}s" if r.get("ttft") else "[dim]N/A[/dim]"
                    table.add_row(f"Stress Round {r.get('round')}", f"{r.get('total_latency', 0):.2f}s", f"TTFT: {ttft}")
            
            console.print(table)

        # 5. Servo Performance
        servos = res.get("servos", {})
        if servos:
            table = Table(title="Servo Gait & Gesture Latencies", box=box.SIMPLE, header_style="bold blue")
            table.add_column("Sequence", style="dim")
            table.add_column("Latency", style="bold yellow")
            table.add_column("Hardware")

            hw = "[green]Detected[/green]" if servos.get("hardware_available") else "[red]Not Found[/red]"
            
            for key in ["forward_gait", "wave_gesture"]:
                data = servos.get(key, {})
                table.add_row(key.replace("_", " ").title(), f"{data.get('latency_sec', 0):.4f}s", hw)
            
            console.print(table)

        console.print("\n" + "[dim]Benchmark complete. Report generated at " + res.get("timestamp", "") + "[/dim]\n")
