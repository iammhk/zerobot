# update_config.py - Update config.json to include wakeWord
import json
import os
from pathlib import Path

config_path = Path.home() / ".zerobot" / "config.json"
if config_path.exists():
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    if "channels" in config and "voice" in config["channels"]:
        config["channels"]["voice"]["wakeWord"] = "Zerobot"
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("Updated config.json with wakeWord: Zerobot")
    else:
        print("Could not find channels.voice in config.json")
else:
    print(f"Config file not found at {config_path}")
