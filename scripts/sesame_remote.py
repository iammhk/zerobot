# sesame_remote.py - Expressive Remote based on Sesame Robot sequences
import smbus2
import time
import sys
import tty
import termios
import subprocess
import os

# Add scripts directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# Colors & Formatting
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_CYAN = "\033[36m"
CLR_GREEN = "\033[32m"
CLR_RED = "\033[31m"
CLR_YELLOW = "\033[33m"
CLR_MAGENTA = "\033[35m"
CLR_BG_BLUE = "\033[44m"

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
    if channel in STATE["angles"]:
        STATE["angles"][channel] = int(safe_angle)

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def run_mvmt(name, args=None):
    """Run a movement script from the scripts folder."""
    try:
        script_path = os.path.join(os.path.dirname(__file__), f"mvmt_{name}.py")
        if os.path.exists(script_path):
            print(f"\n{CLR_BOLD}{CLR_CYAN}Executing {name}...{CLR_RESET}")
            cmd = [sys.executable, script_path]
            if args:
                cmd.extend(args)
            # We run as a subprocess to keep the remote and movement isolated
            subprocess.run(cmd)
        else:
            print(f"Error: Movement script mvmt_{name}.py not found.")
    except Exception as e:
        print(f"Error running movement {name}: {e}")

# --- POSES (Translated from sesame-robot) ---
def run_stand():
    for ch, val in HOME.items(): set_angle(ch, val)

def run_bow(): run_mvmt("bow")
def run_wave(): run_mvmt("wave")
def run_dance(): run_mvmt("bounce")
def run_shrug(): run_mvmt("shrug")
def run_pushup(): run_mvmt("pushups")
def run_cute(): run_mvmt("cute")
def run_crab(): run_mvmt("crab_display")
def run_stand():
    for ch, val in HOME.items(): set_angle(ch, val)

# --- Sesame Gaits ---
def run_walk(dir=1): run_mvmt("sesame_walk", ["--dir", str(dir), "--cycles", "1"])
def run_turn(dir=1): run_mvmt("sesame_turn", ["--dir", str(dir), "--cycles", "2"])

def run_swim(): run_mvmt("swim")
def run_point(): run_mvmt("point")
def run_worm(): run_mvmt("worm")
def run_shake(): run_mvmt("shake")
def run_freaky(): run_mvmt("freaky")

# --- Main UI ---
HISTORY = ["Sesame Remote Booted..."]
STATE = {
    "status": "ACTIVE", 
    "last_cmd": "NONE",
    "angles": {i: 90 for i in range(8)}
}

