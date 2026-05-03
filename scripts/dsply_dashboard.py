"""
scripts/dsply_dashboard.py - System status dashboard for Zerobot
Shows IP, CPU Temp, and Memory usage on the 1.8" TFT.
"""

import sys
import os
import time
import socket
import subprocess

# Add parent directory to path to import zerobot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zerobot.utils.display import ZerobotDisplay
from luma.core.render import canvas

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_cpu_temp():
    try:
        res = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
        return res.replace("temp=", "").replace("'C\n", " C")
    except:
        return "N/A"

def show_dashboard():
    disp = ZerobotDisplay()
    print("Starting Dashboard (Ctrl+C to stop)...")
    
    try:
        while True:
            ip = get_ip()
            temp = get_cpu_temp()
            
            with canvas(disp.device) as draw:
                # Header
                draw.rectangle((0, 0, disp.width, 22), fill="blue")
                draw.text((10, 5), "ZEROBOT DASHBOARD", fill="white")
                
                # Stats
                draw.text((10, 35), f"IP: {ip}", fill="cyan")
                draw.text((10, 55), f"CPU: {temp}", fill="orange")
                draw.text((10, 75), f"MODE: Remote Ready", fill="green")
                
                # Small decorative eye
                draw.ellipse((disp.width - 40, disp.height - 40, disp.width - 10, disp.height - 10), outline="white")
                draw.point((disp.width - 25, disp.height - 25), fill="white")

            time.sleep(5)
    except KeyboardInterrupt:
        print("Dashboard stopped.")

if __name__ == "__main__":
    show_dashboard()
