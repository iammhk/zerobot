"""Network utilities for zerobot."""

import socket
import asyncio
import subprocess
import re
import sys
import json
import httpx
from pathlib import Path
from typing import Optional, List
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

def get_local_subnets() -> List[str]:
    """Find all local IPv4 prefixes using system commands."""
    subnets = []
    try:
        if sys.platform == 'win32':
            # Use ipconfig on Windows
            output = subprocess.check_output("ipconfig", shell=True).decode(errors="ignore")
            matches = re.findall(r"IPv4 Address.*: (\d+\.\d+\.\d+)\.\d+", output)
            for m in matches:
                if not m.startswith("127."):
                    subnets.append(m + ".")
        else:
            # Use hostname -I or ip addr on Linux/macOS
            try:
                output = subprocess.check_output("hostname -I", shell=True).decode(errors="ignore")
                ips = output.split()
                for ip in ips:
                    if "." in ip:
                        prefix = ".".join(ip.split(".")[:-1]) + "."
                        subnets.append(prefix)
            except Exception:
                output = subprocess.check_output("ip addr", shell=True).decode(errors="ignore")
                matches = re.findall(r"inet (\d+\.\d+\.\d+)\.\d+", output)
                for m in matches:
                    if not m.startswith("127."):
                        subnets.append(m + ".")
    except Exception as e:
        logger.debug(f"Error detecting interfaces: {e}")

    return list(set(subnets))

async def verify_ollama(ip: str, port: int) -> bool:
    """Verify the service is actually Ollama by calling /api/tags."""
    url = f"http://{ip}:{port}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return True
    except Exception:
        pass
    return False

def get_network_cache_path() -> Path:
    """Get the path to the network cache file."""
    return Path.home() / ".zerobot" / "network_cache.json"

def load_network_cache() -> dict:
    """Load the network cache from file."""
    path = get_network_cache_path()
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_network_cache(cache: dict) -> None:
    """Save the network cache to file."""
    path = get_network_cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass

async def discover_ollama(port: int = 11434) -> Optional[str]:
    """
    Attempt to discover a running Ollama server on the local network.
    Checks localhost first, then a cached IP if available, then scans all detected local subnets.
    """
    # 1. Check localhost first (fastest)
    if await scan_port("127.0.0.1", port):
        if await verify_ollama("127.0.0.1", port):
            return f"http://localhost:{port}/v1"

    # 2. Check cached IP
    cache = load_network_cache()
    cached_ip = cache.get("ollama_ip")
    if cached_ip:
        logger.debug(f"Checking cached Ollama IP: {cached_ip}")
        if await scan_port(cached_ip, port, timeout=0.5):
            if await verify_ollama(cached_ip, port):
                logger.success(f"Ollama found at cached address: http://{cached_ip}:{port}")
                return f"http://{cached_ip}:{port}/v1"
        logger.debug("Cached Ollama IP unreachable or invalid.")

    # 3. Get all local subnets
    subnets = get_local_subnets()
    if not subnets:
        # Fallback to single interface detection if subnet detection fails
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            if local_ip and local_ip != "127.0.0.1":
                subnets = [".".join(local_ip.split(".")[:-1]) + "."]
        except Exception:
            pass

    if not subnets:
        return None

    logger.info(f"Scanning subnets {', '.join([s + '0/24' for s in subnets])} for Ollama...")

    # 4. Scan subnets in parallel
    for prefix in subnets:
        tasks = []
        for i in range(1, 255):
            tasks.append(scan_port(f"{prefix}{i}", port, timeout=1.0))

        results = await asyncio.gather(*tasks)

        for i, found in enumerate(results):
            if found:
                ip = f"{prefix}{i+1}"
                # Verify it's actually Ollama
                if await verify_ollama(ip, port):
                    logger.success(f"Ollama discovered at http://{ip}:{port}")
                    # Save to cache
                    cache["ollama_ip"] = ip
                    save_network_cache(cache)
                    return f"http://{ip}:{port}/v1"

    return None
