# recalibrate_servos.py - Interactive tool to map servo channels to labels
# This script helps identify which physical servo is connected to which HAT channel (0-7).

import smbus2
import time
import sys

# I2C Setup
BUS = smbus2.SMBus(1)
ADDR = 0x40

def set_pwm(channel, on, off):
    try:
        BUS.write_byte_data(ADDR, 0x06 + 4*channel, on & 0xFF)
        BUS.write_byte_data(ADDR, 0x07 + 4*channel, on >> 8)
        BUS.write_byte_data(ADDR, 0x08 + 4*channel, off & 0xFF)
        BUS.write_byte_data(ADDR, 0x09 + 4*channel, off >> 8)
    except:
        pass

def set_freq(freq):
    prescale = int(25000000.0 / 4096.0 / freq - 1.0)
    old_mode = BUS.read_byte_data(ADDR, 0x00)
    BUS.write_byte_data(ADDR, 0x00, (old_mode & 0x7F) | 0x10)
    BUS.write_byte_data(ADDR, 0xFE, prescale)
    BUS.write_byte_data(ADDR, 0x00, old_mode)
    time.sleep(0.005)
    BUS.write_byte_data(ADDR, 0x00, old_mode | 0x80)

def set_angle(channel, angle):
    # 500us to 2500us pulse width
    pulse_us = 500 + (angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)

def init_hat():
    BUS.write_byte_data(ADDR, 0x01, 0x04)
    BUS.write_byte_data(ADDR, 0x00, 0x01)
    time.sleep(0.005)
    set_freq(50)

def main():
    try:
        init_hat()
    except Exception as e:
        print(f"Error: Could not initialize I2C HAT: {e}")
        return

    print("--- Zerobot Servo Recalibration Tool ---")
    print("Moving all servos to 45 degrees (Safe Start)...")
    for i in range(8):
        set_angle(i, 45)
    time.sleep(1)

    mapping = {}
    
    try:
        for i in range(8):
            print(f"\n>>> Identifying Channel {i}...")
            # Nudge the servo
            for _ in range(2):
                set_angle(i, 80)
                time.sleep(0.3)
                set_angle(i, 45)
                time.sleep(0.3)
            
            label = input(f"Which servo moved? (e.g. R1, L3, etc.) or 'skip': ").strip().upper()
            if label != 'SKIP':
                mapping[label] = i
            
        print("\n--- Recalibration Complete ---")
        print("Final Mapping (to be updated in your scripts):")
        for label, channel in sorted(mapping.items()):
            print(f"{label} = {channel}")
            
    except KeyboardInterrupt:
        print("\nAborting...")
    finally:
        print("Releasing all servos.")
        for i in range(16):
            set_pwm(i, 0, 0)

if __name__ == "__main__":
    main()
