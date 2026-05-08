# servo.py - High-level servo control module for Zerobot
# This module provides a single point of control for all servos using the central config.

import time
from .utils.pca9685 import PCA9685, ServoHelper
from . import config

# Initialize the hardware
_pca = PCA9685(address=config.I2C_ADDR, bus_id=config.I2C_BUS)
_helper = ServoHelper(_pca, freq=config.PWM_FREQ, min_pulse=config.MIN_PULSE, max_pulse=config.MAX_PULSE)

def set_angle(channel, angle):
    """Set servo angle with safety limit clipping."""
    min_a, max_a = config.LIMITS.get(channel, (0, 180))
    safe_angle = max(min_a, min(max_a, angle))
    _helper.set_angle(channel, safe_angle)

def move_to_home():
    """Move all servos to their defined home positions."""
    for ch, angle in config.HOME.items():
        set_angle(ch, angle)

def release_all():
    """Stop sending PWM signals to all servos (save battery/heat)."""
    _helper.release_all()

def release(channel):
    """Stop sending PWM signal to a specific channel."""
    _helper.release(channel)

# Export config constants for easy access
L1, L2, L3, L4 = config.L1, config.L2, config.L3, config.L4
R1, R2, R3, R4 = config.R1, config.R2, config.R3, config.R4
ALL_SERVOS = config.ALL_SERVOS
HOME = config.HOME
