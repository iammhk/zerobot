# sesame_remote.py - Advanced TUI Remote using the 'blessed' library
# Optimized for performance over SSH and Zero-Latency script execution.

import time
import sys, os
import importlib
import random
import threading
import subprocess
from blessed import Terminal

# Add root directory to path for zerobot imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo

try:
    import evdev
    from evdev import ecodes
except ImportError:
    evdev = None

# Add current directory to path for display and movement imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from dsply_xprsn import DsplyExpressions

# Initialize systems
term = Terminal()
expr = DsplyExpressions()

# --- State ---
HISTORY = ["System Initialized"]
STATE = {
    "status": "ACTIVE",
    "last_cmd": "NONE",
    "angles": {i: 90 for i in range(8)},
    "running_script": False,
    "last_blink": time.time(),
    "blink_interval": 5.0,
    "last_eye_move": time.time(),
    "remote_dev": None,
    "dirty": True,
    "last_ui_update": 0,
    "last_input_time": time.time(),
    "tilt_level": 0,
    "last_idle_mvmt": 0,
    "powersaving": False
}

# Cache for movement modules
MVMT_CACHE = {}

# --- Bluetooth Config ---
REMOTE_NAME_KEYWORDS = ["Consumer Control", "Remote", "Shutter", "Gamepad", "Keyboard", "VR-PARK", "MOCUTE", "XiaoMi", "Controller", "Input"]
BT_KEY_MAP = {
    "KEY_UP": 'w', "KEY_DOWN": 's', "KEY_LEFT": 'a', "KEY_RIGHT": 'd',
    "KEY_SELECT": '1', "KEY_HOMEPAGE": '2', "KEY_BACK": ' ', 
    "KEY_POWER": 'p', "KEY_SLEEP": 'p', "KEY_WAKEUP": 'p',
    "KEY_VOLUMEUP": '4', "KEY_VOLUMEDOWN": '3', "KEY_VIDEO": '6',
    "KEY_GREEN": '5', "KEY_VOICECOMMAND": '9', "KEY_APPSELECT": '7',
}

def find_remote():
    if not evdev: return None
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        if not devices:
            HISTORY.append("No input devices found")
            return None
        
        # Log all devices found for debugging
        dev_names = [d.name for d in devices]
        HISTORY.append(f"Found {len(devices)} devs: {', '.join(dev_names[:3])}")
        
        for keyword in REMOTE_NAME_KEYWORDS:
            for device in devices:
                if keyword.lower() in device.name.lower():
                    return device
    except Exception as e:
        HISTORY.append(f"Remote Search Error: {e}")
    return None

def set_angle(channel, angle):
    """Wrapper for servo.set_angle that updates UI state."""
    servo.set_angle(channel, angle)
    if channel in STATE["angles"]:
        min_a, max_a = servo.config.LIMITS.get(channel, (0, 180))
        safe_angle = max(min_a, min(max_a, angle))
        if STATE["angles"][channel] != int(safe_angle):
            STATE["angles"][channel] = int(safe_angle)
            STATE["dirty"] = True

