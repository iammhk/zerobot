# log_events.py - Diagnostic script to log all events from the remote
import evdev
from evdev import ecodes

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

def main():
    device = find_remote()
    if not device:
        print("No remote found.")
        return

    print(f"Listening to {device.name} at {device.path}...")
    print("Press buttons on your remote to see their codes (Ctrl+C to stop)")
    
    try:
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = evdev.categorize(event)
                if key_event.keystate == key_event.key_down:
                    print(f"Key Pressed: {key_event.keycode} | Code: {key_event.scancode}")
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
