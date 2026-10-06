"""The agent: its loop, and the configuration that shapes it."""

from .config import MAX_PAUSE_RESTARTS, MAX_TOKENS, MAX_TURNS, MODEL, SYSTEM_PROMPT
from .loop import Agent, preview

__all__ = [
    "Agent",
    "preview",
    "MODEL",
    "SYSTEM_PROMPT",
    "MAX_TOKENS",
    "MAX_TURNS",
    "MAX_PAUSE_RESTARTS",
]
