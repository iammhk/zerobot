# crab_remote.py - Real-time terminal remote for the Crab-Bot
import smbus2
import time
import sys
import tty
import termios
import subprocess
import os

# Add scripts directory to path (optional, using subprocess for isolation)
SCRIPTS_DIR = os.path.dirname(__file__)

# I2C Setup
BUS = smbus2.SMBus(1)
ADDR = 0x40

# --- Channel Mapping ---
L1, R1, L2, R2 = 0, 1, 2, 3
L3, R3, L4, R4 = 4, 5, 6, 7
ALL_SERVOS = [0, 1, 2, 3, 4, 5, 6, 7]

# --- HARD LIMITS ---
LIMITS = {
    0: (0, 90),   1: (90, 180),
    2: (90, 180), 3: (0, 90),
    4: (0, 180),  5: (0, 180),
    6: (0, 180),  7: (0, 180)
}

# Neutral Home Position
HOME = { 0: 45, 1: 135, 2: 135, 3: 45, 4: 45, 5: 135, 6: 135, 7: 45 }

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

# --- Global State for UI ---
SERVO_STATE = {i: 90 for i in range(8)}
HISTORY = ["...", "...", "..."]

def update_history(cmd):
    global HISTORY
    HISTORY.append(cmd)
    if len(HISTORY) > 3:
        HISTORY.pop(0)

def set_angle(channel, angle):
    min_a, max_a = LIMITS.get(channel, (0, 180))
    safe_angle = max(min_a, min(max_a, angle))
    SERVO_STATE[channel] = int(safe_angle) # Cache for UI
    pulse_us = 500 + (safe_angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)

def move_home():
    for ch, val in HOME.items(): set_angle(ch, val)

def getch():
    """Read a single character from stdin without waiting for Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# --- Gait Functions ---
def step_trot(direction=1):
    swing, lift = 35, 45
    # Phase 1
    set_angle(4, HOME[4] + lift)
    set_angle(7, HOME[7] - lift)
    time.sleep(0.1)
    set_angle(0, HOME[0] - (swing * direction))
    set_angle(3, HOME[3] - (swing * direction))
    set_angle(1, HOME[1] - (swing * direction))
    set_angle(2, HOME[2] - (swing * direction))
    time.sleep(0.1)
    set_angle(4, HOME[4])
    set_angle(7, HOME[7])
    time.sleep(0.1)
    # Phase 2
    set_angle(5, HOME[5] + lift)
    set_angle(6, HOME[6] - lift)
    time.sleep(0.1)
    set_angle(1, HOME[1] + (swing * direction))
    set_angle(2, HOME[2] + (swing * direction))
    set_angle(0, HOME[0] + (swing * direction))
    set_angle(3, HOME[3] + (swing * direction))
    time.sleep(0.1)
    set_angle(5, HOME[5])
    set_angle(6, HOME[6])
    time.sleep(0.1)

def turn_inplace(dir=1):
    # Simplified turn
    for ch in [L1, R1, L2, R2]:
        mid_k = HOME[ch+4]
        lift = 40 if ch in [L1, R2] else -40
        set_angle(ch+4, mid_k + lift)
        time.sleep(0.08)
        set_angle(ch, HOME[ch] + (30 * dir))
        time.sleep(0.08)
        set_angle(ch+4, mid_k)
        time.sleep(0.08)
    for ch in [L1, R1, L2, R2]: set_angle(ch, HOME[ch])

def run_mvmt(name):
    """Run a movement script from the scripts folder."""
    try:
        script_path = os.path.join(SCRIPTS_DIR, f"mvmt_{name}.py")
        if os.path.exists(script_path):
            update_history(f"Running {name}...")
            subprocess.run([sys.executable, script_path])
            update_history(f"Finished {name}")
        else:
            update_history(f"Error: {name} not found")
    except Exception as e:
        update_history(f"Fail: {str(e)}")

# --- Main Interface ---
def print_ui(last_cmd="None"):
    print("\033c", end="") # Clear terminal
    print("====================================================")
    print("      🦀 ZEROBOT - CRAB COCKPIT v2.0 🦀           ")
    print("====================================================")
    print("      /\\  /\\          STATUS: Connected     ")
    print("     (  oo  )         MODE: Remote Control  ")
    print("     / vvvv \\                               ")
    print("====================================================")
    print("  [W] Forward    [S] Backward    [P] Pushups        ")
    print("  [A] Turn L     [D] Turn R      [L] Wave           ")
    print("  [Q] Scuttle L  [E] Scuttle R   [T] Stomp          ")
    print("  [U] Look Up    [J] Look Down   [F] Lay Flat       ")
    print("  [H] Home       [K/Space] Stop  [X] EXIT           ")
    print("====================================================")
    print("  SERVO DASHBOARD (Angles):                         ")
    
    # Dashboard Layout
    s = SERVO_STATE
    print(f"   L-Front: Sh[{s[0]:03}] Kn[{s[4]:03}] | R-Front: Sh[{s[1]:03}] Kn[{s[5]:03}]")
    print(f"   L-Hind:  Sh[{s[2]:03}] Kn[{s[6]:03}] | R-Hind:  Sh[{s[3]:03}] Kn[{s[7]:03}]")
    print("====================================================")
    print("  COMMAND LOG:")
    for h in HISTORY:
        print(f"   > {h}")
    print("====================================================")

# Init
set_freq(50)
move_home()

try:
    cmd_map = {
        'w': "Forward", 's': "Backward", 'a': "Turn Left", 'd': "Turn Right",
        'q': "Scuttle Left", 'e': "Scuttle Right", 'u': "Look Up", 'j': "Look Down",
        'p': "Pushups", 'l': "Wave", 'h': "Home", 'f': "Lay Flat", 't': "Stomp", ' ': "Stop/Release"
    }
    last_cmd = "Standing"
    
    while True:
        print_ui(last_cmd)
        char = getch().lower()
        
        if char == 'x': break
        
        last_cmd = cmd_map.get(char, f"Unknown ({char})")
        update_history(last_cmd)
        
        if char == 'w': step_trot(1)
        elif char == 's': step_trot(-1)
        elif char == 'h': move_home()
        elif char == 't': run_mvmt("stomp")
        elif char == 'f': run_mvmt("flat")
        elif char == 'a': turn_inplace(1)
        elif char == 'd': turn_inplace(-1)
        elif char == 'q': run_mvmt("scuttle_left")
        elif char == 'e': run_mvmt("scuttle_right")
        elif char == 'p': run_mvmt("pushups")
        elif char == 'l': run_mvmt("wave")
        elif char == 'u': run_mvmt("lookup")
        elif char == 'j': run_mvmt("lookdown")

except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"\nError: {e}")
finally:
    # Release all 16 possible channels on the HAT for safety
    for i in range(16):
        set_pwm(i, 0, 0)
    print("\nRemote Closed. All motors released.")
