# fix_home_error.py - Fixes undefined 'HOME' references in movement scripts
import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace the loop with servo.move_to_home()
    pattern = r"for ch, val in HOME\.items\(\):\s+servo\.set_angle\(ch, val\)"
    content = re.sub(pattern, "servo.move_to_home()", content)
    
    # Or just HOME.items() -> servo.HOME.items()
    content = content.replace("HOME.items()", "servo.HOME.items()")

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")

def main():
    for f in os.listdir("scripts"):
        if f.startswith("mvmt_") and f.endswith(".py"):
            fix_file(os.path.join("scripts", f))

if __name__ == "__main__":
    main()
