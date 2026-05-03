# mvmt_sesame_walk.py - Ripple gait from Sesame Robot
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
    # Clamping for safety (simple)
    angle = max(0, min(180, angle))
    pulse_us = 500 + (angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)

def run(direction=1, cycles=1):
    try:
        def sa(ch, ang):
            if ch in [L1, R1, L2, R2]:
                home_val = HOME[ch]
                set_angle(ch, home_val + (ang - home_val) * direction)
            else:
                set_angle(ch, ang)

        for _ in range(cycles):
            # Initial Step
            sa(R3, 135); sa(L3, 45)
            sa(R2, 100); sa(L1, 25)
            time.sleep(0.1)

            # Core Loop (1 cycle)
            sa(R3, 135); sa(L3, 0); time.sleep(0.1)
            sa(L4, 135); sa(L2, 90); sa(R4, 0); sa(R1, 180); time.sleep(0.1)
            sa(R2, 45); sa(L1, 90); time.sleep(0.1)
            sa(R4, 45); sa(L4, 180); time.sleep(0.1)
            sa(R3, 180); sa(L3, 45); sa(R2, 90); sa(L1, 0); time.sleep(0.1)
            sa(L2, 135); sa(R1, 90); time.sleep(0.1)
            
        # Optional: Return home or stay? Remote usually calls multiple times.
        # But standalone script should probably return home.
        for ch, val in HOME.items(): set_angle(ch, val)
        time.sleep(0.2)
    finally:
        # Release if standalone, but remote might not want release between steps.
        # However, user asked for release in previous turn.
        for i in range(8):
            set_pwm(i, 0, 0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=int, default=1)
    parser.add_argument("--cycles", type=int, default=1)
    args = parser.parse_args()
    run(args.dir, args.cycles)
