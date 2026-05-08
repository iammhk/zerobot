# speed_up_scripts.py - Adjusts movement speed by using centralized FRAME_DELAY
import os
import re

def speed_up_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace time.sleep(0.1), time.sleep(0.2), etc. with FRAME_DELAY based logic
    # We'll map the common ones:
    # 0.05 -> 0.5 * FRAME_DELAY
    # 0.1  -> 1.0 * FRAME_DELAY
    # 0.15 -> 1.5 * FRAME_DELAY
    # 0.2  -> 2.0 * FRAME_DELAY
    # 0.3  -> 3.0 * FRAME_DELAY
    # 0.4  -> 4.0 * FRAME_DELAY
    # 0.5  -> 5.0 * FRAME_DELAY
    # 0.6  -> 6.0 * FRAME_DELAY
    
    # First, find all time.sleep(NUMBER)
    def replacer(match):
        val = float(match.group(1))
        if val <= 1.0: # Only speed up short movement sleeps
            multiplier = val / 0.1
            if multiplier == 1.0:
                return f"time.sleep(servo.config.FRAME_DELAY)"
            else:
                return f"time.sleep(servo.config.FRAME_DELAY * {multiplier:.1f})"
        return match.group(0)

    content = re.sub(r"time\.sleep\(([\d\.]+)\)", replacer, content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Sped up {filepath}")

def main():
    for f in os.listdir("scripts"):
        if f.startswith("mvmt_") and f.endswith(".py"):
            speed_up_file(os.path.join("scripts", f))

if __name__ == "__main__":
    main()
