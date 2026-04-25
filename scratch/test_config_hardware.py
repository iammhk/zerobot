# test_config_hardware.py
# This script tests that the connected_hardware field is correctly recognized by the Pydantic schema.

from zerobot.config.schema import Config, AgentDefaults
from pydantic import ValidationError

def test_config():
    try:
        config_dict = {
            "agents": {
                "defaults": {
                    "connected_hardware": ["pca9685", "test_device"]
                }
            }
        }
        config = Config.model_validate(config_dict)
        print(f"Success! Connected hardware: {config.agents.defaults.connected_hardware}")
        assert config.agents.defaults.connected_hardware == ["pca9685", "test_device"]
        
        # Test default value
        config_empty = Config.model_validate({})
        print(f"Default connected hardware: {config_empty.agents.defaults.connected_hardware}")
        assert config_empty.agents.defaults.connected_hardware == []
        
    except ValidationError as e:
        print(f"Validation Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_config()
