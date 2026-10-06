"""The bash tool: minicode's only way to touch the world."""

from __future__ import annotations

import subprocess

MAX_OUTPUT_CHARS = 20_000


def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    cut = len(text) - MAX_OUTPUT_CHARS
    return text[:MAX_OUTPUT_CHARS] + f"\n... [truncated {cut} chars]"


def bash(command: str, timeout: int = 120) -> str:
    """Run a shell command and return output."""
    proc = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=int(timeout),
    )
    parts = []
    if proc.stdout:
        parts.append(proc.stdout.rstrip())
    if proc.stderr:
        parts.append("[stderr]\n" + proc.stderr.rstrip())
    if proc.returncode != 0:
        parts.append(f"[exit code {proc.returncode}]")
    return _truncate("\n".join(parts) or "<no output>")
