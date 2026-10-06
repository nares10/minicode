"""Ollama model client (local, free)."""

import requests
from typing import Any, Generator
import json

from .base import BaseModel, ModelConfig


class OllamaModel(BaseModel):
    """Ollama model client - runs locally, completely free."""
    
    def _setup_client(self) -> None:
        """Initialize Ollama client (uses REST API)."""
        self.base_url = self.config.base_url or "http://localhost:11434"
    
    def create_chat(self, system_instruction: str = "") -> Any:
        """Create a chat session with system instruction."""
        return {
            "messages": [{"role": "system", "content": system_instruction}],
            "model": self.config.model_name,
            "stream": True,
        }
    
    def send_message_stream(self, chat, message: str) -> Generator:
        """Send a message and stream the response."""
        chat["messages"].append({"role": "user", "content": message})
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=chat,
            stream=True,
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                yield json.loads(line)
    
    def format_function_response(self, name: str, response: dict) -> Any:
        """Format a bash response for Ollama."""
        output = response.get("result", response.get("error", ""))
        return {"role": "user", "content": f"Command output:\n{output}"}
    
    def get_function_calls(self, response) -> list:
        """Extract bash commands from Ollama response."""
        # Collect full response text
        full_text = ""
        for chunk in response:
            if chunk.get("message", {}).get("content"):
                full_text += chunk["message"]["content"]
        
        # Simple pattern matching for bash commands
        commands = []
        
        # Look for commands in code blocks
        import re
        for pattern in [r'```bash\s*\n(.*?)\n```', r'```sh\s*\n(.*?)\n```']:
            for match in re.finditer(pattern, full_text, re.DOTALL):
                commands.append({"name": "bash", "args": {"command": match.group(1).strip()}})
        
        return commands
    
    def get_text(self, response) -> str:
        """Extract text from Ollama response."""
        text_parts = []
        for chunk in response:
            if chunk.get("message", {}).get("content"):
                text_parts.append(chunk["message"]["content"])
        return "".join(text_parts)
