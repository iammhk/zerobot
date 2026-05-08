# config.py - Central configuration for Zerobot
# This file contains hardware mappings and safety limits.

# --- SERVO CHANNEL MAPPING ---
# Updated on 2026-05-08 based on recalibration
L1 = 0
L2 = 1
L3 = 5
L4 = 4
R1 = 3
R2 = 2
R3 = 7
R4 = 6

# Helper list for all servos
ALL_SERVOS = [L1, R1, L2, R2, L3, R3, L4, R4]

# Human-readable names
NAMES = {
    L1: "L1", R1: "R1", 
    L2: "L2", R2: "R2", 
    L3: "L3", R3: "R3", 
    L4: "L4", R4: "R4"
}

# --- HARD LIMITS (Safe Ranges) ---
LIMITS = {
    L1: (0, 90),
    R1: (90, 180),
    L2: (90, 180),
    R2: (0, 90),
    L3: (0, 180),
    R3: (0, 180),
    L4: (0, 180),
    R4: (0, 180)
}
