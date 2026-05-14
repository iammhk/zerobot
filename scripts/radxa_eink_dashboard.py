# scripts/radxa_eink_dashboard.py - System status dashboard for Zerobot on Radxa E-Ink Display
# Optimized for Waveshare 2.13" E-Ink BWR V4 (250x122)

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

# Display Constants for V4
WIDTH = 122
HEIGHT = 250

# Pin Mapping for Radxa A7Z
RST_PIN = 33   # PIN_11 on gpiochip0
BUSY_PIN = 313 # PIN_18 on gpiochip0
DC_PIN = 5     # PIN_22 on gpiochip1

class EInkDashboard:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(1, 0)
        self.spi.max_speed_hz = 2000000
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
        time.sleep(0.01)
        self.req0.set_value(RST_PIN, Value.ACTIVE)
        time.sleep(0.2)

    def send_command(self, command):
        self.req1.set_value(DC_PIN, Value.INACTIVE)
        self.spi.writebytes([command])

    def send_data(self, data):
        self.req1.set_value(DC_PIN, Value.ACTIVE)
        self.spi.writebytes([data])

    def send_data_array(self, data):
        self.req1.set_value(DC_PIN, Value.ACTIVE)
        self.spi.writebytes(data)

    def wait_until_idle(self):
        while self.req0.get_value(BUSY_PIN) == Value.ACTIVE:
            time.sleep(0.1)

    def init_display(self):
        print("Initializing Display (BWR V4)...")
        self.reset()
        self.wait_until_idle()
        
        self.send_command(0x12) # SWRESET
        self.wait_until_idle()
        
        self.send_command(0x01) # Driver output control
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x11) # Data entry mode
        self.send_data(0x03)
        
        self.send_command(0x44) # Set RAM X
        self.send_data(0x00)
        self.send_data(0x0F) # 122
        
        self.send_command(0x45) # Set RAM Y
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0xF9) # 250
        self.send_data(0x00)
        
        self.send_command(0x3C) # BorderWavefrom
        self.send_data(0x05)
        
        self.send_command(0x18) # Temperature sensor
        self.send_data(0x80)
        
        self.send_command(0x21) # Display update control
        self.send_data(0x80)
        self.send_data(0x80)
        
        self.wait_until_idle()

    def get_stats(self):
        current_time = time.strftime("%H:%M")
        
        # Wi-Fi SSID
        try:
            ssid = subprocess.check_output("nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2", shell=True).decode("utf-8").strip()
            if not ssid: ssid = "Offline"
        except:
            ssid = "Unknown"
            
        # IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "No IP"
            
        # CPU & RAM
        cpu_usage = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        ram_usage = f"RAM: {ram.percent}%"
        
        # Temp
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = float(f.read()) / 1000.0
        except:
            temp = 0.0
            
        npu_status = "NPU: OK" if os.path.exists("/dev/vipcore") else "NPU: OFF"
        
        return {
            "time": current_time,
            "ssid": ssid,
            "ip": ip,
            "cpu": f"CPU: {cpu_usage}%",
            "ram": ram_usage,
            "temp": f"T: {temp:.1f}C",
            "npu": npu_status
        }

    def update_display(self, black_img, red_img):
        # Set Cursor
        self.send_command(0x4E) # X
        self.send_data(0x00)
        self.send_command(0x4F) # Y
        self.send_data(0x00)
        self.send_data(0x00)
        
        # Send Black Data
        self.send_command(0x24)
        self.send_data_array(self.get_buffer(black_img))
            
        # Send Red Data
        self.send_command(0x26)
        self.send_data_array(self.get_buffer(red_img))
            
        # Refresh
        self.send_command(0x22)
        self.send_data(0xF7)
        self.send_command(0x20)
        self.wait_until_idle()

    def get_buffer(self, image):
        if image.width > image.height:
            image = image.rotate(90, expand=True)
        buf = bytearray(image.convert('1').tobytes('raw'))
        return list(buf)

    def render(self):
        stats = self.get_stats()
        black_img = Image.new('1', (WIDTH, HEIGHT), 255)
        red_img = Image.new('1', (WIDTH, HEIGHT), 255)
        draw_black = ImageDraw.Draw(black_img)
        draw_red = ImageDraw.Draw(red_img)
        
        # Dashboard Layout
        # Red Header with Time
        draw_red.rectangle((0, 0, WIDTH, 35), fill=0)
        draw_red.text((15, 12), f"ZEROBOT | {stats['time']}", fill=255)
        
        # Network Info
        draw_black.text((10, 50), f"WiFi: {stats['ssid']}", fill=0)
        draw_black.text((10, 65), f"IP: {stats['ip']}", fill=0)
        
        # System Stats
        draw_black.line((10, 85, WIDTH-10, 85), fill=0)
        draw_black.text((15, 100), stats['cpu'], fill=0)
        draw_black.text((15, 115), stats['ram'], fill=0)
        draw_black.text((15, 130), stats['temp'], fill=0)
        draw_black.text((15, 145), stats['npu'], fill=0)
        
        # Footer
        draw_black.line((10, 230, WIDTH-10, 230), fill=0)
        draw_black.text((15, 235), "iammhk/zerobot", fill=0)

        print(f"Updating Display: {stats['time']} | {stats['ssid']} | {stats['ram']}")
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
            self.send_command(0x10) # Deep Sleep
            self.send_data(0x01)
            self.req0.release()
            self.req1.release()
            self.spi.close()

if __name__ == "__main__":
    dash = EInkDashboard()
    dash.start()
