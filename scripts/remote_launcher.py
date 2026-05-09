# remote_launcher.py - Background listener for KEY_POWER to toggle sesame_remote
# This file is used in a background service to launch the main TUI on button press.

import evdev
from evdev import ecodes
import subprocess
import time
import os
import sys

# Keywords to find the remote
KEYWORDS = ["Consumer Control", "Remote", "Shutter", "Gamepad", "Keyboard", "VR-PARK", "MOCUTE", "XiaoMi", "Controller", "Input"]

def find_remote():
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for keyword in KEYWORDS:
            for device in devices:
                if keyword.lower() in device.name.lower():
                    return device
    except: pass
    return None

def is_app_running():
    try:
        # Check for sesame_remote.py process
        output = subprocess.check_output(["pgrep", "-f", "sesame_remote.py"])
        return len(output) > 0
    except:
        return False

def main():
    print("Zerobot Remote Launcher started. Listening for KEY_POWER...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sesame_path = os.path.join(script_dir, "sesame_remote.py")
    
    while True:
        device = find_remote()
        if not device:
            time.sleep(5)
            continue
        
        print(f"✅ Linked to {device.name}. Monitoring for Power Key...")
        try:
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:
                    key_event = evdev.categorize(event)
                    if key_event.keystate == key_event.key_down:
                        keycode = key_event.keycode
                        if isinstance(keycode, list):
                            keycode = keycode[0]
                        
                        print(f"Key detected: {keycode}")
                        
                        # Some remotes use KEY_SLEEP or KEY_WAKEUP for the power button
                        if keycode in ["KEY_POWER", "KEY_SLEEP", "KEY_WAKEUP"]:
                            if not is_app_running():
                                print("🚀 Power key pressed! Launching sesame_remote in tmux session 'zerobot'...")
                                # We use tmux so the TUI has a persistent session to live in
                                # Use uv run to ensure the correct environment is used
                                cmd = ["tmux", "new-session", "-d", "-s", "zerobot", f"/home/iammhk/.local/bin/uv run {sesame_path} --bt"]
                                subprocess.Popen(cmd)
                            else:
                                print("ℹ️ App already running. Ignoring Power key.")
        except (IOError, EOFError):
            print("⚠️ Remote disconnected. Searching again...")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
