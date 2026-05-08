# refactor_scripts.py - Advanced script to migrate hardcoded servo logic to zerobot.servo
import os
import re

# Boilerplate blocks to remove
BLOCKS_TO_REMOVE = [
    r"BUS = smbus2\.SMBus\(1\)",
    r"ADDR = 0x40",
    r"def set_pwm\(channel, on, off\):.*?set_pwm\(channel, 0, off\)\n", # Match the functions
    r"def set_freq\(freq\):.*?time\.sleep\(0\.005\)\n",
    r"L1, L2, L3, L4 = 0, 1, 5, 4\nR1, R2, R3, R4 = 3, 2, 7, 6",
    r"L1, R1 = 0, 3 # Shoulders \(Front\)\nL2, R2 = 1, 2 # Shoulders \(Hind\)\nL3, R3 = 5, 7 # Knees \(Front\)\nL4, R4 = 4, 6 # Knees \(Hind\)",
]

def refactor_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # 1. Add Path handling and Import
    if "from zerobot import servo" not in content:
        import_block = "import sys, os\nsys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\nfrom zerobot import servo\n"
        # Insert after other imports
        content = re.sub(r"(import time)", r"\1\n" + import_block, content)

    # 2. Remove old constants and functions
    content = content.replace("import smbus2\n", "")
    content = re.sub(r"BUS = smbus2\.SMBus\(1\)\s*", "", content)
    content = re.sub(r"ADDR = 0x40\s*", "", content)
    
    # Remove set_pwm function
    content = re.sub(r"def set_pwm\(channel, on, off\):.*?\n\s+BUS\.write_byte_data\(ADDR, 0x09 \+ 4\*channel, off >> 8\)\n", "", content, flags=re.DOTALL)
    
    # Remove set_freq function
    content = re.sub(r"def set_freq\(freq\):.*?\n\s+BUS\.write_byte_data\(ADDR, 0x00, old_mode \| 0x80\)\n", "", content, flags=re.DOTALL)

    # Remove set_angle function (but keep calls)
    content = re.sub(r"def set_angle\(channel, angle\):.*?\n\s+set_pwm\(channel, 0, off\)\n", "", content, flags=re.DOTALL)
    
    # Remove I2C Initialization blocks
    content = re.sub(r"# Initialize\s+try:.*?except Exception as e:.*?exit\(1\)", "", content, flags=re.DOTALL)
    content = re.sub(r"try:\s+BUS\.write_byte_data.*?except: pass", "", content, flags=re.DOTALL)
    
    # Remove local LIMITS and HOME if they exist
    content = re.sub(r"LIMITS = \{.*?\}", "", content, flags=re.DOTALL)
    content = re.sub(r"HOME = \{.*?\}", "", content, flags=re.DOTALL)
    
    # Remove mapping lines
    content = re.sub(r"L1, L2, L3, L4 = 0, 1, 5, 4\s*", "", content)
    content = re.sub(r"R1, R2, R3, R4 = 3, 2, 7, 6\s*", "", content)
    content = re.sub(r"L1, R1 = 0, 3.*?\n", "", content)
    content = re.sub(r"L2, R2 = 1, 2.*?\n", "", content)
    content = re.sub(r"L3, R3 = 5, 7.*?\n", "", content)
    content = re.sub(r"L4, R4 = 4, 6.*?\n", "", content)
    
    # Replace local HOME/LIMITS references with servo.HOME/servo.config.LIMITS
    content = content.replace("HOME[", "servo.HOME[")
    content = content.replace("LIMITS[", "servo.config.LIMITS[")

    # 3. Replace calls
    # L1 -> servo.L1, etc. (using negative lookbehind to avoid double-prefixing)
    for label in ["L1", "L2", "L3", "L4", "R1", "R2", "R3", "R4"]:
        content = re.sub(r"(?<!servo\.)\b" + label + r"\b", f"servo.{label}", content)
    
    content = content.replace("set_angle(", "servo.set_angle(")
    content = content.replace("set_pwm(i, 0, 0)", "servo.release(i)")
    
    # Special case for "releasing all"
    content = re.sub(r"for i in range\(8\):\s+servo\.set_pwm\(i, 0, 0\)", "servo.release_all()", content)
    content = re.sub(r"for i in range\(16\):\s+servo\.set_pwm\(i, 0, 0\)", "servo.release_all()", content)
    content = re.sub(r"for i in range\(8\):\s+set_pwm\(i, 0, 0\)", "servo.release_all()", content)
    content = re.sub(r"for i in range\(16\):\s+set_pwm\(i, 0, 0\)", "servo.release_all()", content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Refactored {filepath}")

def main():
    for f in os.listdir("scripts"):
        if f.startswith("mvmt_") and f.endswith(".py"):
            refactor_file(os.path.join("scripts", f))
    
    # Also refactor sesame_remote.py and crab_test.py
    refactor_file("scripts/sesame_remote.py")
    refactor_file("scripts/crab_test.py")

if __name__ == "__main__":
    main()
