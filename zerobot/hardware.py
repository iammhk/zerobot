# config.py - Central configuration for Zerobot
# This file contains hardware mappings, safety limits, and default positions.

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

# --- HARD LIMITS (Safe Ranges) ---
# Format: (min_angle, max_angle)
LIMITS = {
    L1: (0, 90),   R1: (90, 180),
    L2: (90, 180), R2: (0, 90),
    L3: (0, 180),  R3: (0, 180),
    L4: (0, 180),  R4: (0, 180)
}

# --- HOME POSITIONS (Default Standing) ---
HOME = {
    L1: 45,  R1: 135,
    L2: 135, R2: 45,
    L3: 0,   R3: 180,
    L4: 180, R4: 0
}

# --- HARDWARE SETTINGS ---
I2C_ADDR = 0x40
I2C_BUS = 1
PWM_FREQ = 50
MIN_PULSE = 500  # us
MAX_PULSE = 2500 # us

# Helper lists
ALL_SERVOS = [L1, R1, L2, R2, L3, R3, L4, R4]
SHOULDERS = [L1, R1, L2, R2]
KNEES = [L3, R3, L4, R4]

NAMES = {
    L1: "L1", R1: "R1", 
    L2: "L2", R2: "R2", 
    L3: "L3", R3: "R3", 
    L4: "L4", R4: "R4"
}
