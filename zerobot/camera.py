# zerobot/camera.py
# Purpose: Provides a high-level interface for the Raspberry Pi Camera (V1.3 5MP).
# Used in: Actual project (Zerobot hardware integration).

import os
import time
import logging
from typing import Optional

try:
    from picamera2 import Picamera2
    HAS_PICAMERA2 = True
except ImportError:
    HAS_PICAMERA2 = False

class ZerobotCamera:
    """Wrapper for Raspberry Pi Camera using Picamera2."""
    
    def __init__(self, resolution=(1280, 720)):
        self.resolution = resolution
        self.pc2 = None
        self.logger = logging.getLogger("zerobot.camera")

    def _ensure_initialized(self):
        if not HAS_PICAMERA2:
            raise RuntimeError("picamera2 library not found. Install with: sudo apt install python3-picamera2")
        
        if self.pc2 is None:
            try:
                self.pc2 = Picamera2()
                self.pc2.configure(self.pc2.create_still_configuration(main=self.resolution))
                self.pc2.start()
                self.logger.info("Camera initialized and started.")
            except Exception as e:
                self.pc2 = None
                self.logger.error(f"Failed to initialize camera: {e}")
                raise RuntimeError(f"Camera initialization failed: {e}")

    def capture_image(self, filename: str) -> bool:
        """Captures a still image and saves it to the specified filename."""
        try:
            self._ensure_initialized()
            self.pc2.capture_file(filename)
            self.logger.info(f"Image captured: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to capture image: {e}")
            return False

    def close(self):
        """Releases camera resources."""
        if self.pc2:
            self.pc2.stop()
            self.pc2.close()
            self.pc2 = None
            self.logger.info("Camera closed.")

    def __del__(self):
        self.close()

if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    cam = ZerobotCamera()
    try:
        test_file = "test_capture.jpg"
        if cam.capture_image(test_file):
            print(f"Success! Saved to {test_file}")
        else:
            print("Capture failed.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cam.close()
