# scripts/bt_sniff.py - Utility to sniff Bluetooth remote key codes.
# Run this script and press buttons on your remote to see their names.

import evdev
import sys
import os

def main():
    print("Searching for devices...")
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    
    if not devices:
        print("No input devices found. Try running with sudo.")
        return

    for i, dev in enumerate(devices):
        print(f"[{i}] {dev.name} ({dev.path})")

    try:
        idx = int(input("Select device index to sniff: "))
        device = devices[idx]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    print(f"Sniffing {device.name}. Press Ctrl+C to stop.")
    
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            key_event = evdev.categorize(event)
            if key_event.keystate == key_event.key_down:
                print(f"Key Down: {key_event.keycode} ({key_event.scancode})")

if __name__ == "__main__":
    main()
