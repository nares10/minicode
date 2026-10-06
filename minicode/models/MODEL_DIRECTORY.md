# Model Directory - Complete Implementation

## What Was Created

I've created a flexible model directory structure that allows minicode to work with multiple LLM providers.

## Directory Structure

```
minicode/
├── models/
│   ├── __init__.py          # Exports all model classes
│   ├── base.py             # Abstract base interface
│   ├── gemini.py           # Google Gemini client
│   ├── groq.py             # Groq client (free tier)
│   ├── ollama.py            # Ollama client (local, free)
│   ├── openai.py           # OpenAI-compatible client
│   ├── factory.py          # Model factory for easy creation
│   └── README.md           # Detailed documentation
├── .env                    # Updated with model options
└── setup_model.sh          # Setup helper script
```

## Key Features

### 1. **Unified Interface**
All models implement the same `BaseModel` interface:
- `create_chat()` - Create chat session
- `send_message_stream()` - Stream responses
- `format_function_response()` - Format tool responses
- `get_function_calls()` - Extract bash commands
- `get_text()` - Extract text from response

### 2. **Auto-Detection**
The agent automatically detects which model to use based on environment variables:
```python
from minicode.models import auto_detect_model
model = auto_detect_model()  # Auto-detects based on env vars
```

**Priority:**
1. `GROQ_API_KEY` → Groq (free, fast)
2. `OLLAMA_BASE_URL` → Ollama (local, free)
3. `GEMINI_API_KEY` → Gemini (paid)

### 3. **Easy Switching**
```python
from minicode.models import create_model

# Explicit model selection
model = create_model("groq", "llama-3.3-70b-versatile")
model = create_model("ollama", "llama3.1:8b")
model = create_model("gemini", "gemini-3.1-flash-lite")
```

### 4. **Text-Based Command Parsing**
For models without function calling (Groq, Ollama), we parse bash commands from text:
```python
# Detects:
```bash
ls -la
```
# or
$ ls -la
```

## Supported Providers

| Provider | Cost | Speed | Setup | Best For |
|----------|------|-------|-------|----------|
| **Groq** | Free ⭐ | Very Fast ⚡⚡⚡ | Easy | Development, testing |
| **Ollama** | Free ⭐ | Fast ⚡⚡ | Medium | Production, privacy |
| **Gemini** | Paid | Fast ⚡⚡ | Easy | Existing users |
| **OpenAI** | Paid | Fast ⚡⚡ | Easy | OpenAI ecosystem |

## Quick Start

### Option 1: Groq (Recommended - Free!)

```bash
# 1. Sign up (2 minutes, no credit card)
# Go to https://console.groq.com

# 2. Get API key
# https://console.groq.com/keys

# 3. Set environment variable
export GROQ_API_KEY="your-key"

# 4. Run minicode
python -m minicode.cli
```

### Option 2: Ollama (Local - Free!)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull a model (smaller is faster)
ollama pull llama3.1:8b  # 4.7GB (recommended)
# or
ollama pull llama3.3:70b  # 42GB (better quality)

# 3. Set environment variable
export OLLAMA_BASE_URL="http://localhost:11434"

# 4. Run minicode
python -m minicode.cli
```

### Option 3: Keep Using Gemini

```bash
# Already configured in .env
# Just run:
python -m minicode.cli
```

## Updated Files

### agent.py
- Removed direct Gemini client dependency
- Added model client factory
- Uses `auto_detect_model()` by default
- Supports explicit model selection

### .env
- Added configuration options for all providers
- Clear comments explaining each option
- Easy to switch between providers

### New Files
- `models/__init__.py` - Package exports
- `models/base.py` - Abstract interface
- `models/gemini.py` - Gemini implementation
- `models/groq.py` - Groq implementation
- `models/ollama.py` - Ollama implementation
- `models/openai.py` - OpenAI implementation
- `models/factory.py` - Model factory
- `models/README.md` - Detailed documentation
- `setup_model.sh` - Setup helper script

## Testing

Run the setup script to check your configuration:
```bash
cd minicode
./setup_model.sh
```

## Harbor Integration

When using Harbor for evaluation, you can now use any model:

```bash
# With Groq (free)
export GROQ_API_KEY="your-key"
harbor run \
  --dataset terminal-bench@2.0 \
  --agent gemini-cli \
  --model groq/llama-3.3-70b-versatile \
  --ve GROQ_API_KEY="$GROQ_API_KEY"

# With local Ollama
harbor run \
  --dataset terminal-bench@2.0 \
  --agent gemini-cli \
  --model ollama/llama3.1:8b \
  --env docker
```

## Benefits

1. **Cost Savings**: Use free Groq or local Ollama instead of paid APIs
2. **Flexibility**: Easy to switch between providers
3. **Privacy**: Ollama keeps data local
4. **Speed**: Groq is incredibly fast (280-800 tokens/sec)
5. **No Vendor Lock-in**: Switch providers with one line change

## Next Steps

1. **Choose a provider**: I recommend Groq (free, fast)
2. **Set up API key**: Follow the quick start above
3. **Test locally**: Run `python -m minicode.cli`
4. **Run Harbor evaluation**: Use cloud or local evaluation

## Troubleshooting

### Import Error
```bash
# Install missing dependencies
pip install groq  # for Groq
# or
pip install openai  # for OpenAI/DeepSeek
```

### Ollama Connection Refused
```bash
# Start Ollama server
ollama serve
```

### Groq Rate Limit
Wait until next day (UTC midnight) or upgrade to Developer tier.

## Migration Notes

The old code directly used Gemini. The new code:
- Is backward compatible (still works with Gemini)
- Auto-detects the best available model
- Makes it easy to add new providers
- Separates model logic from agent logic

All changes are non-breaking if you keep `GEMINI_API_KEY` set.
