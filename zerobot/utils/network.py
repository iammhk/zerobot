"""Network utilities for zerobot."""

import socket
import asyncio
from typing import Optional
from loguru import logger

async def scan_port(ip: str, port: int, timeout: float = 0.5) -> bool:
    """Check if a port is open on a given IP."""
    try:
        conn = asyncio.open_connection(ip, port)
        _, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False

async def discover_ollama(port: int = 11434) -> Optional[str]:
    """
    Attempt to discover a running Ollama server on the local network.
    Checks localhost first, then scans the local subnet.
    """
    # 1. Check localhost first (fastest)
    if await scan_port("127.0.0.1", port):
        return f"http://localhost:{port}/v1"

    # 2. Get local IP and determine subnet
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't actually connect, just used to find local interface
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        logger.debug(f"Could not determine local IP: {e}")
        return None

    if not local_ip or local_ip == "127.0.0.1":
        return None

    prefix = ".".join(local_ip.split(".")[:-1]) + "."
    logger.info(f"Scanning subnet {prefix}0/24 for Ollama on port {port}...")

    # 3. Scan subnet in parallel
    # We use a slightly longer timeout for network scan
    tasks = []
    for i in range(1, 255):
        ip = f"{prefix}{i}"
        if ip == local_ip:
            continue
        tasks.append(scan_port(ip, port, timeout=1.0))

    results = await asyncio.gather(*tasks)

    for i, found in enumerate(results):
        if found:
            found_ip = f"{prefix}{i+1}"
            # Verify it's actually Ollama by checking /api/tags or similar?
            # For now, port 11434 is a strong indicator.
            return f"http://{found_ip}:{port}/v1"

    return None
