# scratch/update_config_camera.py
# Purpose: Updates Zerobot config to include camera in connected hardware and fix any syntax errors.
# Used in: One-time configuration update.

import json
import os
from pathlib import Path

config_path = Path.home() / ".zerobot" / "config.json"

if not config_path.exists():
    print(f"Config not found at {config_path}")
    exit(1)

try:
    # Read raw text first to fix potential missing comma
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix missing comma if it exists (very specific fix for what I saw in cat output)
    if '"connectedHardware": ["pca9685"]' in content and '"dream":' in content:
        if '"connectedHardware": ["pca9685"]\n      "dream":' in content:
            content = content.replace('"connectedHardware": ["pca9685"]', '"connectedHardware": ["pca9685"],')
            print("Fixed missing comma in config.")

    data = json.loads(content)
    
    defaults = data.get("agents", {}).get("defaults", {})
    hardware = defaults.get("connectedHardware", [])
    
    if "camera" not in hardware:
        hardware.append("camera")
        defaults["connectedHardware"] = hardware
        print("Added 'camera' to connectedHardware.")
    else:
        print("'camera' already in connectedHardware.")
        
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Config updated successfully.")

except Exception as e:
    print(f"Error updating config: {e}")
    exit(1)
