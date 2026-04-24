"""
Standalone utility script to scan all local network interfaces for Ollama servers.
This version detects all active subnets and verifies Ollama by hitting the API.
"""

import socket
import asyncio
import sys
import subprocess
import re
import urllib.request
import json

def get_local_subnets():
    """Find all local IPv4 prefixes using system commands."""
    subnets = []
    try:
        if sys.platform == 'win32':
            output = subprocess.check_output("ipconfig", shell=True).decode()
            # Look for IPv4 Address pattern
            matches = re.findall(r"IPv4 Address.*: (\d+\.\d+\.\d+)\.\d+", output)
            for m in matches:
                if not m.startswith("127."):
                    subnets.append(m + ".")
        else:
            # Linux/macOS
            try:
                output = subprocess.check_output("hostname -I", shell=True).decode()
                ips = output.split()
                for ip in ips:
                    if "." in ip:
                        prefix = ".".join(ip.split(".")[:-1]) + "."
                        subnets.append(prefix)
            except:
                output = subprocess.check_output("ip addr", shell=True).decode()
                matches = re.findall(r"inet (\d+\.\d+\.\d+)\.\d+", output)
                for m in matches:
                    if not m.startswith("127."):
                        subnets.append(m + ".")
    except Exception as e:
        print(f"Error detecting interfaces: {e}")
    
    return list(set(subnets))

async def scan_port(ip: str, port: int, timeout: float = 0.5) -> bool:
    """Check if a port is open."""
    try:
        conn = asyncio.open_connection(ip, port)
        _, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

def verify_ollama(ip, port):
    """Verify the service is actually Ollama by calling /api/tags."""
    url = f"http://{ip}:{port}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=1) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return True, data.get("models", [])
    except:
        pass
    return False, []

async def main():
    port = 11434
    print(f"--- Ollama Network Scanner ---")
    
    subnets = get_local_subnets()
    if not subnets:
        print("[!] No active IPv4 interfaces found.")
        return

    print(f"Detected subnets: {', '.join([s + '0/24' for s in subnets])}")
    
    found_servers = []
    
    for prefix in subnets:
        print(f"\nScanning {prefix}0/24...")
        tasks = []
        for i in range(1, 255):
            tasks.append(scan_port(f"{prefix}{i}", port, timeout=1.0))
        
        results = await asyncio.gather(*tasks)
        
        for i, found in enumerate(results):
            if found:
                ip = f"{prefix}{i+1}"
                print(f" [?] Found open port 11434 on {ip}. Verifying...")
                is_ol, models = verify_ollama(ip, port)
                if is_ol:
                    print(f" [!] CONFIRMED: Ollama is running at http://{ip}:{port}")
                    if models:
                        model_names = [m['name'] for m in models[:3]]
                        print(f"     Models: {', '.join(model_names)}{' ...' if len(models) > 3 else ''}")
                    found_servers.append(f"http://{ip}:{port}/v1")
                else:
                    print(f" [x] {ip}:11434 is open but not responding as Ollama.")

    if found_servers:
        print("\n" + "="*30)
        print("SUMMARY: Found Ollama servers:")
        for s in found_servers:
            print(f" -> {s}")
        print("="*30)
    else:
        print("\n[FAILED] No Ollama server found on any local subnet.")

if __name__ == "__main__":
    try:
        # Standard Windows asyncio fix
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScan cancelled.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
