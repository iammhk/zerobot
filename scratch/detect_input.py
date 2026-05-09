# detect_input.py - Diagnostic script to list all input devices and their names
import evdev

def main():
    print("Listing all input devices...")
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    if not devices:
        print("No input devices found. Are you running as root or in the 'input' group?")
        return

    for device in devices:
        print(f"Path: {device.path} | Name: {device.name} | Phys: {device.phys}")

if __name__ == "__main__":
    main()
