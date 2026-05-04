# scripts/bt_remote.py - Bluetooth Remote Control for Zerobot
# This script listens for events from a Bluetooth HID device (remote) and maps them to robot movements.

import sys
import os
import time
import subprocess

# Add current directory to path for potential imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

try:
    import evdev
    from evdev import ecodes
except ImportError:
    print("❌ evdev library not found. Please install it with: pip install evdev")
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    # We will still try to proceed so the user can see the logic, but it will fail at runtime if not installed.

from dsply_xprsn import DsplyExpressions

# Initialize Display
try:
    expr = DsplyExpressions()
except:
    expr = None

# --- Configuration ---
# You can update this to match your remote's name or part of it.
REMOTE_NAME_KEYWORDS = ["Consumer Control", "Remote", "Shutter", "Gamepad", "Keyboard", "VR-PARK"]

# --- Mapping ---
# Custom mapping for Xiaomi RC Keyboard / Consumer Control
KEY_MAP = {
    # Directional
    "KEY_UP": "sesame_walk --dir 1",
    "KEY_DOWN": "sesame_walk --dir -1",
    "KEY_LEFT": "sesame_turn --dir 1",
    "KEY_RIGHT": "sesame_turn --dir -1",
    
    # Primary Actions
    "KEY_SELECT": "stand",       # Center button
    "KEY_HOMEPAGE": "stand",     # Home button
    "KEY_BACK": "mvmt_release",  # Back button (Release motors)
    "KEY_POWER": "mvmt_release", # Power button (Safety)
    
    # Secondary Actions
    "KEY_VOLUMEUP": "wave",
    "KEY_VOLUMEDOWN": "bow",
    "KEY_VIDEO": "dance",        # Play/Video button
    "KEY_GREEN": "bounce",       # Green / Special button
    "KEY_VOICECOMMAND": "cute",   # Voice / Mic button
    "KEY_APPSELECT": "point",    # App / Menu button
}

def find_remote():
    """Finds the first input device that matches common remote names, respecting keyword priority."""
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        if not devices:
            print("⚠️ No input devices found. Are you running as root?")
            return None
            
        # Priority search based on REMOTE_NAME_KEYWORDS order
        for keyword in REMOTE_NAME_KEYWORDS:
            for device in devices:
                if keyword.lower() in device.name.lower():
                    print(f"✅ Selected: {device.name} (matched '{keyword}')")
                    return device
                    
        print("Available devices searched:")
        for d in devices: print(f" - {d.name} ({d.path})")
    except Exception as e:
        print(f"Error listing devices: {e}")
    return None

def run_mvmt(name, args=None):
    """Executes a movement script."""
    # Check if name is already a full script filename or needs prefix
    if name.startswith("mvmt_"):
        script_base = name
    else:
        script_base = f"mvmt_{name}"
    
    if not script_base.endswith(".py"):
        script_filename = f"{script_base}.py"
    else:
        script_filename = script_base

    script_path = os.path.join(os.path.dirname(__file__), script_filename)
    
    # Fallback for complex commands
    if not os.path.exists(script_path):
        parts = name.split()
        if len(parts) > 1:
            name = parts[0]
            args = parts[1:] + (args if args else [])
            script_path = os.path.join(os.path.dirname(__file__), f"mvmt_{name}.py")

    if os.path.exists(script_path):
        cmd = [sys.executable, script_path]
        if args: cmd.extend(args)
        print(f"🚀 Running: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, capture_output=True)
            if expr: expr.happy()
        except Exception as e:
            print(f"❌ Execution error: {e}")
    else:
        print(f"⚠️ Movement script not found: {script_path}")

def main():
    print("🔵 Zerobot Bluetooth Remote Listener")
    print("Searching for remote...")
    
    # Check for root (evdev usually needs it)
    if os.geteuid() != 0:
        print("💡 TIP: You might need to run this with 'sudo' to access input devices.")

    remote = find_remote()
    if not remote:
        print("❌ No Bluetooth remote found. Make sure it's paired and connected.")
        return

    print(f"Listening to {remote.name}...")
    
    try:
        for event in remote.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = evdev.categorize(event)
                if key_event.keystate == key_event.key_down:
                    key_name = key_event.keycode
                    if isinstance(key_name, list):
                        key_name = key_name[0]
                    
                    print(f"Key Pressed: {key_name}")
                    
                    if key_name in KEY_MAP:
                        cmd_str = KEY_MAP[key_name]
                        run_mvmt(cmd_str)
                    else:
                        print(f"Unhandled key: {key_name}")


    except KeyboardInterrupt:
        print("\nStopping remote listener.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            remote.ungrab()
        except: pass

if __name__ == "__main__":
    main()
