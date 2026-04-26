# Test script for Tiered LLM routing
from zerobot.config.schema import TiersConfig, Config
from zerobot.agent.router import LLMRouter

def test_routing():
    config = TiersConfig(
        enable=True,
        chat_model="chat-2b",
        task_model="task-7b",
        complex_model="complex-cloud"
    )
    router = LLMRouter(config)

    # Test Chat
    assert router.route("Hello there!") == "chat-2b"
    assert router.route("How are you?") == "chat-2b"

    # Test Task
    assert router.route("list my files") == "task-7b"
    assert router.route("run a shell command") == "task-7b"
    assert router.route("open the door") == "task-7b"

    # Test Complex
    assert router.route("debug the memory leak in loop.py") == "complex-cloud"
    assert router.route("implement a new feature for the agent") == "complex-cloud"
    assert router.route("write a python script to analyze the logs") == "complex-cloud"
    
    # Test Length
    long_prompt = "a" * 801
    assert router.route(long_prompt) == "complex-cloud"

    print("✅ Tiered routing tests passed!")

if __name__ == "__main__":
    test_routing()
