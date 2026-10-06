"""Tool definitions for minicode (bash-only).

Following mini-swe-agent philosophy: only a bash tool, the model uses the
shell for everything.
"""

from .bash import MAX_OUTPUT_CHARS, bash
from .registry import CLIENT_TOOLS, Tool, tool_params, validate_input

__all__ = [
    "bash",
    "MAX_OUTPUT_CHARS",
    "Tool",
    "CLIENT_TOOLS",
    "tool_params",
    "validate_input",
]
