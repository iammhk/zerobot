# mvmt_sesame_turn.py - Turn logic from Sesame Robot
import smbus2
import time
import sys
import argparse

BUS = smbus2.SMBus(1)
ADDR = 0x40

L1, R1, L2, R2 = 0, 1, 2, 3
L3, R3, L4, R4 = 4, 5, 6, 7
HOME = { 
    L1: 45, R1: 135,
    L2: 135, R2: 45,
    L3: 45, R3: 135,
    L4: 135, R4: 45 
}

def set_pwm(channel, on, off):
    BUS.write_byte_data(ADDR, 0x06 + 4*channel, on & 0xFF)
    BUS.write_byte_data(ADDR, 0x07 + 4*channel, on >> 8)
    BUS.write_byte_data(ADDR, 0x08 + 4*channel, off & 0xFF)
    BUS.write_byte_data(ADDR, 0x09 + 4*channel, off >> 8)

def set_angle(channel, angle):
    angle = max(0, min(180, angle))
    pulse_us = 500 + (angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)

def run(direction=1, cycles=2):
    try:
        for _ in range(cycles):
            if direction > 0: # Left
                set_angle(R3, 135); set_angle(L4, 135); time.sleep(0.1)
                set_angle(R1, 180); set_angle(L2, 180); time.sleep(0.1)
                set_angle(R3, 180); set_angle(L4, 180); time.sleep(0.1)
                set_angle(R1, 135); set_angle(L2, 135); time.sleep(0.1)
            else: # Right
                set_angle(R4, 45); set_angle(L3, 45); time.sleep(0.1)
                set_angle(R2, 0); set_angle(L1, 0); time.sleep(0.1)
                set_angle(R4, 0); set_angle(L3, 0); time.sleep(0.1)
                set_angle(R2, 45); set_angle(L1, 45); time.sleep(0.1)
        
        for ch, val in HOME.items(): set_angle(ch, val)
        time.sleep(0.2)
    finally:
        for i in range(8):
            set_pwm(i, 0, 0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=int, default=1)
    parser.add_argument("--cycles", type=int, default=2)
    args = parser.parse_args()
    run(args.dir, args.cycles)
