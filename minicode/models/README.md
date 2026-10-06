# Model Clients for Minicode

This directory contains model client implementations for different LLM providers, allowing you to easily switch between them.

## Supported Providers

| Provider | Cost | Speed | Setup |
|----------|------|-------|-------|
| **Groq** | Free ⭐ | Very Fast ⚡⚡⚡ | Easy |
| **Ollama** | Free ⭐ | Fast ⚡⚡ | Medium |
| **Gemini** | Paid | Fast ⚡⚡ | Easy |
| **OpenAI** | Paid | Fast ⚡⚡ | Easy |

## Quick Start

### Option 1: Auto-Detect (Recommended)

The agent will automatically detect which model to use based on environment variables:

```bash
# Set your preferred model's API key
export GROQ_API_KEY="your-key"  # Priority 1: Groq (free, fast)
# or
export OLLAMA_BASE_URL="http://localhost:11434"  # Priority 2: Ollama (local, free)
# or
export GEMINI_API_KEY="your-key"  # Priority 3: Gemini

# Run minicode
python -m minicode.cli
```

### Option 2: Explicit Model Selection

```python
from minicode.models import create_model

# Use Groq (free)
model = create_model("groq", "llama-3.3-70b-versatile")

# Use Ollama (local)
model = create_model("ollama", "llama3.3:70b")

# Use Gemini
model = create_model("gemini", "gemini-3.1-flash-lite")
```

## Provider Setup

### Groq (Recommended - Free!)

1. Sign up at https://console.groq.com (free, no credit card)
2. Get API key from https://console.groq.com/keys
3. Set environment variable:
   ```bash
   export GROQ_API_KEY="your-api-key"
   export MODEL="llama-3.3-70b-versatile"
   ```

**Available Models:**
- `llama-3.3-70b-versatile` - Best quality
- `llama-3.1-8b-instant` - Fastest, cheapest
- `qwen-32b` - Efficient reasoning

**Rate Limits (Free Tier):**
- 30 requests per minute
- 14,400 requests per day
- 1M tokens per minute

### Ollama (Local - Free!)

1. Install Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Pull a model:
   ```bash
   ollama pull llama3.3:70b  # 42GB (slow download)
   # or smaller model
   ollama pull llama3.1:8b   # 4.7GB (faster)
   ```

3. Set environment variable:
   ```bash
   export OLLAMA_BASE_URL="http://localhost:11434"
   export MODEL="llama3.3:70b"
   ```

**Available Models:**
- `llama3.3:70b` - Best quality (42GB)
- `llama3.1:8b` - Fast, small (4.7GB)
- `qwen2.5:7b` - Efficient (4.7GB)

### Gemini (Paid)

1. Get API key from https://ai.google.dev
2. Set environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   export MODEL="gemini-3.1-flash-lite"
   ```

**Available Models:**
- `gemini-3.1-flash-lite` - Cost-efficient, high-volume
- `gemini-3.6-flash` - Previous generation
- `gemini-3.5-flash` - Legacy

### OpenAI / DeepSeek (Paid/Free Tier)

1. Get API key from provider
2. Set environment variable:
   ```bash
   export OPENAI_API_KEY="your-key"  # or DEEPSEEK_API_KEY
   export MODEL="gpt-4o-mini"  # or deepseek-chat
   ```

## Architecture

### Base Interface

All models implement the `BaseModel` interface:

```python
class BaseModel(ABC):
    def create_chat(system_instruction: str) -> Any
    def send_message_stream(chat, message: str) -> Generator
    def format_function_response(name: str, response: dict) -> Any
    def get_function_calls(response) -> list
    def get_text(response) -> str
```

### Model Types

- **Gemini**: Uses Google GenAI SDK with function calling
- **Groq**: Uses OpenAI-compatible API with text-based command parsing
- **Ollama**: Uses REST API with text-based command parsing
- **OpenAI**: Uses OpenAI SDK with text-based command parsing

### Text-Based Command Parsing

For models without function calling (Groq, Ollama), we parse bash commands from the response using regex patterns:

```python
# Detects commands in code blocks
```bash
ls -la
```

# Or with $ prefix
$ ls -la
```

## Adding a New Provider

1. Create a new file in `models/` (e.g., `myprovider.py`)
2. Implement the `BaseModel` interface
3. Add to `models/__init__.py`
4. Add to `models/factory.py`

Example:

```python
# models/myprovider.py
from .base import BaseModel, ModelConfig

class MyProviderModel(BaseModel):
    def _setup_client(self) -> None:
        self.client = MyProviderClient(api_key=self.config.api_key)
    
    def create_chat(self, system_instruction: str) -> Any:
        # Implementation
        pass
    
    # ... implement other methods
```

## Troubleshooting

### "No model API key found"

Set one of these environment variables:
```bash
export GROQ_API_KEY="your-key"  # or
export OLLAMA_BASE_URL="http://localhost:11434"  # or
export GEMINI_API_KEY="your-key"
```

### Groq rate limit exceeded

Wait until the next day (UTC midnight) or upgrade to Developer tier.

### Ollama connection refused

Make sure Ollama is running:
```bash
ollama serve
```

### Model download too slow (Ollama)

Use a smaller model:
```bash
ollama pull llama3.1:8b  # instead of 70b
```

## Performance Comparison

| Provider | Latency | Throughput | Cost per 1M tokens |
|----------|---------|------------|-------------------|
| Groq (free) | ~50ms | 280-800 tok/s | $0 |
| Ollama (local) | ~100ms | 50-100 tok/s | $0 |
| Gemini 3.1-lite | ~200ms | ~50 tok/s | $0.25 |
| GPT-4o-mini | ~150ms | ~100 tok/s | $0.15 |

## Best Practices

1. **Development**: Use Groq (free, fast)
2. **Production**: Use Ollama (local, unlimited) or paid provider
3. **Large-scale**: Use cloud evaluation with Harbor + Groq
4. **Privacy-sensitive**: Use Ollama (data stays local)

## License

Each model client follows the license of its respective SDK.
