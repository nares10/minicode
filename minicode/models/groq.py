"""Groq model client (free tier).

Uses text-based parsing for bash commands (no function calling).
"""

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

from typing import Any, Generator
import re

from .base import BaseModel, ModelConfig


class GroqModel(BaseModel):
    """Groq model client - completely free tier."""
    
    def _setup_client(self) -> None:
        """Initialize Groq client."""
        if not GROQ_AVAILABLE:
            raise ImportError("groq package not installed. Install with: pip install groq")
        self.client = Groq(api_key=self.config.api_key)
    
    def create_chat(self, system_instruction: str = "") -> Any:
        """Create a chat session with system instruction."""
        return {
            "messages": [{"role": "system", "content": system_instruction}],
            "model": self.config.model_name,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
    
    def send_message_stream(self, chat, message: str) -> Generator:
        """Send a message and stream the response."""
        chat["messages"].append({"role": "user", "content": message})
        
        response = self.client.chat.completions.create(
            model=chat["model"],
            messages=chat["messages"],
            temperature=chat["temperature"],
            max_tokens=chat["max_tokens"],
            stream=True,
        )
        
        return response
    
    def format_function_response(self, name: str, response: dict) -> Any:
        """Format a bash response for Groq (as a user message)."""
        output = response.get("result", response.get("error", ""))
        return {"role": "user", "content": f"Command output:\n{output}"}
    
    def get_function_calls(self, response) -> list:
        """Extract bash commands from Groq response using regex."""
        # Collect full response text
        full_text = self.get_text(response)
        
        # Look for bash commands in code blocks or after markers
        commands = []
        
        # Pattern 1: ```bash code blocks
        bash_pattern = r'```bash\s*\n(.*?)\n```'
        for match in re.finditer(bash_pattern, full_text, re.DOTALL):
            commands.append({"name": "bash", "args": {"command": match.group(1).strip()}})
        
        # Pattern 2: ```sh code blocks
        sh_pattern = r'```sh\s*\n(.*?)\n```'
        for match in re.finditer(sh_pattern, full_text, re.DOTALL):
            commands.append({"name": "bash", "args": {"command": match.group(1).strip()}})
        
        # Pattern 3: Lines starting with $ (common in terminal output)
        dollar_pattern = r'^\$\s+(.+)$'
        for match in re.finditer(dollar_pattern, full_text, re.MULTILINE):
            commands.append({"name": "bash", "args": {"command": match.group(1).strip()}})
        
        return commands
    
    def get_text(self, response) -> str:
        """Extract text from Groq response."""
        text_parts = []
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                text_parts.append(chunk.choices[0].delta.content)
        return "".join(text_parts)
