"""Model clients for minicode.

Supports multiple LLM providers: Gemini, Groq, Ollama, OpenAI, etc.
"""

from .base import BaseModel, ModelConfig
from .factory import create_model, auto_detect_model, ModelType

__all__ = [
    "BaseModel",
    "ModelConfig",
    "create_model",
    "auto_detect_model",
    "ModelType",
]

# Lazy imports for model classes (only import when used)
def get_model_class(model_type: str):
    """Get model class by type (lazy import)."""
    if model_type == "gemini":
        from .gemini import GeminiModel
        return GeminiModel
    elif model_type == "groq":
        from .groq import GroqModel
        return GroqModel
    elif model_type == "ollama":
        from .ollama import OllamaModel
        return OllamaModel
    elif model_type == "openai":
        from .openai import OpenAIModel
        return OpenAIModel
    else:
        raise ValueError(f"Unknown model type: {model_type}")
