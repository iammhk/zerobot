# test_servo_mock.py - Mock test for servo logic
# This file is used to verify the PCA9685 driver and ServoHelper logic without hardware.

import sys
from unittest.mock import MagicMock

# Mock smbus2 before importing our driver
mock_smbus_lib = MagicMock()
sys.modules['smbus2'] = mock_smbus_lib

# Create a mock bus instance that will be returned by SMBus()
mock_bus_instance = MagicMock()
mock_smbus_lib.SMBus.return_value = mock_bus_instance

from zerobot.utils.pca9685 import PCA9685, ServoHelper

def test_servo_logic():
    print("Running servo logic test...")
    
    # Initialize driver with mock
    pca = PCA9685(address=0x40, bus_id=1)
    # The setup calls should have happened
    # mode1 = self._bus.read_byte_data(self.address, self.MODE1)
    
    helper = ServoHelper(pca, freq=50)
    
    # Test angle to pulse conversion
    # 90 degrees should be roughly 1500us
    # 50Hz frequency -> 20ms period
    # 1500us / 20000us * 4096 = 307.2
    
    # Mock set_pwm to capture calls
    pca.set_pwm = MagicMock()
    
    print("Testing 90 degrees (center)...")
    helper.set_angle(0, 90)
    # Check if set_pwm was called with expected values
    # pulse_bits = int(1500 * 4096 * 50 / 1000000) = 307
    pca.set_pwm.assert_called_with(0, 0, 307)
    print("OK 90 degrees produced 307 bits")
    
    print("Testing 0 degrees (min)...")
    helper.set_angle(0, 0)
    # pulse_bits = int(500 * 4096 * 50 / 1000000) = 102
    pca.set_pwm.assert_called_with(0, 0, 102)
    print("OK 0 degrees produced 102 bits")
    
    print("Testing 180 degrees (max)...")
    helper.set_angle(0, 180)
    # pulse_bits = int(2500 * 4096 * 50 / 1000000) = 512
    pca.set_pwm.assert_called_with(0, 0, 512)
    print("OK 180 degrees produced 512 bits")
    
    print("Testing release...")
    helper.release(0)
    pca.set_pwm.assert_called_with(0, 0, 0)
    print("OK Release produced 0 bits")
    
    print("\nAll logic tests passed!")

if __name__ == "__main__":
    try:
        test_servo_logic()
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
