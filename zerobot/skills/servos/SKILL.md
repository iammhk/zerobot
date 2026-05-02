---
name: servos
description: Control servos connected to the Waveshare Servo Driver HAT.
metadata: {"Zerobot":{"emoji":"🤖","always":true}}
---

# Servo Control

This skill allows you to control up to 16 servos using the Waveshare Servo Driver HAT (PCA9685) on a Raspberry Pi.

## Prerequisites

1. **Enable I2C**:
   ```bash
   sudo raspi-config nonint do_i2c 0
   ```
2. **Install dependencies**:
   ```bash
   uv pip install smbus2
   # OR if you don't have uv:
   python3 -m pip install smbus2
   ```
3. **Enable Tool in Zerobot**:
   Add `"pca9685"` to the `connected_hardware` list in your `~/.zerobot/config.json`:
   ```json
   {
     "agents": {
       "defaults": {
         "connectedHardware": ["pca9685"]
       }
     }
   }
   ```
   *Restart Zerobot after changing the config.*

## Usage

You can control servos using the `servos` tool.

### Actions

- **move**: Move a servo to a specific angle (0-180).
- **center**: Move a servo to 90 degrees.
- **release**: Stop sending PWM signals to a channel (saves power, allows manual movement).
- **set_pwm**: Set a raw pulse width in microseconds (usually 500-2500).

### Example Commands

- "Move servo on channel 0 to 45 degrees"
- "Center the servo on channel 5"
- "Release channel 2"
- "Set channel 0 pulse to 1500us"

## CLI Utility

You can also use the Zerobot CLI to control servos directly:

```bash
# Move channel 0 to 90 degrees
Zerobot servo move 0 90

# Release channel 0
Zerobot servo release 0

# Center all servos (0-15)
Zerobot servo center --all
```

## Hardware Notes

- **Power**: If using many servos, connect an external 6V-12V power supply to the VIN terminal on the HAT.
- **Channels**: 0-15 are available on the pin headers.
- **Wiring**: Black = GND, Red = 5V, Yellow = PWM.
