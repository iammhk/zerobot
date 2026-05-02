# hat_check.py - Diagnostic tool for Waveshare Servo HAT (PCA9685)
import smbus2
import time

# I2C Setup
BUS_NUM = 1
ADDR = 0x40

def check_i2c():
    try:
        bus = smbus2.SMBus(BUS_NUM)
        bus.read_byte_data(ADDR, 0x00)
        print(f"[OK] HAT detected at I2C address 0x{ADDR:02x}")
        return bus
    except Exception as e:
        print(f"[ERROR] Could not find HAT at 0x{ADDR:02x}. Check wiring/I2C enable.")
        print(f"Details: {e}")
        return None

def set_freq(bus, freq):
    prescale = int(25000000.0 / 4096.0 / freq - 1.0)
    old_mode = bus.read_byte_data(ADDR, 0x00)
    bus.write_byte_data(ADDR, 0x00, (old_mode & 0x7F) | 0x10)
    bus.write_byte_data(ADDR, 0xFE, prescale)
    bus.write_byte_data(ADDR, 0x00, old_mode)
    time.sleep(0.005)
    bus.write_byte_data(ADDR, 0x00, old_mode | 0x80)
    print(f"[OK] Frequency set to {freq}Hz")

def test_channel(bus, channel):
    print(f"Testing Channel {channel}...", end="\r")
    # Move to 45 deg
    off = int(1000 * 4096 * 50 / 1000000)
    bus.write_byte_data(ADDR, 0x08 + 4*channel, off & 0xFF)
    bus.write_byte_data(ADDR, 0x09 + 4*channel, off >> 8)
    time.sleep(0.1)
    # Move to 135 deg
    off = int(2000 * 4096 * 50 / 1000000)
    bus.write_byte_data(ADDR, 0x08 + 4*channel, off & 0xFF)
    bus.write_byte_data(ADDR, 0x09 + 4*channel, off >> 8)
    time.sleep(0.1)
    # Release
    bus.write_byte_data(ADDR, 0x08 + 4*channel, 0)
    bus.write_byte_data(ADDR, 0x09 + 4*channel, 0)

# Main Diagnostic
bus = check_i2c()
if bus:
    try:
        # Reset
        bus.write_byte_data(ADDR, 0x00, 0x00)
        set_freq(bus, 50)
        
        print("\nStarting Sequential Channel Test (0-15)...")
        print("Each servo should perform a tiny wiggle.")
        for i in range(16):
            test_channel(bus, i)
            time.sleep(0.05)
        
        print("\n[COMPLETE] All 16 channels addressed.")
        print("If a servo didn't move, check its power/plug orientation.")
        
    except KeyboardInterrupt:
        print("\nTest aborted.")
    finally:
        for i in range(16):
            bus.write_byte_data(ADDR, 0x08 + 4*i, 0)
            bus.write_byte_data(ADDR, 0x09 + 4*i, 0)
