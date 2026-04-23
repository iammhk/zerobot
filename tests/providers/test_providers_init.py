"""Tests for lazy provider exports from zerobot.providers."""

from __future__ import annotations

import importlib
import sys


def test_importing_providers_package_is_lazy(monkeypatch) -> None:
    monkeypatch.delitem(sys.modules, "zerobot.providers", raising=False)
    monkeypatch.delitem(sys.modules, "zerobot.providers.anthropic_provider", raising=False)
    monkeypatch.delitem(sys.modules, "zerobot.providers.openai_compat_provider", raising=False)
    monkeypatch.delitem(sys.modules, "zerobot.providers.openai_codex_provider", raising=False)
    monkeypatch.delitem(sys.modules, "zerobot.providers.github_copilot_provider", raising=False)
    monkeypatch.delitem(sys.modules, "zerobot.providers.azure_openai_provider", raising=False)

    providers = importlib.import_module("zerobot.providers")

    assert "zerobot.providers.anthropic_provider" not in sys.modules
    assert "zerobot.providers.openai_compat_provider" not in sys.modules
    assert "zerobot.providers.openai_codex_provider" not in sys.modules
    assert "zerobot.providers.github_copilot_provider" not in sys.modules
    assert "zerobot.providers.azure_openai_provider" not in sys.modules
    assert providers.__all__ == [
        "LLMProvider",
        "LLMResponse",
        "AnthropicProvider",
        "OpenAICompatProvider",
        "OpenAICodexProvider",
        "GitHubCopilotProvider",
        "AzureOpenAIProvider",
    ]


def test_explicit_provider_import_still_works(monkeypatch) -> None:
    monkeypatch.delitem(sys.modules, "zerobot.providers", raising=False)
    monkeypatch.delitem(sys.modules, "zerobot.providers.anthropic_provider", raising=False)

    namespace: dict[str, object] = {}
    exec("from zerobot.providers import AnthropicProvider", namespace)

    assert namespace["AnthropicProvider"].__name__ == "AnthropicProvider"
    assert "zerobot.providers.anthropic_provider" in sys.modules

