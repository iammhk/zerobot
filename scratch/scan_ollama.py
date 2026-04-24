"""
Standalone utility script to scan the local network for Ollama servers.
This version uses only standard libraries (no dependencies like loguru).
"""

import socket
import asyncio
import sys

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

async def discover_ollama(port: int = 11434):
    """
    Attempt to discover a running Ollama server on the local network.
    Checks localhost first, then scans the local subnet.
    """
    # 1. Check localhost first
    print(f"Checking localhost on port {port}...")
    if await scan_port("127.0.0.1", port):
        return f"http://localhost:{port}/v1"

    # 2. Get local IP and determine subnet
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"Could not determine local IP: {e}")
        return None

    if not local_ip or local_ip == "127.0.0.1":
        print("Could not find a valid local network interface.")
        return None

    prefix = ".".join(local_ip.split(".")[:-1]) + "."
    print(f"Detected local IP: {local_ip}")
    print(f"Scanning subnet {prefix}0/24 for Ollama on port {port}...")

    # 3. Scan subnet in parallel
    tasks = []
    for i in range(1, 255):
        ip = f"{prefix}{i}"
        if ip == local_ip:
            continue
        tasks.append(scan_port(ip, port, timeout=1.0))

    results = await asyncio.gather(*tasks)

    found_ips = []
    for i, found in enumerate(results):
        if found:
            found_ip = f"{prefix}{i+1}"
            found_ips.append(found_ip)
    
    return found_ips

async def main():
    port = 11434
    found = await discover_ollama(port)
    
    if isinstance(found, list) and found:
        print("\n[SUCCESS] Found potential Ollama servers at:")
        for ip in found:
            print(f" - http://{ip}:{port}/v1")
    elif isinstance(found, str):
        print(f"\n[SUCCESS] Found Ollama at: {found}")
    else:
        print("\n[FAILED] No Ollama server found on the local network.")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScan cancelled.")
