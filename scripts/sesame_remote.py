# sesame_remote.py - Expressive Remote based on Sesame Robot sequences
import smbus2
import time
import sys
import tty
import termios

# I2C Setup
BUS = smbus2.SMBus(1)
ADDR = 0x40

# --- USER Channel Mapping ---
# 0:L1, 1:R1, 2:L2, 3:R2 (Shoulders)
# 4:L3, 5:R3, 6:L4, 7:R4 (Knees)
L1, R1, L2, R2 = 0, 1, 2, 3
L3, R3, L4, R4 = 4, 5, 6, 7
ALL_SERVOS = [0, 1, 2, 3, 4, 5, 6, 7]

# --- HARD LIMITS ---
LIMITS = {i: (0, 180) for i in range(8)}
# Shoulder safety (mirroring your BODY.md)
LIMITS[L1] = (0, 90); LIMITS[R1] = (90, 180)
LIMITS[L2] = (90, 180); LIMITS[R2] = (0, 90)

# Sesame Stand/Home Equivalents
HOME = { 
    L1: 45, R1: 135,
    L2: 135, R2: 45,
    L3: 45, R3: 135,
    L4: 135, R4: 45 
}

# --- Low Level ---
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
    min_a, max_a = LIMITS.get(channel, (0, 180))
    safe_angle = max(min_a, min(max_a, angle))
    pulse_us = 500 + (safe_angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# --- POSES (Translated from sesame-robot) ---
def run_stand():
    for ch, val in HOME.items(): set_angle(ch, val)

def run_bow():
    set_angle(L1, 0); set_angle(R1, 180)
    set_angle(L3, 10); set_angle(R3, 170)
    set_angle(L2, 180); set_angle(R2, 0)
    set_angle(L4, 180); set_angle(R4, 0)
    time.sleep(1)
    set_angle(L3, 90); set_angle(R3, 90)
    time.sleep(2)
    run_stand()

def run_wave():
    run_stand()
    time.sleep(0.2)
    # Lean right/back
    set_angle(R3, 170); set_angle(L4, 10); set_angle(R4, 170)
    time.sleep(0.3)
    set_angle(L3, 170) # Lift FL knee high
    time.sleep(0.3)
    for _ in range(4):
        set_angle(L1, 10); time.sleep(0.3)
        set_angle(L1, 80); time.sleep(0.3)
    run_stand()

def run_dance():
    for _ in range(5):
        set_angle(L3, 10); set_angle(L4, 10); set_angle(R3, 170); set_angle(R4, 170)
        time.sleep(0.3)
        set_angle(L3, 65); set_angle(L4, 65); set_angle(R3, 115); set_angle(R4, 115)
        time.sleep(0.3)
    run_stand()

def run_shrug():
    set_angle(L3, 90); set_angle(R3, 90); set_angle(L4, 90); set_angle(R4, 90)
    time.sleep(1)
    set_angle(L3, 180); set_angle(L4, 0); set_angle(R3, 0); set_angle(R4, 180)
    time.sleep(1.5)
    run_stand()

def run_pushup():
    set_angle(L1, 0); set_angle(R1, 180)
    for _ in range(4):
        set_angle(L3, 10); set_angle(R3, 170); time.sleep(0.6)
        set_angle(L3, 90); set_angle(R3, 90); time.sleep(0.5)
    run_stand()

def run_cute():
    set_angle(L2, 160); set_angle(R2, 20); set_angle(R4, 180); set_angle(L4, 0)
    set_angle(L1, 0); set_angle(R1, 180); set_angle(L3, 180); set_angle(R3, 0)
    for _ in range(5):
        set_angle(R4, 180); set_angle(L4, 45); time.sleep(0.3)
        set_angle(R4, 135); set_angle(L4, 0); time.sleep(0.3)
    run_stand()

def run_crab():
    for _ in range(5):
        set_angle(R4, 45); set_angle(R3, 135); set_angle(L3, 0); set_angle(L4, 180)
        time.sleep(0.3)
        set_angle(R4, 0); set_angle(R3, 180); set_angle(L3, 45); set_angle(L4, 135)
        time.sleep(0.3)
    run_stand()

# --- Sesame Gaits ---
def run_walk(dir=1):
    # Sesame ripple gait translated
    # Initial Step
    set_angle(R3, 135); set_angle(L3, 45)
    set_angle(R2, 100); set_angle(L1, 25)
    time.sleep(0.1)

    # Core Loop (1 cycle)
    set_angle(R3, 135); set_angle(L3, 0); time.sleep(0.1)
    set_angle(L4, 135); set_angle(L2, 90); set_angle(R4, 0); set_angle(R1, 180); time.sleep(0.1)
    set_angle(R2, 45); set_angle(L1, 90); time.sleep(0.1)
    set_angle(R4, 45); set_angle(L4, 180); time.sleep(0.1)
    set_angle(R3, 180); set_angle(L3, 45); set_angle(R2, 90); set_angle(L1, 0); time.sleep(0.1)
    set_angle(L2, 135); set_angle(R1, 90); time.sleep(0.1)

def run_turn(dir=1):
    # Simplified Sesame turn
    for _ in range(2):
        if dir > 0: # Left
            set_angle(R3, 135); set_angle(L4, 135); time.sleep(0.1)
            set_angle(R1, 180); set_angle(L2, 180); time.sleep(0.1)
            set_angle(R3, 180); set_angle(L4, 180); time.sleep(0.1)
            set_angle(R1, 135); set_angle(L2, 135); time.sleep(0.1)
        else: # Right
            set_angle(R4, 45); set_angle(L3, 45); time.sleep(0.1)
            set_angle(R2, 0); set_angle(L1, 0); time.sleep(0.1)
            set_angle(R4, 0); set_angle(L3, 0); time.sleep(0.1)
            set_angle(R2, 45); set_angle(L1, 45); time.sleep(0.1)

def run_swim():
    for _ in range(4):
        set_angle(R1, 135); set_angle(R2, 45); set_angle(L1, 45); set_angle(L2, 135); time.sleep(0.4)
        set_angle(R1, 90); set_angle(R2, 90); set_angle(L1, 90); set_angle(L2, 90); time.sleep(0.4)
    run_stand()

def run_point():
    set_angle(L2, 180); set_angle(R1, 135); set_angle(R2, 45); set_angle(L4, 180)
    set_angle(L1, 0); set_angle(L3, 180); set_angle(R4, 0); set_angle(R3, 180)
    time.sleep(2.0)
    run_stand()

def run_worm():
    set_angle(R1, 180); set_angle(R2, 0); set_angle(L1, 0); set_angle(L2, 180)
    set_angle(R4, 90); set_angle(R3, 90); set_angle(L3, 90); set_angle(L4, 90)
    time.sleep(0.2)
    for _ in range(5):
        set_angle(R3, 45); set_angle(L3, 135); set_angle(R4, 45); set_angle(L4, 135); time.sleep(0.3)
        set_angle(R3, 135); set_angle(L3, 45); set_angle(R4, 135); set_angle(L4, 45); time.sleep(0.3)
    run_stand()

def run_shake():
    run_stand()
    time.sleep(0.2)
    set_angle(R1, 135); set_angle(L1, 45); set_angle(L3, 90); set_angle(R3, 90)
    set_angle(L2, 90); set_angle(R2, 90)
    time.sleep(0.2)
    for _ in range(5):
        set_angle(R4, 45); set_angle(L4, 135); time.sleep(0.15)
        set_angle(R4, 0); set_angle(L4, 180); time.sleep(0.15)
    run_stand()

def run_freaky():
    run_stand()
    time.sleep(0.2)
    set_angle(L1, 0); set_angle(R1, 180); set_angle(L2, 180); set_angle(R2, 0)
    set_angle(R4, 90); set_angle(R3, 0)
    time.sleep(0.2)
    for _ in range(6):
        set_angle(R3, 25); time.sleep(0.2)
        set_angle(R3, 0); time.sleep(0.2)
    run_stand()

# --- Main UI ---
HISTORY = ["Sesame Remote Booted..."]
def print_ui():
    print("\033c", end="")
    print("====================================================")
    print("      🦀 SESAME ROBOT - PYTHON REMOTE 🦀          ")
    print("====================================================")
    print("  [1] Stand     [2] Rest/Dead   [3] Bow           ")
    print("  [4] Wave      [5] Dance       [6] Swim          ")
    print("  [7] Point     [8] Pushup      [9] Cute          ")
    print("  [0] Shrug     [C] Crab        [V] Worm          ")
    print("  [Z] Freaky    [K] Shake       [Space] Release   ")
    print("====================================================")
    print("  MOVEMENTS: W/A/S/D (Walk & Turn)                ")
    print("====================================================")
    print("  LOG:")
    for h in HISTORY[-3:]: print(f"   > {h}")
    print("====================================================")

set_freq(50)
run_stand()

try:
    while True:
        print_ui()
        char = getch().lower()
        if char == 'x': break
        elif char == 'w': run_walk(1); HISTORY.append("Walk Forward")
        elif char == 's': run_walk(-1); HISTORY.append("Walk Backward")
        elif char == 'a': run_turn(1); HISTORY.append("Turn Left")
        elif char == 'd': run_turn(-1); HISTORY.append("Turn Right")
        elif char == '1': run_stand(); HISTORY.append("Stand")
        elif char == '2': 
            for i in range(8): set_angle(i, 90)
            HISTORY.append("Rest/Dead")
        elif char == '3': run_bow(); HISTORY.append("Bow")
        elif char == '4': run_wave(); HISTORY.append("Wave")
        elif char == '5': run_dance(); HISTORY.append("Dance")
        elif char == '6': run_swim(); HISTORY.append("Swim")
        elif char == '7': run_point(); HISTORY.append("Point")
        elif char == '8': run_pushup(); HISTORY.append("Pushup")
        elif char == '9': run_cute(); HISTORY.append("Cute")
        elif char == '0': run_shrug(); HISTORY.append("Shrug")
        elif char == 'c': run_crab(); HISTORY.append("Crab Display")
        elif char == 'v': run_worm(); HISTORY.append("Worm")
        elif char == 'k': run_shake(); HISTORY.append("Shake")
        elif char == 'z': run_freaky(); HISTORY.append("Freaky")
        elif char == ' ': 
            for i in range(16): set_pwm(i, 0, 0)
            HISTORY.append("RELEASE")
except KeyboardInterrupt:
    pass
finally:
    for i in range(16): set_pwm(i, 0, 0)
    print("\nSesame Remote Closed.")
