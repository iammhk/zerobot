"""
Test script to verify the upgraded discover_ollama utility.
"""

import asyncio
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from zerobot.utils.network import discover_ollama

async def main():
    print("Testing upgraded discover_ollama...")
    result = await discover_ollama()
    if result:
        print(f"\n[SUCCESS] Found and verified Ollama at: {result}")
    else:
        print("\n[FAILED] No Ollama server found or verified.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest cancelled.")
