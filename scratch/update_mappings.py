# update_mappings.py - Script to batch update servo mappings in all files
# Used to apply the new 2026-05-08 calibration across the project.

import os
import re

MAPPINGS = {
    r"L1, R1, L2, R2 = 0, 1, 2, 3": "L1, L2, L3, L4 = 0, 1, 5, 4\nR1, R2, R3, R4 = 3, 2, 7, 6",
    r"L3, R3, L4, R4 = 4, 5, 6, 7": "", # Handled by the first line usually
    r"L1, R1 = 0, 1 # Shoulders \(Front\)": "L1, R1 = 0, 3 # Shoulders (Front)",
    r"L2, R2 = 2, 3 # Shoulders \(Hind\)": "L2, R2 = 1, 2 # Shoulders (Hind)",
    r"L3, R3 = 4, 5 # Knees \(Front\)": "L3, R3 = 5, 7 # Knees (Front)",
    r"L4, R4 = 6, 7 # Knees \(Hind\)": "L4, R4 = 4, 6 # Knees (Hind)",
}

def update_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return
    
    original = content
    
    # Robust regex for the 2-line block
    pattern2 = r"L1,\s*R1,\s*L2,\s*R2\s*=\s*0,\s*1,\s*2,\s*3\s*\n\s*L3,\s*R3,\s*L4,\s*R4\s*=\s*4,\s*5,\s*6,\s*7"
    replacement2 = "L1, L2, L3, L4 = 0, 1, 5, 4\nR1, R2, R3, R4 = 3, 2, 7, 6"
    content = re.sub(pattern2, replacement2, content)
    
    # Individual replacements for other formats
    for pattern, replacement in MAPPINGS.items():
        if pattern:
            content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

def main():
    roots = ["scripts", "zerobot"]
    for root in roots:
        if not os.path.exists(root): continue
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip hidden directories
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            for f in filenames:
                if f.endswith(".py") and f not in ["update_mappings.py", "recalibrate_servos.py"]:
                    update_file(os.path.join(dirpath, f))

if __name__ == "__main__":
    main()
