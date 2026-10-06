"""The tool registry: schemas, lookup by name, and input validation."""

from __future__ import annotations

from dataclasses import dataclass

from google.genai import types

from .bash import bash


@dataclass
class Tool:
    name: str
    description: str
    schema: dict
    required: tuple[str, ...]
    fn: callable
    needs_approval: bool

    def to_param(self) -> types.FunctionDeclaration:
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters_json_schema=self.schema,
        )


CLIENT_TOOLS: dict[str, Tool] = {
    t.name: t
    for t in [
        Tool(
            name="bash",
            description=(
                "Run a shell command. Use this for ALL file operations, testing, git, etc. "
                "Examples: cat file.py, echo 'content' > file.py, sed -i 's/old/new/g' file.py, "
                "ls, grep, find, git status, python test.py. Commands are non-interactive."
            ),
            schema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to run."},
                    "timeout": {"type": "integer", "description": "Timeout in seconds (default 120)."},
                },
                "required": ["command"],
            },
            required=("command",),
            fn=bash,
            needs_approval=True,
        ),
    ]
}


def tool_params() -> types.Tool:
    function_declarations = [t.to_param() for t in CLIENT_TOOLS.values()]
    return types.Tool(function_declarations=function_declarations)


def validate_input(tool: Tool, data: object) -> str | None:
    """Return an error string if the tool input is unusable."""
    if not isinstance(data, dict):
        return "tool input was not a JSON object"
    missing = [k for k in tool.required if k not in data]
    if missing:
        return f"missing required field(s): {', '.join(missing)}"
    for key in tool.required:
        prop = tool.schema["properties"][key]
        if prop["type"] == "string" and not isinstance(data[key], str):
            return f"field '{key}' must be a string"
    return None
