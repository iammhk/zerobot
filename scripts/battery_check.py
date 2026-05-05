# scripts/battery_check.py - Battery monitoring utility for Zerobot
# Supports Waveshare Servo HAT (B) with onboard INA219 sensor.
# Also provides reference ranges for 3S LiPo batteries.

import smbus2
import time
import sys

def read_ina219_voltage(bus, address=0x41):
    try:
        # Register 0x02 is Bus Voltage
        # Data is in bits 3-15, LSB is 4mV
        raw = bus.read_word_data(address, 0x02)
        # Byte swap because I2C is big-endian and read_word_data is little-endian on Pi
        raw = ((raw << 8) & 0xFF00) | (raw >> 8)
        
        voltage_raw = (raw >> 3) * 4 # mV
        return voltage_raw / 1000.0 # V
    except Exception:
        return None

def get_battery_status(voltage, cells=3):
    if voltage is None:
        return "Sensor Not Found", "N/A"
    
    # 3S LiPo Ranges
    full = 4.2 * cells
    nominal = 3.7 * cells
    low = 3.5 * cells
    critical = 3.3 * cells
    
    percentage = max(0, min(100, (voltage - critical) / (full - critical) * 100))
    
    if voltage > nominal:
        status = "HEALTHY"
    elif voltage > low:
        status = "LOW"
    else:
        status = "CRITICAL"
        
    return status, f"{percentage:.1f}%"

def main():
    print("--- Zerobot Battery Diagnostic ---")
    print("Checking for Waveshare Power Monitoring Hardware (INA219)...")
    
    try:
        bus = smbus2.SMBus(1)
    except:
        print("[ERROR] Could not open I2C bus. Is I2C enabled in raspi-config?")
        return

    # Check common INA219 addresses (0x41 is default for Waveshare Servo HAT B)
    # 0x45 is also common for some Waveshare Power HATs.
    addresses = [0x41, 0x45]
    found_addr = None
    
    for addr in addresses:
        try:
            bus.read_byte(addr)
            found_addr = addr
            print(f"[OK] Found INA219 sensor at address: {hex(addr)}")
            break
        except:
            continue
            
    if not found_addr:
        print("[INFO] No onboard battery sensor detected at 0x41 or 0x45.")
        print("Note: The standard blue Waveshare Servo Driver HAT does NOT have battery monitoring.")
        print("The black 'Version B' HAT (with OLED) includes this feature.")
        return

    try:
        while True:
            v = read_ina219_voltage(bus, found_addr)
            status, pct = get_battery_status(v)
            
            print(f"\rVoltage: {v:.2f}V | Charge: {pct} | Status: {status}    ", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()
