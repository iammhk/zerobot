# mvmt_swim.py - Swimming movement sequence
import smbus2
import time

BUS = smbus2.SMBus(1)
ADDR = 0x40

L1, R1, L2, R2 = 0, 1, 2, 3
L3, R3, L4, R4 = 4, 5, 6, 7
HOME = {0:45, 1:135, 2:135, 3:45, 4:45, 5:135, 6:135, 7:45}

def set_pwm(channel, on, off):
    BUS.write_byte_data(ADDR, 0x06 + 4*channel, on & 0xFF)
    BUS.write_byte_data(ADDR, 0x07 + 4*channel, on >> 8)
    BUS.write_byte_data(ADDR, 0x08 + 4*channel, off & 0xFF)
    BUS.write_byte_data(ADDR, 0x09 + 4*channel, off >> 8)

def set_angle(channel, angle):
    pulse_us = 500 + (angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)

def run():
    print("Swimming...")
    for _ in range(4):
        set_angle(R1, 135); set_angle(R2, 45); set_angle(L1, 45); set_angle(L2, 135); time.sleep(0.4)
        set_angle(R1, 90); set_angle(R2, 90); set_angle(L1, 90); set_angle(L2, 90); time.sleep(0.4)
    for ch, val in HOME.items(): set_angle(ch, val)

if __name__ == "__main__":
    run()
