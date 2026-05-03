# pca9685.py - PCA9685 PWM controller driver for zerobot
# This file is used in the actual project to control servos via I2C on Raspberry Pi.

import math
import time
from typing import Optional

try:
    from smbus2 import SMBus
except ImportError:
    SMBus = None


class PCA9685:
    """
    Low-level driver for the PCA9685 PWM controller.
    Used by the Waveshare Servo Driver HAT.
    """

    # Registers/Constants
    MODE1 = 0x00
    MODE2 = 0x01
    SUBADR1 = 0x02
    SUBADR2 = 0x03
    SUBADR3 = 0x04
    PRESCALE = 0xFE
    LED0_ON_L = 0x06
    LED0_ON_H = 0x07
    LED0_OFF_L = 0x08
    LED0_OFF_H = 0x09
    ALL_LED_ON_L = 0xFA
    ALL_LED_ON_H = 0xFB
    ALL_LED_OFF_L = 0xFC
    ALL_LED_OFF_H = 0xFD

    # Bits
    RESTART = 0x80
    SLEEP = 0x10
    ALLCALL = 0x01
    INVRT = 0x10
    OUTDRV = 0x04

    def __init__(self, address: int = 0x40, bus_id: int = 1):
        self.address = address
        self.bus_id = bus_id
        self._bus: Optional[SMBus] = None

        if SMBus:
            try:
                self._bus = SMBus(bus_id)
                self._setup()
            except Exception as e:
                # We don't raise here to allow the agent to handle the error gracefully
                # when the tool is actually called.
                print(f"Warning: Could not initialize SMBus: {e}")

    def _setup(self):
        """Initial configuration of the PCA9685."""
        if not self._bus:
            return
        
        self.set_all_pwm(0, 0)
        self._bus.write_byte_data(self.address, self.MODE2, self.OUTDRV)
        self._bus.write_byte_data(self.address, self.MODE1, self.ALLCALL)
        time.sleep(0.005)  # wait for oscillator

        mode1 = self._bus.read_byte_data(self.address, self.MODE1)
        mode1 = mode1 & ~self.SLEEP  # wake up
        self._bus.write_byte_data(self.address, self.MODE1, mode1)
        time.sleep(0.005)  # wait for oscillator

    def set_pwm_freq(self, freq_hz: float):
        """Sets the PWM frequency in Hz."""
        if not self._bus:
            return
            
        prescaleval = 25000000.0  # 25MHz
        prescaleval /= 4096.0  # 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)

        oldmode = self._bus.read_byte_data(self.address, self.MODE1)
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self._bus.write_byte_data(self.address, self.MODE1, newmode)  # go to sleep
        self._bus.write_byte_data(self.address, self.PRESCALE, int(prescale))
        self._bus.write_byte_data(self.address, self.MODE1, oldmode)
        time.sleep(0.005)
        self._bus.write_byte_data(self.address, self.MODE1, oldmode | 0x80)

    def set_pwm(self, channel: int, on: int, off: int):
        """Sets a single PWM channel."""
        if not self._bus:
            return
            
        self._bus.write_byte_data(self.address, self.LED0_ON_L + 4 * channel, on & 0xFF)
        self._bus.write_byte_data(self.address, self.LED0_ON_H + 4 * channel, on >> 8)
        self._bus.write_byte_data(self.address, self.LED0_OFF_L + 4 * channel, off & 0xFF)
        self._bus.write_byte_data(self.address, self.LED0_OFF_H + 4 * channel, off >> 8)

    def set_all_pwm(self, on: int, off: int):
        """Sets all PWM channels."""
        if not self._bus:
            return
            
        self._bus.write_byte_data(self.address, self.ALL_LED_ON_L, on & 0xFF)
        self._bus.write_byte_data(self.address, self.ALL_LED_ON_H, on >> 8)
        self._bus.write_byte_data(self.address, self.ALL_LED_OFF_L, off & 0xFF)
        self._bus.write_byte_data(self.address, self.ALL_LED_OFF_H, off >> 8)

    def close(self):
        """Close the I2C bus."""
        if self._bus:
            self._bus.close()


class ServoHelper:
    """
    Helper to convert servo parameters (angle, pulse width) to PCA9685 values.
    """
    def __init__(self, pca: PCA9685, freq: int = 50, min_pulse: int = 500, max_pulse: int = 2500):
        self.pca = pca
        self.freq = freq
        self.min_pulse = min_pulse  # us
        self.max_pulse = max_pulse  # us
        self.pca.set_pwm_freq(freq)

    def set_angle(self, channel: int, angle: float):
        """Set servo angle (0-180)."""
        angle = max(0, min(180, angle))
        pulse = self.min_pulse + (angle / 180.0) * (self.max_pulse - self.min_pulse)
        self.set_pulse(channel, int(pulse))

    def set_pulse(self, channel: int, pulse_us: int):
        """Set pulse width in microseconds."""
        # pulse_bits = (pulse_us / period_us) * 4096
        # period_us = 1,000,000 / freq
        pulse_bits = int(pulse_us * 4096 * self.freq / 1000000)
        self.pca.set_pwm(channel, 0, pulse_bits)

    def release(self, channel: int):
        """Stop sending pulses to the channel."""
        self.pca.set_pwm(channel, 0, 0)

    def release_all(self):
        """Stop sending pulses to all channels."""
        self.pca.set_all_pwm(0, 0)