def print_ui():
    print("\033c", end="")
    status_color = CLR_GREEN if STATE["status"] == "ACTIVE" else CLR_RED
    
    print(f"{CLR_BG_BLUE}{CLR_BOLD}  SESAME ROBOT - ADVANCED REMOTE CONTROL  {CLR_RESET}")
    print(f"Status: {status_color}{STATE['status']}{CLR_RESET} | Last Command: {CLR_CYAN}{STATE['last_cmd']}{CLR_RESET}")
    print("-" * 50)
    
    # Servo Dashboard
    a = STATE["angles"]
    print(f"{CLR_BOLD}  SERVO ANGLES:{CLR_RESET}")
    print(f"  Front: L:{CLR_CYAN}{a[L1]:3}{CLR_RESET} R:{CLR_CYAN}{a[R1]:3}{CLR_RESET} | Knees: L:{CLR_YELLOW}{a[L3]:3}{CLR_RESET} R:{CLR_YELLOW}{a[R3]:3}{CLR_RESET}")
    print(f"  Hind:  L:{CLR_CYAN}{a[L2]:3}{CLR_RESET} R:{CLR_CYAN}{a[R2]:3}{CLR_RESET} | Knees: L:{CLR_YELLOW}{a[L4]:3}{CLR_RESET} R:{CLR_YELLOW}{a[R4]:3}{CLR_RESET}")
    print("-" * 50)
    
    print(f"{CLR_BOLD}  GAITS (WASD):{CLR_RESET}")
    print(f"  [W] {CLR_YELLOW}Walk Fwd{CLR_RESET}   [S] {CLR_YELLOW}Walk Bwd{CLR_RESET}   [A] {CLR_YELLOW}Turn Left{CLR_RESET}   [D] {CLR_YELLOW}Turn Right{CLR_RESET}")
    print("-" * 50)
    
    print(f"{CLR_BOLD}  EXPRESSIONS & GESTURES:{CLR_RESET}")
    print(f"  [1] Stand      [2] {CLR_RED}Rest{CLR_RESET}       [3] Bow")
    print(f"  [4] Wave       [5] Bounce     [6] Swim")
    print(f"  [7] Point      [8] Pushup     [9] Cute")
    print(f"  [0] Shrug      [C] Display    [V] Worm")
    print(f"  [Z] Freaky     [K] Shake      [Space] {CLR_RED}RELEASE{CLR_RESET}")
    print("-" * 50)
    
    print(f"{CLR_BOLD}  SYSTEM LOG:{CLR_RESET}")
    for i, h in enumerate(HISTORY[-5:]):
        prefix = " > " if i == len(HISTORY[-5:]) - 1 else "   "
        color = CLR_CYAN if i == len(HISTORY[-5:]) - 1 else CLR_RESET
        print(f"{color}{prefix}{h}{CLR_RESET}")
    print("-" * 50)
    print(f"  Press {CLR_BOLD}'X'{CLR_RESET} to Exit")

set_freq(50)
run_stand()

try:
    while True:
        print_ui()
        char = getch().lower()
        if char == 'x': break
        elif char == 'w': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "WALK_FWD"; run_walk(1); HISTORY.append("Walk Forward")
        elif char == 's': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "WALK_BWD"; run_walk(-1); HISTORY.append("Walk Backward")
        elif char == 'a': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "TURN_LEFT"; run_turn(1); HISTORY.append("Turn Left")
        elif char == 'd': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "TURN_RIGHT"; run_turn(-1); HISTORY.append("Turn Right")
        elif char == '1': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "STAND"; run_stand(); HISTORY.append("Stand")
        elif char == '2': 
            STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "REST";
            for i in range(8): set_angle(i, 90)
            HISTORY.append("Rest/Dead")
        elif char == '3': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "BOW"; run_bow(); HISTORY.append("Bow")
        elif char == '4': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "WAVE"; run_wave(); HISTORY.append("Wave")
        elif char == '5': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "BOUNCE"; run_dance(); HISTORY.append("Dance")
        elif char == '6': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "SWIM"; run_swim(); HISTORY.append("Swim")
        elif char == '7': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "POINT"; run_point(); HISTORY.append("Point")
        elif char == '8': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "PUSHUP"; run_pushup(); HISTORY.append("Pushup")
        elif char == '9': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "CUTE"; run_cute(); HISTORY.append("Cute")
        elif char == '0': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "SHRUG"; run_shrug(); HISTORY.append("Shrug")
        elif char == 'c': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "CRAB_DISPLAY"; run_crab(); HISTORY.append("Crab Display")
        elif char == 'v': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "WORM"; run_worm(); HISTORY.append("Worm")
        elif char == 'k': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "SHAKE"; run_shake(); HISTORY.append("Shake")
        elif char == 'z': STATE["status"] = "ACTIVE"; STATE["last_cmd"] = "FREAKY"; run_freaky(); HISTORY.append("Freaky")
        elif char == ' ': 
            STATE["status"] = "RELEASED"; STATE["last_cmd"] = "RELEASE";
            for i in range(16): set_pwm(i, 0, 0)
            HISTORY.append("RELEASE")
except KeyboardInterrupt:
    pass
finally:
    for i in range(16): set_pwm(i, 0, 0)
    print("\nSesame Remote Closed.")
