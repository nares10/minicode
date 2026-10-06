"""The agent loop: stream a turn, run the tools, repeat."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ..memory import Memory
from ..models import ModelType, auto_detect_model, create_model
from ..tools import CLIENT_TOOLS, tool_params
from .config import MAX_TURNS, SYSTEM_PROMPT


class Agent:
    def __init__(
        self,
        cwd: str,
        approve,
        model: str | None = None,
        model_type: ModelType | None = None,
        enable_memory: bool = True,
    ):
        self.cwd = cwd
        self.approve = approve  # callable(tool_name, input_dict) -> bool
        self.chat = None
        self.tools = tool_params()
        self.enable_memory = enable_memory
        
        # Initialize memory system
        if self.enable_memory:
            self.memory = Memory(Path(cwd))
        else:
            self.memory = None
        
        # Create model client
        if model_type:
            self.model_client = create_model(model_type, model)
        else:
            self.model_client = auto_detect_model()
    
    def get_system_prompt(self) -> str:
        """Get system prompt with memory if enabled."""
        if self.memory:
            memory_text = self.memory.get_memory_text()
            if memory_text:
                return SYSTEM_PROMPT + f"\n\n{memory_text}\n\nThe working directory is {self.cwd}."
        return SYSTEM_PROMPT + f"\nThe working directory is {self.cwd}."
    
    def cleanup(self):
        """Save memory and cleanup resources."""
        if self.memory:
            self.memory.save()

    # -- tool execution ----------------------------------------------------

    def _run_tool(self, function_call: dict) -> dict:
        """Execute a bash command from the function call."""
        name = function_call.get("name")
        args = function_call.get("args", {})

        if name != "bash":
            return {"error": f"Unknown tool: {name}"}

        command = args.get("command", "")
        timeout = args.get("timeout", 120)

        if not command:
            return {"error": "No command provided"}

        if not self.approve("bash", {"command": command}):
            return {"error": "The user declined to run this command."}

        try:
            result = CLIENT_TOOLS["bash"].fn(command, timeout)
            return {"result": result}
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {e}"}

    # -- the loop ----------------------------------------------------------

    def run(self, user_text: str, on_text, on_thinking, on_tool) -> None:
        # Initialize chat with system prompt
        if self.chat is None:
            self.chat = self.model_client.create_chat(
                system_instruction=self.get_system_prompt()
            )
        
        # Record task to memory
        if self.memory:
            self.memory.record_task(user_text, "in_progress")
        
        restarts = 0
        turns = 0

        try:
            while True:
                if MAX_TURNS and turns >= MAX_TURNS:
                    on_text(f"\n[stopped after {MAX_TURNS} turns]\n")
                    if self.memory:
                        self.memory.record_task(user_text, "stopped at turn limit")
                    return
                turns += 1
                
                # Stream the response
                response_stream = self.model_client.send_message_stream(self.chat, user_text)
                
                # Stream text output
                text = self.model_client.get_text(response_stream)
                on_text(text)
                
                # Get function calls (bash commands)
                function_calls = self.model_client.get_function_calls(response_stream)
                
                if not function_calls:
                    if self.memory:
                        self.memory.record_task(user_text, "completed")
                    return

                # Execute tools and send responses back
                for fc in function_calls:
                    args = fc.get("args", {})
                    command = args.get("command", "")
                    on_tool(fc["name"], args)
                    result = self._run_tool({"name": fc["name"], "args": args})
                    
                    # Record to memory
                    if self.memory:
                        self.memory.record_command(command, str(result))
                        
                        # Detect file operations
                        if "cat " in command or "head " in command or "tail " in command:
                            # Extract file path
                            parts = command.split()
                            if len(parts) > 1:
                                self.memory.record_file_access(parts[1])
                
                # Send the response back to the model
                response_msg = self.model_client.format_function_response(fc["name"], result)
                if isinstance(self.chat, dict):
                    self.chat["messages"].append(response_msg)
                else:
                    # For stateful chat objects
                    self.chat.send_message(response_msg)
        finally:
            # Save memory on completion
            if self.memory:
                self.memory.save()


def preview(tool_name: str, data: dict) -> str:
    """One line describing a pending tool call, for the approval prompt."""
    return data.get("command", "")


