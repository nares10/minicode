"""Model factory for creating model clients."""

import os
from typing import Literal

from .base import BaseModel, ModelConfig

# Lazy imports to handle optional dependencies
def _get_gemini_model():
    from .gemini import GeminiModel
    return GeminiModel

def _get_groq_model():
    from .groq import GroqModel
    return GroqModel

def _get_ollama_model():
    from .ollama import OllamaModel
    return OllamaModel


ModelType = Literal["gemini", "groq", "ollama"]


def create_model(model_type: ModelType, model_name: str | None = None) -> BaseModel:
    """Create a model client based on type.
    
    Args:
        model_type: Type of model ("gemini", "groq", "ollama")
        model_name: Specific model name (uses default if None)
    
    Returns:
        Configured model client
    """
    if model_type == "gemini":
        ModelClass = _get_gemini_model()
        config = ModelConfig(
            model_name=model_name or os.getenv("MODEL", "gemini-3.1-flash-lite"),
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        return ModelClass(config)
    
    elif model_type == "groq":
        ModelClass = _get_groq_model()
        config = ModelConfig(
            model_name=model_name or os.getenv("MODEL", "llama-3.3-70b-versatile"),
            api_key=os.getenv("GROQ_API_KEY"),
        )
        return ModelClass(config)
    
    elif model_type == "ollama":
        ModelClass = _get_ollama_model()
        config = ModelConfig(
            model_name=model_name or os.getenv("MODEL", "llama3.3:70b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
        return ModelClass(config)
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def auto_detect_model() -> BaseModel:
    """Auto-detect which model to use based on environment variables.
    
    Priority:
    1. GROQ_API_KEY set -> Groq (free, fast)
    2. OLLAMA_BASE_URL set -> Ollama (local, free)
    3. GEMINI_API_KEY set -> Gemini (default)
    """
    if os.getenv("GROQ_API_KEY"):
        print("Using Groq model (free tier)")
        return create_model("groq")
    
    if os.getenv("OLLAMA_BASE_URL") or os.path.exists("/usr/local/bin/ollama"):
        print("Using Ollama model (local)")
        return create_model("ollama")
    
    if os.getenv("GEMINI_API_KEY"):
        print("Using Gemini model")
        return create_model("gemini")
    
    raise ValueError(
        "No model API key found. Set one of:\n"
        "- GROQ_API_KEY (recommended, free)\n"
        "- OLLAMA_BASE_URL (local, free)\n"
        "- GEMINI_API_KEY"
    )
