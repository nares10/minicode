"""OpenAI-compatible model client."""

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from typing import Any, Generator

from .base import BaseModel, ModelConfig


class OpenAIModel(BaseModel):
    """OpenAI-compatible model client (works with OpenAI, DeepSeek, etc.)."""
    
    def _setup_client(self) -> None:
        """Initialize OpenAI client."""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package not installed. Install with: pip install openai")
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )
    
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
        """Format a bash response for OpenAI."""
        output = response.get("result", response.get("error", ""))
        return {"role": "user", "content": f"Command output:\n{output}"}
    
    def get_function_calls(self, response) -> list:
        """Extract bash commands from OpenAI response."""
        # Similar to Groq - use text parsing
        import re
        full_text = self.get_text(response)
        
        commands = []
        for pattern in [r'```bash\s*\n(.*?)\n```', r'```sh\s*\n(.*?)\n```']:
            for match in re.finditer(pattern, full_text, re.DOTALL):
                commands.append({"name": "bash", "args": {"command": match.group(1).strip()}})
        
        return commands
    
    def get_text(self, response) -> str:
        """Extract text from OpenAI response."""
        text_parts = []
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                text_parts.append(chunk.choices[0].delta.content)
        return "".join(text_parts)
