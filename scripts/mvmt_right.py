# crab_right.py - Turn the Crab-Bot right in place
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from zerobot import servo


# I2C Setup
# --- Channel Mapping ---
# --- HARD LIMITS ---


# Neutral Home Position





def turn_step(s_ch, k_ch, dir):
    """
    dir: -1 for CW (Right)
    """
    mid_s = servo.HOME[s_ch]
    mid_k = servo.HOME[k_ch]
    
    # 1. Lift
    lift_val = 40 if k_ch in [4, 7] else -40
    servo.set_angle(k_ch, mid_k + lift_val)
    time.sleep(servo.config.FRAME_DELAY * 1.2)
    
    # 2. Swing shoulder to the target turn position
    offset = 35 * dir
    servo.set_angle(s_ch, mid_s + offset)
    time.sleep(servo.config.FRAME_DELAY * 1.2)
    
    # 3. Lower
    servo.set_angle(k_ch, mid_k)
    time.sleep(servo.config.FRAME_DELAY * 1.2)



try:
    print("Moving to Home...")
    servo.move_to_home()
    time.sleep(1.5)

    print("Turning Right (Clockwise)...")
    for _ in range(10): # 10 cycles
        # One by one, move legs to their "turn" positions
        turn_step(servo.L1, servo.L3, -1) 
        turn_step(servo.R1, servo.R3, -1) 
        turn_step(servo.L2, servo.L4, -1) 
        turn_step(servo.R2, servo.R4, -1) 
        
        # Pull body around (Reset all shoulders to HOME while feet are down)
        print("Rotating body...")
        for ch in [servo.L1, servo.R1, servo.L2, servo.R2]:
            servo.set_angle(ch, servo.HOME[ch])
        time.sleep(servo.config.FRAME_DELAY * 4.0)

    print("Resting at Home.")
    servo.move_to_home()
    time.sleep(servo.config.FRAME_DELAY * 10.0)
    for ch in range(8): set_pwm(ch, 0, 0)

except KeyboardInterrupt:
    for ch in range(8): set_pwm(ch, 0, 0)
