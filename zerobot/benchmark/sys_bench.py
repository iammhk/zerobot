# This file is part of the Zerobot benchmarking suite.
# It measures system resources like CPU and RAM usage.

import os
import time
import platform
import subprocess
from typing import Any, Dict

class SystemBenchmark:
    """Benchmark for system resources."""

    def run(self) -> Dict[str, Any]:
        """Execute the system benchmark."""
        results = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "memory": self._get_memory_info(),
            "load": self._get_load_avg(),
        }
        return results

    def _get_memory_info(self) -> Dict[str, Any]:
        """Get RAM usage info."""
        mem_info = {}
        if platform.system() == "Linux":
            try:
                with open("/proc/meminfo", "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        if "MemTotal" in line:
                            mem_info["total_kb"] = int(line.split()[1])
                        if "MemAvailable" in line:
                            mem_info["available_kb"] = int(line.split()[1])
                        if "MemFree" in line:
                            mem_info["free_kb"] = int(line.split()[1])
            except Exception:
                pass
        
        # Process specific memory
        try:
            import psutil
            process = psutil.Process(os.getpid())
            mem = process.memory_info()
            mem_info["rss_bytes"] = mem.rss
            mem_info["vms_bytes"] = mem.vms
        except ImportError:
            # Fallback for process memory on Linux if psutil is missing
            if platform.system() == "Linux":
                try:
                    with open(f"/proc/{os.getpid()}/status", "r") as f:
                        for line in f:
                            if "VmRSS" in line:
                                mem_info["rss_kb"] = int(line.split()[1])
                            if "Vmsize" in line:
                                mem_info["vms_kb"] = int(line.split()[1])
                except Exception:
                    pass
        
        return mem_info

    def _get_load_avg(self) -> Any:
        """Get system load average."""
        if hasattr(os, "getloadavg"):
            return os.getloadavg()
        return None

if __name__ == "__main__":
    bench = SystemBenchmark()
    print(bench.run())
