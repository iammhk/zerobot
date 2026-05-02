# crab_remote.py - Real-time terminal remote for the Crab-Bot
import smbus2
import time
import sys
import tty
import termios

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

def set_angle(channel, angle):
    min_a, max_a = LIMITS.get(channel, (0, 180))
    safe_angle = max(min_a, min(max_a, angle))
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

# --- Main Interface ---
def print_ui(last_cmd="None"):
    print("\033c", end="") # Clear terminal
    print("==========================================")
    print("        CRAB-BOT REMOTE CONTROL           ")
    print("==========================================")
    print("  [W] Forward    [S] Backward             ")
    print("  [A] Turn Left  [D] Turn Right           ")
    print("  [Q] Scuttle L  [E] Scuttle R            ")
    print("  [U] Look Up    [J] Look Down            ")
    print("  [P] Pushups    [L] Wave                 ")
    print("  [T] Stomp      [F] Lay Flat             ")
    print("  [H] Home       [Space/K] Stop/Release   ")
    print("  [X] EXIT                                ")
    print("==========================================")
    print(f"  LAST COMMAND: {last_cmd}")
    print("==========================================")

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
        
        if char == 'w': step_trot(1)
        elif char == 's': step_trot(-1)
        elif char == 'h': move_home()
        elif char == 't':
            # Stomp
            for _ in range(3):
                set_angle(4, 160); time.sleep(0.12); set_angle(4, 10); time.sleep(0.1); set_angle(4, 45); time.sleep(0.1)
                set_angle(5, 20); time.sleep(0.12); set_angle(5, 170); time.sleep(0.1); set_angle(5, 135); time.sleep(0.1)
            move_home()
        elif char == 'f':
            # Lay Flat
            for i in range(30):
                o = i * 4
                set_angle(4, 45+o); set_angle(5, 135-o); set_angle(6, 135-o); set_angle(7, 45+o)
                time.sleep(0.02)
            for i in range(16): set_pwm(i, 0, 0)
        elif char == 'a': turn_inplace(1)
        elif char == 'd': turn_inplace(-1)
        elif char == 'q':
            # Scuttle Left
            set_angle(4, 160); set_angle(6, 20); time.sleep(0.15)
            set_angle(0, 5); set_angle(2, 175); time.sleep(0.15)
            set_angle(4, HOME[4]); set_angle(6, HOME[6]); time.sleep(0.15)
            set_angle(0, HOME[0]); set_angle(2, HOME[2]); time.sleep(0.2)
        elif char == 'e':
            # Scuttle Right
            set_angle(5, 20); set_angle(7, 160); time.sleep(0.15)
            set_angle(1, 175); set_angle(3, 5); time.sleep(0.15)
            set_angle(5, HOME[5]); set_angle(7, HOME[7]); time.sleep(0.15)
            set_angle(1, HOME[1]); set_angle(3, HOME[3]); time.sleep(0.2)
        elif char == 'p':
            for _ in range(3):
                set_angle(4, 10); set_angle(5, 170); time.sleep(0.4)
                set_angle(4, 80); set_angle(5, 100); time.sleep(0.4)
            move_home()
        elif char == 'l':
            # Wave sequence
            set_angle(5, 170); set_angle(6, 10); set_angle(7, 170); time.sleep(0.5)
            set_angle(4, 170); time.sleep(0.3)
            for _ in range(4):
                set_angle(0, 10); time.sleep(0.2); set_angle(0, 80); time.sleep(0.2)
            move_home()
        elif char == ' ' or char == 'k':
            last_cmd = "STOP/RELEASE"
            for i in range(8): set_pwm(i, 0, 0)
        elif char == 'u':
            for i in range(20):
                o = i * 2
                set_angle(4, 45-o); set_angle(5, 135+o); set_angle(6, 135+o); set_angle(7, 45-o)
                time.sleep(0.02)
        elif char == 'j':
            for i in range(20):
                o = i * 2
                set_angle(4, 45+o); set_angle(5, 135-o); time.sleep(0.02)

except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"\nError: {e}")
finally:
    # Release all 16 possible channels on the HAT for safety
    for i in range(16):
        set_pwm(i, 0, 0)
    print("\nRemote Closed. All motors released.")
