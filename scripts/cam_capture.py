# scripts/cam_capture.py
# Purpose: CLI tool to capture a photo using the Zerobot camera.
# Used in: Testing and manual photo capture.

import os
import sys
import argparse
import datetime

# Add parent directory to path to allow importing zerobot module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zerobot.camera import ZerobotCamera

def main():
    parser = argparse.ArgumentParser(description="Zerobot Camera Capture Utility")
    parser.add_argument("-o", "--output", help="Output filename (default: photo_TIMESTAMP.jpg)")
    parser.add_argument("-r", "--resolution", nargs=2, type=int, default=[1280, 720], help="Resolution (width height)")
    
    args = parser.parse_args()
    
    if args.output:
        filename = args.output
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.jpg"
    
    print(f"Initializing camera at {args.resolution[0]}x{args.resolution[1]}...")
    
    try:
        cam = ZerobotCamera(resolution=tuple(args.resolution))
        print("Capturing...")
        if cam.capture_image(filename):
            print(f"Image successfully saved to: {os.path.abspath(filename)}")
        else:
            print("Failed to capture image.")
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure the camera is enabled in /boot/firmware/config.txt")
        print("and 'python3-picamera2' is installed.")
    finally:
        if 'cam' in locals():
            cam.close()

if __name__ == "__main__":
    main()
