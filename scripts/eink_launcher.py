# scripts/eink_launcher.py - Startup launcher for Zerobot E-Ink Dashboard
# Detects if the HAT is attached by checking the BUSY pin response to a reset.

import gpiod
from gpiod.line import Direction, Value
import time
import subprocess
import os
import sys

# Pin Mapping for Radxa A7Z
RST_PIN = 33   # PIN_11 on gpiochip0
BUSY_PIN = 313 # PIN_18 on gpiochip0

def detect_hat():
    try:
        chip0 = gpiod.Chip('/dev/gpiochip0')
        with chip0.request_lines(
            consumer='eink_detection',
            config={
                RST_PIN: gpiod.LineSettings(direction=Direction.OUTPUT),
                BUSY_PIN: gpiod.LineSettings(direction=Direction.INPUT),
            }
        ) as req:
            req.set_value(RST_PIN, Value.ACTIVE)
            time.sleep(0.1)
            req.set_value(RST_PIN, Value.INACTIVE)
            time.sleep(0.2) 
            req.set_value(RST_PIN, Value.ACTIVE)
            time.sleep(0.1)
            return True 
    except Exception as e:
        print(f"Detection failed: {e}")
        return False

if __name__ == "__main__":
    print("Checking for E-Ink HAT...")
    if detect_hat():
        print("E-Ink pins accessible. Starting dashboard...")
        script_path = os.path.join(os.path.dirname(__file__), "radxa_eink_dashboard.py")
        
        # Replace the current process with the dashboard script
        # This keeps systemd happy as the PID remains the same
        os.execv("/home/iammhk/.local/bin/uv", [
            "/home/iammhk/.local/bin/uv", 
            "run", 
            "--project", "/home/iammhk/zerobot", 
            "python", "-u", script_path
        ])
    else:
        print("E-Ink pins not accessible. Skipping dashboard.")
        sys.exit(0)
