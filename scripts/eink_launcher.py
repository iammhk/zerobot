# scripts/eink_launcher.py - Startup launcher for Zerobot E-Ink Dashboard
# Detects if the HAT is attached by checking the BUSY pin response to a reset.

import gpiod
from gpiod.line import Direction, Value
import time
import subprocess
import os

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
            # Check if BUSY toggles after RST
            initial_busy = req.get_value(BUSY_PIN)
            
            # Hardware Reset
            req.set_value(RST_PIN, Value.ACTIVE)
            time.sleep(0.1)
            req.set_value(RST_PIN, Value.INACTIVE)
            time.sleep(0.1)
            
            after_reset_busy = req.get_value(BUSY_PIN)
            
            # If the pin changed or is in a specific state, HAT is likely present
            # Note: Floating pins might be unpredictable, but usually pulled high/low by the HAT
            if initial_busy != after_reset_busy or after_reset_busy == Value.INACTIVE:
                return True
            return False
    except Exception as e:
        print(f"Detection failed: {e}")
        return False

if __name__ == "__main__":
    print("Checking for E-Ink HAT...")
    if detect_hat():
        print("E-Ink HAT detected! Starting dashboard...")
        script_path = os.path.join(os.path.dirname(__file__), "radxa_eink_dashboard.py")
        # Run the dashboard script
        subprocess.run(["~/.local/bin/uv", "run", "--project", "~/zerobot", "python", "-u", script_path], shell=True)
    else:
        print("E-Ink HAT not detected. Skipping dashboard.")
