# zerobot/benchmark/servo_bench.py
# Benchmark for servo movement sequences.
# This file is used in actual project to measure hardware interaction latency and gait timing.

import time
import asyncio
import sys
from typing import Any, Dict
from zerobot.utils.pca9685 import PCA9685, ServoHelper

class ServoBenchmark:
    """Benchmark for servo movement sequences."""

    def __init__(self):
        self.pca = None
        self.helper = None
        
        # --- Channel Mapping ---
        self.L1, self.R1, self.L2, self.R2 = 0, 1, 2, 3
        self.L3, self.R3, self.L4, self.R4 = 4, 5, 6, 7

        # --- HARD LIMITS ---
        self.LIMITS = {
            0: (0, 90), 1: (90, 180), 2: (90, 180), 3: (0, 90),
            4: (0, 180), 5: (0, 180), 6: (0, 180), 7: (0, 180)
        }
        # Standing Home Position
        self.HOME = {
            0: 45, 1: 135, 2: 135, 3: 45,
            4: 45, 5: 135, 6: 135, 7: 45
        }

    def _init_hardware(self) -> bool:
        """Initialize PCA9685 if on Linux."""
        if sys.platform != "linux":
            return False
        try:
            self.pca = PCA9685()
            # If PCA9685 was not initialized (e.g. no I2C device), it doesn't raise but _bus is None
            if self.pca._bus is None:
                return False
            self.helper = ServoHelper(self.pca)
            return True
        except Exception:
            return False

    async def run(self) -> Dict[str, Any]:
        """Execute all servo benchmarks."""
        results = {}
        
        hw_available = self._init_hardware()
        results["hardware_available"] = hw_available

        # Execute sequences
        results["forward_gait"] = await self.benchmark_forward_gait()
        results["wave_gesture"] = await self.benchmark_wave_gesture()

        if self.pca:
            # Release all servos to save power after benchmark
            for i in range(8):
                if hw_available:
                    self.helper.release(i)
            self.pca.close()

        return results

    async def benchmark_forward_gait(self) -> Dict[str, Any]:
        """Measure time to perform 1 cycle of forward gait."""
        start_time = time.time()
        
        try:
            # 1. Standing Home
            self._set_angles(self.HOME)
            await asyncio.sleep(0.05)

            # simplified "Power Stomp" cycle
            # Lift Front
            self._set_angles({4: 160, 5: 20})
            await asyncio.sleep(0.05)
            
            # Reach Front
            self._set_angles({0: 5, 1: 175})
            await asyncio.sleep(0.05)
            
            # Slam Front
            self._set_angles({4: 10, 5: 170})
            await asyncio.sleep(0.05)
            
            # Push Hind
            self._set_angles({6: 20, 7: 160})
            await asyncio.sleep(0.05)
            
            # Reset
            self._set_angles(self.HOME)
            await asyncio.sleep(0.05)

        except Exception as e:
            return {"error": str(e)}

        end_time = time.time()
        return {"latency_sec": round(end_time - start_time, 4)}

    async def benchmark_wave_gesture(self) -> Dict[str, Any]:
        """Measure time to perform a wave gesture."""
        start_time = time.time()
        
        try:
            # Home
            self._set_angles(self.HOME)
            await asyncio.sleep(0.05)

            # Stabilize Shift
            self._set_angles({0: 90, 1: 90, 2: 90, 3: 90, 5: 120, 6: 100, 7: 80})
            await asyncio.sleep(0.1)

            # Lift Knee
            self._set_angles({4: 170})
            await asyncio.sleep(0.05)
            
            # 2 Waves
            for _ in range(2):
                self._set_angles({0: 10})
                await asyncio.sleep(0.05)
                self._set_angles({0: 80})
                await asyncio.sleep(0.05)

            # Return Home
            self._set_angles(self.HOME)
            await asyncio.sleep(0.05)

        except Exception as e:
            return {"error": str(e)}

        end_time = time.time()
        return {"latency_sec": round(end_time - start_time, 4)}

    def _set_angles(self, angles: Dict[int, float]):
        """Internal helper to set multiple angles if hardware is available."""
        if self.helper:
            for ch, ang in angles.items():
                self.helper.set_angle(ch, ang)
