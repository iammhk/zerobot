# sesame_remote.py - Advanced TUI Remote using the 'blessed' library
import smbus2
import time
import sys
import subprocess
import os
from blessed import Terminal

# Add scripts directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from dsply_xprsn import DsplyExpressions
expr = DsplyExpressions() # Initialize LCD

# I2C Setup
try:
    BUS = smbus2.SMBus(1)
    ADDR = 0x40
except:
    BUS = None
    ADDR = 0x40

# --- Channel Mapping ---
L1, R1, L2, R2 = 0, 1, 2, 3
L3, R3, L4, R4 = 4, 5, 6, 7
HOME = { L1: 45, R1: 135, L2: 135, R2: 45, L3: 45, R3: 135, L4: 135, R4: 45 }
LIMITS = {i: (0, 180) for i in range(8)}
LIMITS[L1] = (0, 90); LIMITS[R1] = (90, 180)
LIMITS[L2] = (90, 180); LIMITS[R2] = (0, 90)

# --- State ---
term = Terminal()
HISTORY = ["System Initialized"]
STATE = {
    "status": "ACTIVE",
    "last_cmd": "NONE",
    "angles": {i: 90 for i in range(8)},
    "running_script": False,
    "last_blink": time.time(),
    "blink_interval": 5.0
}

def set_pwm(channel, on, off):
    if BUS:
        BUS.write_byte_data(ADDR, 0x06 + 4*channel, on & 0xFF)
        BUS.write_byte_data(ADDR, 0x07 + 4*channel, on >> 8)
        BUS.write_byte_data(ADDR, 0x08 + 4*channel, off & 0xFF)
        BUS.write_byte_data(ADDR, 0x09 + 4*channel, off >> 8)

def set_angle(channel, angle):
    min_a, max_a = LIMITS.get(channel, (0, 180))
    safe_angle = max(min_a, min(max_a, angle))
    pulse_us = 500 + (safe_angle / 180.0) * 2000
    off = int(pulse_us * 4096 * 50 / 1000000)
    set_pwm(channel, 0, off)
    if channel in STATE["angles"]:
        STATE["angles"][channel] = int(safe_angle)

def run_mvmt(name, args=None):
    script_path = os.path.join(os.path.dirname(__file__), f"mvmt_{name}.py")
    if os.path.exists(script_path):
        STATE["running_script"] = True
        draw_dynamic_ui()
        cmd = [sys.executable, script_path]
        if args: cmd.extend(args)
        # We use capture_output to keep the UI clean
        subprocess.run(cmd, capture_output=True)
        STATE["running_script"] = False
        STATE["status"] = "RELEASED" # Scripts release at end
        draw_static_ui()
        expr.happy()
    else:
        HISTORY.append(f"Error: {name} not found")

def draw_static_ui():
    """Draws labels and frames once."""
    print(term.home + term.clear)
    header_text = term.center(" SESAME ROBOT - BLESSED DASHBOARD ")
    print(term.black_on_cyan(term.bold(header_text)))
    print(term.move_y(5) + term.bold("  [ GAITS ]") + term.move_x(35) + term.bold("[ SERVO TELEMETRY ]"))
    print(term.move_y(6) + "  W: Walk Fwd" + term.move_x(37) + "Front L:        R:")
    print(term.move_y(7) + "  S: Walk Bwd" + term.move_x(37) + "Hind  L:        R:")
    print(term.move_y(8) + "  A: Turn Left" + term.move_x(35) + term.bold("[ KNEE POSITIONS ]"))
    print(term.move_y(9) + "  D: Turn Right" + term.move_x(37) + "Front L:        R:")
    print(term.move_y(10) + term.move_x(37) + "Hind  L:        R:")
    print(term.move_y(12) + term.bold("  [ GESTURES & POSES ]"))
    grid = [["1: Stand", "4: Wave", "7: Point", "0: Shrug"], ["2: Rest", "5: Bounce", "8: Pushup", "C: Display"], ["3: Bow", "6: Swim", "9: Cute", "V: Worm"], ["Z: Freaky", "K: Shake", "SPACE: Release", "X: Exit"]]
    for i, row in enumerate(grid):
        print(term.move_y(13+i) + "  " + "   ".join([f"{item:12}" for item in row]))
    print(term.move_y(18) + term.bold("  [ RECENT ACTIVITY ]"))
    print(term.move_y(term.height - 1) + term.center(term.dim + "Use Keyboard to Control | Zerobot Project 2026"))

def draw_dynamic_ui():
    """Updates only the values on the screen."""
    status_clr = term.green if STATE["status"] == "ACTIVE" else term.red
    with term.location(0, 3):
        print(term.clear_eol + f" Status: {term.bold(status_clr(STATE['status']))}  |  Last: {term.bold_yellow(STATE['last_cmd'])}")
    if STATE["running_script"]:
        with term.location(30, 3): print(term.blink_magenta("EXECUTING..."))
    # Servo Angles
    with term.location(46, 6): print(term.cyan(f"{STATE['angles'][L1]:3}"))
    with term.location(54, 6): print(term.cyan(f"{STATE['angles'][R1]:3}"))
    with term.location(46, 7): print(term.cyan(f"{STATE['angles'][L2]:3}"))
    with term.location(54, 7): print(term.cyan(f"{STATE['angles'][R2]:3}"))
    with term.location(46, 9): print(term.yellow(f"{STATE['angles'][L3]:3}"))
    with term.location(54, 9): print(term.yellow(f"{STATE['angles'][R3]:3}"))
    with term.location(46, 10): print(term.yellow(f"{STATE['angles'][L4]:3}"))
    with term.location(54, 10): print(term.yellow(f"{STATE['angles'][R4]:3}"))
    for i, msg in enumerate(HISTORY[-4:]):
        with term.location(3, 19 + i): print(term.clear_eol + f"{term.dim}> {msg}")

