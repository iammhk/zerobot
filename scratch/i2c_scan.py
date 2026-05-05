# i2c_scan.py - Utility to scan the I2C bus for connected devices.
# Used to determine if battery sensors (like INA219) are present.

import smbus2

def scan_i2c():
    bus = smbus2.SMBus(1)
    found = []
    print("Scanning I2C bus 1...")
    for addr in range(0x03, 0x78):
        try:
            bus.read_byte(addr)
            found.append(hex(addr))
        except OSError:
            pass
    
    if found:
        print(f"Devices found at: {', '.join(found)}")
        if '0x40' in found:
            print(" - 0x40: PCA9685 (Servo Driver)")
        if '0x41' in found:
            print(" - 0x41: INA219 (Battery/Power Monitor - Likely HAT version B)")
        if '0x48' in found:
            print(" - 0x48: ADS1115 (ADC - Likely General Driver HAT)")
    else:
        print("No I2C devices found.")
    return found

if __name__ == "__main__":
    scan_i2c()
