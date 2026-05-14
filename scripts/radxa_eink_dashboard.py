# scripts/radxa_eink_dashboard.py - System status dashboard for Zerobot on Radxa E-Ink Display
# Optimized for Waveshare 2.13" E-Ink BWR V3/V4

import os
import sys
import time
import socket
import subprocess
import psutil
from PIL import Image, ImageDraw, ImageFont

# Add parent directory to path to import zerobot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import spidev
    import gpiod
    from gpiod.line import Direction, Value
except ImportError:
    print("Error: Missing spidev or gpiod.")
    sys.exit(1)

# Display Constants
WIDTH = 104
HEIGHT = 212

# Pin Mapping for Radxa A7Z
RST_PIN = 33   # PIN_11 on gpiochip0
BUSY_PIN = 313 # PIN_18 on gpiochip0
DC_PIN = 5     # PIN_22 on gpiochip1

class EInkDashboard:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(1, 0)
        self.spi.max_speed_hz = 4000000
        self.spi.mode = 0

        self.chip0 = gpiod.Chip('/dev/gpiochip0')
        self.chip1 = gpiod.Chip('/dev/gpiochip1')
        
        self.req0 = self.chip0.request_lines(
            consumer='eink_dashboard',
            config={
                RST_PIN: gpiod.LineSettings(direction=Direction.OUTPUT),
                BUSY_PIN: gpiod.LineSettings(direction=Direction.INPUT),
            }
        )
        self.req1 = self.chip1.request_lines(
            consumer='eink_dashboard',
            config={
                DC_PIN: gpiod.LineSettings(direction=Direction.OUTPUT),
            }
        )

    def reset(self):
        self.req0.set_value(RST_PIN, Value.ACTIVE)
        time.sleep(0.2)
        self.req0.set_value(RST_PIN, Value.INACTIVE)
        time.sleep(0.1) # Increased wait
        self.req0.set_value(RST_PIN, Value.ACTIVE)
        time.sleep(0.2)

    def send_command(self, command):
        self.req1.set_value(DC_PIN, Value.INACTIVE)
        self.spi.writebytes([command])

    def send_data(self, data):
        self.req1.set_value(DC_PIN, Value.ACTIVE)
        self.spi.writebytes([data])

    def wait_until_idle(self):
        # Most Waveshare BWR are High when Busy
        print("Waiting for display idle...", end="", flush=True)
        while self.req0.get_value(BUSY_PIN) == Value.ACTIVE:
            print(".", end="", flush=True)
            time.sleep(0.1)
        print(" Done.")

    def init_display(self):
        print("Initializing Display (BWR V3/V4)...")
        self.reset()
        
        self.send_command(0x06) # BOOSTER_SOFT_START
        self.send_data(0x17)
        self.send_data(0x17)
        self.send_data(0x17)
        
        self.send_command(0x04) # POWER_ON
        self.wait_until_idle()
        
        self.send_command(0x00) # PANEL_SETTING
        self.send_data(0x8F)
        
        self.send_command(0x50) # VCOM_AND_DATA_INTERVAL_SETTING
        self.send_data(0xF0)
        
        self.send_command(0x61) # RESOLUTION_SETTING
        self.send_data(WIDTH & 0xff)
        self.send_data(HEIGHT >> 8)
        self.send_data(HEIGHT & 0xff)

    def get_stats(self):
        current_time = time.strftime("%H:%M")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "No Network"
        cpu_usage = psutil.cpu_percent()
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = float(f.read()) / 1000.0
        except:
            temp = 0.0
        npu_status = "NPU: OK" if os.path.exists("/dev/vipcore") else "NPU: OFF"
        return {
            "time": current_time,
            "ip": ip,
            "cpu": f"CPU: {cpu_usage}%",
            "temp": f"T: {temp:.1f}C",
            "npu": npu_status
        }

    def update_display(self, black_img, red_img):
        # Data Transmission 1 (Black)
        self.send_command(0x10)
        buf = self.get_buffer(black_img)
        self.spi.writebytes(buf)
            
        # Data Transmission 2 (Red)
        self.send_command(0x13)
        buf = self.get_buffer(red_img)
        self.spi.writebytes(buf)
            
        self.send_command(0x12) # DISPLAY_REFRESH
        self.wait_until_idle()

    def get_buffer(self, image):
        # BWR displays usually expect 1 bit per pixel, MSB first
        buf = [0xFF] * (int(WIDTH / 8) * HEIGHT)
        image_monochrome = image.convert('1')
        pixels = image_monochrome.load()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if pixels[x, y] == 0: # Black/Red pixel (active)
                    buf[int(x / 8) + y * int(WIDTH / 8)] &= ~(0x80 >> (x % 8))
        return buf

    def render(self):
        stats = self.get_stats()
        black_img = Image.new('1', (WIDTH, HEIGHT), 255)
        red_img = Image.new('1', (WIDTH, HEIGHT), 255)
        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)
        
        # Red Header
        draw_red.rectangle((0, 0, WIDTH, 30), fill=0)
        draw_red.text((10, 8), "ZEROBOT", fill=255)
        
        # Black Stats
        draw_black.text((10, 40), f"TIME: {stats['time']}", fill=0)
        draw_black.text((10, 60), f"IP  : {stats['ip']}", fill=0)
        draw_black.text((10, 80), f"CPU : {stats['cpu']}", fill=0)
        draw_black.text((10, 100), stats['temp'], fill=0)
        draw_black.text((10, 120), stats['npu'], fill=0)
        
        draw_black.line((0, 200, WIDTH, 200), fill=0)
        draw_black.text((10, 202), "iammhk/zerobot", fill=0)

        print(f"Updating Display: {stats['time']}")
        self.update_display(black_img, red_img)
        
    def start(self):
        self.init_display()
        try:
            while True:
                self.render()
                time.sleep(300) 
        except KeyboardInterrupt:
            print("Dashboard stopped.")
        finally:
            self.send_command(0x02) # Power OFF
            self.wait_until_idle()
            self.send_command(0x07) # Deep Sleep
            self.send_data(0xA5)
            self.req0.release()
            self.req1.release()
            self.spi.close()

if __name__ == "__main__":
    dash = EInkDashboard()
    dash.start()
