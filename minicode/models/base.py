"""Base model interface for minicode."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ModelConfig:
    """Configuration for model clients."""
    model_name: str
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 64000
    timeout: int = 120


class BaseModel(ABC):
    """Abstract base class for model clients."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = None
        self._setup_client()
    
    @abstractmethod
    def _setup_client(self) -> None:
        """Initialize the model client."""
        pass
    
    @abstractmethod
    def create_chat(self, system_instruction: str = "") -> Any:
        """Create a chat session with system instruction."""
        pass
    
    @abstractmethod
    def send_message_stream(self, chat, message: str):
        """Send a message and stream the response."""
        pass
    
    @abstractmethod
    def format_function_response(self, name: str, response: dict) -> Any:
        """Format a function/tool response for the model."""
        pass
    
    @abstractmethod
    def get_function_calls(self, response) -> list:
        """Extract function calls from model response."""
        pass
    
    @abstractmethod
    def get_text(self, response) -> str:
        """Extract text from model response."""
        pass