def set_low_power(enabled):
    """Toggles CPU governor and HDMI power."""
    try:
        if enabled:
            # Set governor to powersave (600MHz)
            # Use sudo -n (non-interactive) to avoid hanging on password prompt
            cmd = "echo powersave | sudo -n tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
            subprocess.run(cmd, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Disable HDMI output (usually doesn't need sudo if in video group)
            subprocess.run(["vcgencmd", "display_power", "0"], check=False, stdout=subprocess.DEVNULL)
            # Disable SPI Display Backlight
            if hasattr(expr.eyes.disp, 'set_backlight'):
                expr.eyes.disp.set_backlight(False)
            STATE["powersaving"] = True
            HISTORY.append("🔋 Power Saving: ON (Display Off / CPU Low)")
        else:
            # Set governor back to ondemand
            cmd = "echo ondemand | sudo -n tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
            subprocess.run(cmd, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Enable HDMI output
            subprocess.run(["vcgencmd", "display_power", "1"], check=False, stdout=subprocess.DEVNULL)
            # Enable SPI Display Backlight
            if hasattr(expr.eyes.disp, 'set_backlight'):
                expr.eyes.disp.set_backlight(True)
            STATE["powersaving"] = False
            HISTORY.append("⚡ Power Saving: OFF (Resuming)")
            draw_static_ui() # Refresh screen after HDMI wake
    except Exception as e:
        HISTORY.append(f"Power Error: {e}")

def run_mvmt(name, kwargs=None):
    """Executes a movement by importing its module for zero-latency startup."""
    try:
        if name not in MVMT_CACHE:
            module_name = f"mvmt_{name}"
            # Modules are in the same directory as this script
            MVMT_CACHE[name] = importlib.import_module(module_name)
        
        module = MVMT_CACHE[name]
        
        STATE["running_script"] = True
        draw_dynamic_ui(force=True)
        
        # Call the module's run() function
        if kwargs:
            module.run(**kwargs)
        else:
            module.run()
            
        STATE["running_script"] = False
        if name != "idle":
            STATE["status"] = "RELEASED"
        STATE["dirty"] = True
        draw_static_ui()
        expr.happy()
        
    except Exception as e:
        HISTORY.append(f"Mvmt Error ({name}): {e}")
        STATE["running_script"] = False
        STATE["dirty"] = True

def draw_static_ui():
    """Draws labels and frames."""
    print(term.home + term.clear)
    header_text = term.center(" SESAME ROBOT - BLESSED DASHBOARD ")
    print(term.black_on_cyan(term.bold(header_text)))
    print(term.move_y(5) + term.bold("  [ GAITS ]") + term.move_x(35) + term.bold("[ SERVO TELEMETRY ]"))
    print(term.move_y(6) + "  W: Walk Fwd   Q: Look Up" + term.move_x(37) + "Front L:        R:")
    print(term.move_y(7) + "  S: Walk Bwd   E: Look Down" + term.move_x(37) + "Hind  L:        R:")
    print(term.move_y(8) + "  A: Turn Left" + term.move_x(35) + term.bold("[ KNEE POSITIONS ]"))
    print(term.move_y(9) + "  D: Turn Right" + term.move_x(37) + "Front L:        R:")
    print(term.move_y(10) + term.move_x(37) + "Hind  L:        R:")
    print(term.move_y(12) + term.bold("  [ GESTURES & POSES ]"))
    grid = [["1: Stand", "4: Wave", "7: Point", "0: Shrug"], ["2: Rest", "5: Bounce", "8: Pushup", "C: Display"], ["3: Bow", "6: Swim", "9: Cute", "V: Worm"], ["Z: Freaky", "K: Shake", "SPACE: Release", "X: Exit"]]
    for i, row in enumerate(grid):
        print(term.move_y(13+i) + "  " + "   ".join([f"{item:12}" for item in row]))
    print(term.move_y(18) + term.bold("  [ RECENT ACTIVITY ]"))
    print(term.move_y(term.height - 1) + term.center(term.dim + "Use Keyboard to Control | Zerobot Project 2026"))
    STATE["dirty"] = True

def draw_dynamic_ui(force=False):
    """Updates dynamic values only if dirty or forced."""
    if not force and not STATE["dirty"] and time.time() - STATE["last_ui_update"] < 0.2:
        return

    status_clr = term.green if STATE["status"] == "ACTIVE" else term.red
    output = ""
    output += term.move_xy(0, 3) + term.clear_eol + f" Status: {term.bold(status_clr(STATE['status']))}  |  Last: {term.bold_yellow(STATE['last_cmd'])}"
    
    if STATE["running_script"]:
        output += term.move_xy(30, 3) + term.blink_magenta("EXECUTING...")
    else:
        output += term.move_xy(30, 3) + term.clear_eol

    # Servo Angles
    output += term.move_xy(46, 6) + term.cyan(f"{STATE['angles'][servo.L1]:3}")
    output += term.move_xy(54, 6) + term.cyan(f"{STATE['angles'][servo.R1]:3}")
    output += term.move_xy(46, 7) + term.cyan(f"{STATE['angles'][servo.L2]:3}")
    output += term.move_xy(54, 7) + term.cyan(f"{STATE['angles'][servo.R2]:3}")
    output += term.move_xy(46, 9) + term.yellow(f"{STATE['angles'][servo.L3]:3}")
    output += term.move_xy(54, 9) + term.yellow(f"{STATE['angles'][servo.R3]:3}")
    output += term.move_xy(46, 10) + term.yellow(f"{STATE['angles'][servo.L4]:3}")
    output += term.move_xy(54, 10) + term.yellow(f"{STATE['angles'][servo.R4]:3}")
    
    for i, msg in enumerate(HISTORY[-4:]):
        output += term.move_xy(3, 19 + i) + term.clear_eol + f"{term.dim}> {msg}"
    
    print(output, end='', flush=True)
    STATE["dirty"] = False
    STATE["last_ui_update"] = time.time()

def handle_input(char):
    if not char: return True
    char = char.lower()
    
    if STATE["status"] == "RELEASED" and char not in [' ', 'x']:
        expr.happy()
        STATE["status"] = "ACTIVE"
        STATE["dirty"] = True

    if STATE["powersaving"]:
        set_low_power(False)

    if char == 'x': return False
    if char == 'p': 
        set_low_power(True)
        HISTORY.append("Manual Sleep (Power Key)")
        return True
    
    STATE["dirty"] = True
    
    # Reset tilt if it's not a tilt command
    if char not in ['q', 'e']:
        STATE["tilt_level"] = 0

    if char == 'w': STATE["last_cmd"]="WALK_FWD"; expr.eyes.look("up"); run_mvmt("sesame_walk", {"direction": 1}); HISTORY.append("Walk Forward")
    elif char == 's': STATE["last_cmd"]="WALK_BWD"; expr.eyes.look("down"); run_mvmt("sesame_walk", {"direction": -1}); HISTORY.append("Walk Backward")
    elif char == 'a': STATE["last_cmd"]="TURN_LEFT"; expr.eyes.look("left"); run_mvmt("sesame_turn", {"direction": 1}); HISTORY.append("Turn Left")
    elif char == 'd': STATE["last_cmd"]="TURN_RIGHT"; expr.eyes.look("right"); run_mvmt("sesame_turn", {"direction": -1}); HISTORY.append("Turn Right")
    elif char == 'q': 
        STATE["last_cmd"]="LOOK_UP"
        STATE["tilt_level"] = min(STATE["tilt_level"] + 15, 135)
        expr.eyes.look("up")
        run_mvmt("lookup", {"offset": STATE["tilt_level"]})
        HISTORY.append(f"Look Up (+{STATE['tilt_level']})")
    elif char == 'e': 
        STATE["last_cmd"]="LOOK_DOWN"
        STATE["tilt_level"] = max(STATE["tilt_level"] - 15, -135)
        expr.eyes.look("down")
        run_mvmt("lookdown", {"offset": abs(STATE["tilt_level"])})
        HISTORY.append(f"Look Down (-{abs(STATE['tilt_level'])})")
    elif char == '1': 
        STATE["last_cmd"]="STAND"; expr.happy()
        for ch, val in servo.HOME.items(): set_angle(ch, val)
        HISTORY.append("Stand")
    elif char == '2': 
        STATE["last_cmd"]="REST"; expr.sad()
        run_mvmt("rest")
        HISTORY.append("Resting")
    elif char == '3': STATE["last_cmd"]="BOW"; expr.happy(looking="down"); run_mvmt("bow"); HISTORY.append("Bowing")
    elif char == '4': STATE["last_cmd"]="WAVE"; expr.wink(); run_mvmt("wave"); HISTORY.append("Waving")
    elif char == '5': 
        STATE["last_cmd"]="BOUNCE"
        threading.Thread(target=expr.bounce, args=(4.0,), daemon=True).start()
        run_mvmt("bounce")
        HISTORY.append("Bouncing")
    elif char == '6': STATE["last_cmd"]="SWIM"; expr.happy(); run_mvmt("swim"); HISTORY.append("Swimming")
    elif char == '7': STATE["last_cmd"]="POINT"; expr.happy(); run_mvmt("point"); HISTORY.append("Pointing")
    elif char == '8': STATE["last_cmd"]="PUSHUP"; expr.happy(); run_mvmt("pushups"); HISTORY.append("Pushups")
    elif char == '9': STATE["last_cmd"]="CUTE"; expr.love(); run_mvmt("cute"); HISTORY.append("Cute Mode")
    elif char == '0': STATE["last_cmd"]="SHRUG"; expr.pondering(); run_mvmt("shrug"); HISTORY.append("Shrugging")
    elif char == 'c': STATE["last_cmd"]="CRAB"; expr.scan(); run_mvmt("crab_display"); HISTORY.append("Crab Display")
    elif char == 'v': STATE["last_cmd"]="WORM"; expr.glitch(); run_mvmt("worm"); HISTORY.append("Worming")
    elif char == 'k': STATE["last_cmd"]="SHAKE"; expr.matrix(); run_mvmt("shake"); HISTORY.append("Shaking")
    elif char == 'z': STATE["last_cmd"]="FREAKY"; expr.angry(); run_mvmt("freaky"); HISTORY.append("Freaky Mode")
    elif char == ' ': 
        STATE["status"]="RELEASED"; STATE["last_cmd"]="RELEASE"
        servo.release_all()
        HISTORY.append("Motors Released")
        expr.sleeping()
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--bt", action="store_true", help="Auto-enable Bluetooth Remote")
    args = parser.parse_args()

    # 1. Pre-initialization Prompt
    if not args.bt:
        print(term.clear + term.home)
        print(term.bold_cyan("Zerobot Control System 2026"))
        use_bt = input("\nEnable Bluetooth Remote functionality? (y/n): ").strip().lower() == 'y'
    else:
        use_bt = True
    
    # 2. Hardware Initialization
    expr.wakeup()
    run_mvmt("wakeup")
    
    if use_bt:
        print(term.yellow("\nSearching for Bluetooth Remote..."))
        STATE["remote_dev"] = find_remote()
        if STATE["remote_dev"]:
            HISTORY.append(f"Remote Linked: {STATE['remote_dev'].name}")
            print(term.green(f"Success! Linked to {STATE['remote_dev'].name}"))
            time.sleep(1)
        else:
            HISTORY.append("No BT Remote Found")
            print(term.red("No remote found. Continuing with keyboard only."))
            time.sleep(1.5)
    else:
        HISTORY.append("BT Remote Disabled")

    # 3. Main TUI Loop
    with term.cbreak(), term.hidden_cursor():
        draw_static_ui()
        while True:
            draw_dynamic_ui()
            key = term.inkey(timeout=0.01)
            
            if key:
                STATE["last_input_time"] = time.time()
                if not handle_input(str(key)): break
            
            if STATE["remote_dev"]:
                try:
                    for event in STATE["remote_dev"].read():
                        if event.type == ecodes.EV_KEY:
                            key_event = evdev.categorize(event)
                            if key_event.keystate == key_event.key_down:
                                STATE["last_input_time"] = time.time()
                                key_name = key_event.keycode
                                if isinstance(key_name, list): key_name = key_name[0]
                                
                                # Debug: log all remote keys to history
                                HISTORY.append(f"Remote: {key_name}")
                                
                                if key_name in BT_KEY_MAP:
                                    if not handle_input(BT_KEY_MAP[key_name]):
                                        return # Exit main()
                except (BlockingIOError, OSError): pass
                except (IOError, EOFError):
                    STATE["remote_dev"] = None
                    HISTORY.append("BT Remote Disconnected")
                    STATE["dirty"] = True
            
            if not key:
                idle_time = time.time() - STATE["last_input_time"]
                
                # Low Power Mode (5 mins / 300s)
                if idle_time > 300.0 and not STATE["powersaving"]:
                    set_low_power(True)
                
                # Auto-Rest (60s)
                if idle_time > 60.0 and STATE["last_cmd"] != "REST":
                    HISTORY.append("Auto-Rest (Idle)")
                    handle_input('2')
                
                # Auto-Stand (5s)
                elif idle_time > 5.0 and STATE["last_cmd"] not in ["STAND", "REST"]:
                    HISTORY.append("Auto-Stand (Idle)")
                    handle_input('1')

                if idle_time > 5.0 and STATE["status"] == "ACTIVE":
                    # Random Idle Movements (every 8-10 seconds while between 5s and 60s)
                    if idle_time < 60.0 and time.time() - STATE.get("last_idle_mvmt", 0) > random.uniform(8.0, 10.0):
                        run_mvmt("idle")
                        STATE["last_idle_mvmt"] = time.time()
                        HISTORY.append("Idle Movement")
                        STATE["dirty"] = True

                    # Random Eye Movements (every 2-4 seconds while idle)
                    if time.time() - STATE["last_eye_move"] > random.uniform(2.0, 4.0):
                        expr.eyes.look(random.choice(["left", "right", "center", "up", "down", "center"]))
                        STATE["last_eye_move"] = time.time()
                    
                    # Random Blinking
                    if time.time() - STATE["last_blink"] > STATE["blink_interval"]:
                        expr.blink()
                        STATE["last_blink"] = time.time()
                        STATE["blink_interval"] = random.uniform(3.0, 7.0)

    run_mvmt("sleep")
    if hasattr(expr.eyes.disp, 'set_backlight'):
        expr.eyes.disp.set_backlight(False)
    servo.release_all()
    print(term.clear + "Dashboard closed safely.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        servo.release_all()
        sys.exit(0)
