"""Google Gemini model client."""

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    types = None

from typing import Any

from .base import BaseModel, ModelConfig


class GeminiModel(BaseModel):
    """Google Gemini model client."""
    
    def _setup_client(self) -> None:
        """Initialize Gemini client."""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-genai package not installed. Install with: pip install google-genai")
        self.client = genai.Client(api_key=self.config.api_key)
    
    def create_chat(self, system_instruction: str = "") -> Any:
        """Create a chat session with system instruction."""
        return self.client.chats.create(
            model=self.config.model_name,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
            )
        )
    
    def send_message_stream(self, chat, message: str):
        """Send a message and stream the response."""
        return chat.send_message_stream(message)
    
    def format_function_response(self, name: str, response: dict) -> Any:
        """Format a function response for Gemini."""
        return types.Part.from_function_response(
            name=name,
            response=response
        )
    
    def get_function_calls(self, response) -> list:
        """Extract function calls from Gemini response."""
        function_calls = []
        for chunk in response:
            if chunk.candidates:
                for candidate in chunk.candidates:
                    for part in candidate.content.parts:
                        if part.function_call:
                            function_calls.append(part.function_call)
        return function_calls
    
    def get_text(self, response) -> str:
        """Extract text from Gemini response."""
        text_parts = []
        for chunk in response:
            if chunk.candidates:
                for candidate in chunk.candidates:
                    for part in candidate.content.parts:
                        if part.text:
                            text_parts.append(part.text)
        return "".join(text_parts)
