# remote_launcher.py - Background listener for KEY_POWER to toggle sesame_remote
import evdev
from evdev import ecodes
import subprocess
import time
import os
import sys

# Keywords to find the remote
KEYWORDS = ["Consumer Control", "Remote", "Shutter", "Gamepad", "Keyboard", "VR-PARK", "MOCUTE", "XiaoMi", "Controller"]

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
        output = subprocess.check_output(["pgrep", "-f", "sesame_remote.py"])
        return len(output) > 0
    except:
        return False

def main():
    print("Remote Launcher started. Listening for KEY_POWER...")
    while True:
        device = find_remote()
        if not device:
            time.sleep(5)
            continue
        
        print(f"Linked to {device.name}. Monitoring...")
        try:
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:
                    key_event = evdev.categorize(event)
                    if key_event.keystate == key_event.key_down:
                        if key_event.keycode == "KEY_POWER":
                            if not is_app_running():
                                print("Power key pressed! Launching sesame_remote...")
                                # Launch in a way that doesn't block the launcher
                                # We use tmux so the TUI has a session to live in
                                subprocess.Popen(["tmux", "new-session", "-d", "-s", "zerobot", "python3 " + os.path.expanduser("~/zerobot/scripts/sesame_remote.py") + " --bt"])
                            else:
                                print("App already running. KEY_POWER will be handled by the app itself to exit.")
        except (IOError, EOFError):
            print("Remote disconnected. Searching again...")
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
