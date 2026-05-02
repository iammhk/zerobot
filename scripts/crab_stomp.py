# crab_stomp.py - Stomping movement for the Crab-Bot
import smbus2
import time

# I2C Setup
BUS = smbus2.SMBus(1)
ADDR = 0x40

# --- Channel Mapping ---
L3, R3 = 4, 5 # Front Knees

# Standing Home Position
HOME = { 4: 45, 5: 135 }

def set_pwm(channel, on, off):
    BUS.write_byte_data(ADDR, 0x06 + 4*channel, on & 0xFF)
    BUS.write_byte_data(ADDR, 0x07 + 4*channel, on >> 8)
    BUS.write_byte_data(ADDR, 0x08 + 4*channel, off & 0xFF)
    BUS.write_byte_data(ADDR, 0x09 + 4*channel, off >> 8)

def set_freq(freq):
    prescale = int(25000000.0 / 4096.0 / freq - 1.0)
    old_mode = BUS.read_byte_data(ADDR, 0x00)
    BUS.write_byte_data(ADDR, 0x00, (old_mode & 0x7F) | 0x10)
    BUS.write_byte_data(ADDR, 0xFE, prescale)
    BUS.write_byte_data(ADDR, 0x00, old_mode)
    time.sleep(0.005)
    BUS.write_byte_data(ADDR, 0x00, old_mode | 0x80)

def set_angle(channel, angle):
    pulse_us = 500 + (angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)

try:
    set_freq(50)
    print("Standing up...")
    set_angle(4, 45); set_angle(5, 135)
    time.sleep(1)

    print("Stomping!")
    for _ in range(5):
        # Stomp Left
        set_angle(4, 160); time.sleep(0.15) # Lift
        set_angle(4, 10); time.sleep(0.1)  # Slam
        set_angle(4, 45); time.sleep(0.1)  # Reset
        
        # Stomp Right
        set_angle(5, 20); time.sleep(0.15)  # Lift
        set_angle(5, 170); time.sleep(0.1) # Slam
        set_angle(5, 135); time.sleep(0.1) # Reset

    time.sleep(0.5)
    for i in range(8): set_pwm(i, 0, 0)

except KeyboardInterrupt:
    for i in range(8): set_pwm(i, 0, 0)
