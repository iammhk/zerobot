# This file is part of the Zerobot benchmarking suite.
# It provides the CLI entry point for running benchmarks.

import asyncio
import typer
from pathlib import Path
from zerobot.zerobot import Zerobot
from .suite import BenchmarkSuite

app = typer.Typer(help="Zerobot performance benchmarking suite.")

@app.command()
def run(
    config: Path = typer.Option(None, "--config", "-c", help="Path to zerobot config.json"),
    output: Path = typer.Option(None, "--output", "-o", help="Path to save results (JSON)"),
):
    """Run the performance benchmarks."""
    async def _run():
        bot = None
        try:
            bot = Zerobot.from_config(config)
        except Exception as e:
            print(f"Warning: Could not load Zerobot config: {e}")
            print("Running system benchmarks only.")

        suite = BenchmarkSuite(bot)
        await suite.run_all(output_path=output)
        suite.print_summary()

    asyncio.run(_run())

if __name__ == "__main__":
    app()
