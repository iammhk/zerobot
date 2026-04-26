# This file is part of the Zerobot multi-tiered LLM system.
# It classifies user intent to select the optimal model tier.

import re
from typing import Optional
from loguru import logger
from zerobot.config.schema import TiersConfig

class LLMRouter:
    """Routes prompts to different LLM tiers based on complexity."""

    # Keywords that suggest a complex reasoning or coding task (Tier 3)
    COMPLEX_KEYWORDS = [
        r"\bfix\b", r"\bdebug\b", r"\bimplement\b", r"\bwrite code\b", 
        r"\brefactor\b", r"\banalyze\b", r"\bcomplex\b", r"\barchitecture\b",
        r"\bsolve\b", r"\bcoding\b", r"\bscript\b"
    ]

    # Keywords that suggest a tool-based task (Tier 2)
    TASK_KEYWORDS = [
        r"\blist\b", r"\bread\b", r"\brun\b", r"\bsearch\b", r"\bfind\b", 
        r"\bshow\b", r"\bopen\b", r"\bservo\b", r"\bbluetooth\b", r"\baudio\b",
        r"\bexec\b", r"\bshell\b", r"\bfile\b"
    ]

    # Keywords that suggest simple movement or reactive control (Fast Path)
    REACTIVE_KEYWORDS = [
        r"\bmove\b", r"\bforward\b", r"\bbackward\b", r"\bturn\b", 
        r"\bleft\b", r"\bright\b", r"\bstop\b", r"\bhalt\b", r"\bcenter\b"
    ]

    def __init__(self, config: TiersConfig):
        self.config = config
        self._complex_pattern = re.compile("|".join(self.COMPLEX_KEYWORDS), re.IGNORECASE)
        self._task_pattern = re.compile("|".join(self.TASK_KEYWORDS), re.IGNORECASE)
        self._reactive_pattern = re.compile("|".join(self.REACTIVE_KEYWORDS), re.IGNORECASE)

    def route(self, prompt: str) -> str:
        """Select the model for the given prompt."""
        if not self.config.enable:
            return "" # Use default model

        # Rule 1: Length heuristic (very long prompts are usually complex)
        if len(prompt) > 800:
            logger.debug("Routing to Complex Tier due to prompt length.")
            return self.config.complex_model

        # Rule 2: Complex keyword matching
        if self._complex_pattern.search(prompt):
            logger.debug("Routing to Complex Tier based on keywords.")
            return self.config.complex_model

        # Rule 3: Task keyword matching
        if self._task_pattern.search(prompt):
            logger.debug("Routing to Task Tier based on keywords.")
            return self.config.task_model

        # Rule 4: Reactive keyword matching (Default to Chat Tier)
        if self._reactive_pattern.search(prompt):
            logger.debug("Routing to Chat Tier based on reactive keywords.")
            return self.config.chat_model

        # Rule 5: Default to Chat Tier
        logger.debug("Routing to Chat Tier.")
        return self.config.chat_model