def main():
    if BUS:
        # Reset PCA9685 and set freq
        try:
            BUS.write_byte_data(ADDR, 0x00, 0x00)
            prescale = int(25000000.0 / 4096.0 / 50 - 1.0)
            old_mode = BUS.read_byte_data(ADDR, 0x00)
            BUS.write_byte_data(ADDR, 0x00, (old_mode & 0x7F) | 0x10)
            BUS.write_byte_data(ADDR, 0xFE, prescale)
            BUS.write_byte_data(ADDR, 0x00, old_mode)
            time.sleep(0.005)
            BUS.write_byte_data(ADDR, 0x00, old_mode | 0x80)
        except: pass
    
    # Wake up and stand up
    expr.wakeup()
    for ch, val in HOME.items(): set_angle(ch, val)
    
    with term.cbreak(), term.hidden_cursor():
        draw_static_ui()
        while True:
            draw_dynamic_ui()
            key = term.inkey(timeout=0.1)
            
            if not key: 
                # Random Idle Blink
                if time.time() - STATE["last_blink"] > STATE["blink_interval"] and STATE["status"] == "ACTIVE":
                    expr.blink()
                    STATE["last_blink"] = time.time()
                    STATE["blink_interval"] = 3.0 + (5.0 * (1.0 - (1.0 / (1.0 + time.time() % 10)))) # Randomize next
                continue
            
            char = key.lower()
            # Reset expression to happy on any movement/active key if we were sleeping
            if STATE["status"] == "RELEASED" and char != ' ' and char != 'x':
                expr.happy()
                STATE["status"] = "ACTIVE"

            if char == 'x': break
            elif char == 'w': STATE["status"]="ACTIVE"; STATE["last_cmd"]="WALK_FWD"; run_mvmt("sesame_walk", ["--dir","1"]); HISTORY.append("Walk Forward")
            elif char == 's': STATE["status"]="ACTIVE"; STATE["last_cmd"]="WALK_BWD"; run_mvmt("sesame_walk", ["--dir","-1"]); HISTORY.append("Walk Backward")
            elif char == 'a': STATE["status"]="ACTIVE"; STATE["last_cmd"]="TURN_LEFT"; run_mvmt("sesame_turn", ["--dir","1"]); HISTORY.append("Turn Left")
            elif char == 'd': STATE["status"]="ACTIVE"; STATE["last_cmd"]="TURN_RIGHT"; run_mvmt("sesame_turn", ["--dir","-1"]); HISTORY.append("Turn Right")
            elif char == '1': STATE["status"]="ACTIVE"; STATE["last_cmd"]="STAND"; [set_angle(ch, val) for ch, val in HOME.items()]; HISTORY.append("Stand"); expr.happy()
            elif char == '2': STATE["status"]="ACTIVE"; STATE["last_cmd"]="REST"; [set_angle(i, 90) for i in range(8)]; HISTORY.append("Resting")
            elif char == '3': STATE["status"]="ACTIVE"; STATE["last_cmd"]="BOW"; expr.happy(looking="down"); run_mvmt("bow"); HISTORY.append("Bowing")
            elif char == '4': STATE["status"]="ACTIVE"; STATE["last_cmd"]="WAVE"; expr.wink(); run_mvmt("wave"); HISTORY.append("Waving")
            elif char == '5': STATE["status"]="ACTIVE"; STATE["last_cmd"]="BOUNCE"; expr.happy(); run_mvmt("bounce"); HISTORY.append("Bouncing")
            elif char == '6': STATE["status"]="ACTIVE"; STATE["last_cmd"]="SWIM"; expr.happy(); run_mvmt("swim"); HISTORY.append("Swimming")
            elif char == '7': STATE["status"]="ACTIVE"; STATE["last_cmd"]="POINT"; expr.happy(); run_mvmt("point"); HISTORY.append("Pointing")
            elif char == '8': STATE["status"]="ACTIVE"; STATE["last_cmd"]="PUSHUP"; expr.happy(); run_mvmt("pushups"); HISTORY.append("Pushups")
            elif char == '9': STATE["status"]="ACTIVE"; STATE["last_cmd"]="CUTE"; expr.love(); run_mvmt("cute"); HISTORY.append("Cute Mode")
            elif char == '0': STATE["status"]="ACTIVE"; STATE["last_cmd"]="SHRUG"; expr.pondering(); run_mvmt("shrug"); HISTORY.append("Shrugging")
            elif char == 'c': STATE["status"]="ACTIVE"; STATE["last_cmd"]="CRAB"; run_mvmt("crab_display"); HISTORY.append("Crab Display")
            elif char == 'v': STATE["status"]="ACTIVE"; STATE["last_cmd"]="WORM"; run_mvmt("worm"); HISTORY.append("Worming")
            elif char == 'k': STATE["status"]="ACTIVE"; STATE["last_cmd"]="SHAKE"; run_mvmt("shake"); HISTORY.append("Shaking")
            elif char == 'z': STATE["status"]="ACTIVE"; STATE["last_cmd"]="FREAKY"; run_mvmt("freaky"); HISTORY.append("Freaky Mode"); expr.angry()
            elif char == ' ': 
                STATE["status"]="RELEASED"; STATE["last_cmd"]="RELEASE";
                for i in range(16): set_pwm(i, 0, 0)
                HISTORY.append("Motors Released")
                expr.sleeping()

    # Final Release
    for i in range(16): set_pwm(i, 0, 0)
    print(term.clear + "Remote closed safely.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        for i in range(16): set_pwm(i, 0, 0)
        sys.exit(0)
