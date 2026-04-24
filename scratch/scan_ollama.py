"""
Utility script to scan the local network for Ollama servers.
This uses the built-in discovery logic from zerobot.
"""

import asyncio
import sys
import os

# Add the project root to path so we can import zerobot
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from zerobot.utils.network import discover_ollama

async def main():
    print("Scanning local network for Ollama (port 11434)...")
    result = await discover_ollama()
    if result:
        print(f"\n[SUCCESS] Found Ollama at: {result}")
    else:
        print("\n[FAILED] No Ollama server found on the local network.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScan cancelled.")
