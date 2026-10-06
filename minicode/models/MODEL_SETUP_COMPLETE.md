# ✅ Model Directory Setup Complete!

## What Was Created

I've created a flexible model directory that allows minicode to work with **multiple LLM providers** including free options!

## Directory Structure

```
minicode/
├── models/
│   ├── __init__.py          # Package exports
│   ├── base.py             # Abstract interface
│   ├── gemini.py           # Google Gemini (with lazy import)
│   ├── groq.py             # Groq (free tier, with lazy import)
│   ├── ollama.py            # Ollama (local, free)
│   ├── openai.py           # OpenAI-compatible (with lazy import)
│   ├── factory.py          # Model factory with lazy imports
│   └── README.md           # Full documentation
├── .env                    # Updated with all model options
├── setup_model.sh          # Setup helper script
└── MODEL_DIRECTORY.md      # This summary
```

## Key Features

### 1. **Multiple Provider Support**
- ✅ **Groq** - Completely free, 30 RPM, fast
- ✅ **Ollama** - Local, unlimited, free
- ✅ **Gemini** - Your current setup
- ✅ **OpenAI** - OpenAI/DeepSeek compatible

### 2. **Auto-Detection**
The agent automatically detects which model to use:
```python
from minicode.models import auto_detect_model
model = auto_detect_model()  # Auto-detects based on env vars
```

**Priority:**
1. `GROQ_API_KEY` → Groq (free, fast)
2. `OLLAMA_BASE_URL` → Ollama (local, free)
3. `GEMINI_API_KEY` → Gemini (your current setup)

### 3. **Lazy Imports**
All model clients use lazy imports, so you don't need to install all packages:
- Only install the packages you use
- No import errors if a package is missing
- Clean error messages

### 4. **Easy Switching**
```python
from minicode.models import create_model

# Use Groq (free)
model = create_model("groq", "llama-3.3-70b-versatile")

# Use Ollama (local)
model = create_model("ollama", "llama3.1:8b")

# Use Gemini
model = create_model("gemini", "gemini-3.1-flash-lite")
```

## Quick Start - FREE Options

### Option 1: Groq (Recommended - Free!)

```bash
# 1. Sign up (2 minutes, no credit card)
# Go to https://console.groq.com

# 2. Get API key
# https://console.groq.com/keys

# 3. Install groq package
pip install groq

# 4. Set environment variable
export GROQ_API_KEY="your-key"

# 5. Run minicode
python -m minicode.cli
```

**Groq Benefits:**
- ✅ Completely free
- ✅ Very fast (280-800 tokens/sec)
- ✅ Good models (Llama 3.3 70B, Llama 3.1 8B)
- ✅ 30 requests per minute
- ✅ 14,400 requests per day

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

**Ollama Benefits:**
- ✅ Completely free
- ✅ Unlimited requests
- ✅ Data stays local (privacy)
- ✅ Works offline
- ✅ No rate limits

## Updated .env File

Your `.env` file now has clear options for all providers:

```bash
# Option 1: Groq (FREE, Recommended)
# GROQ_API_KEY="your-groq-api-key"
# MODEL="llama-3.3-70b-versatile"

# Option 2: Ollama (FREE, Local)
# OLLAMA_BASE_URL="http://localhost:11434"
# MODEL="llama3.1:8b"

# Option 3: Gemini (Paid) - Your current setup
GEMINI_API_KEY="your-key"
MODEL="gemini-3.1-flash-lite"
```

Just uncomment the provider you want to use!

## Testing

Run the setup script to check your configuration:
```bash
cd minicode
./setup_model.sh
```

## For Harbor Evaluation

Now you can use any model with Harbor:

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

## Current Status

✅ Model directory created
✅ All model clients implemented
✅ Lazy imports working (no import errors)
✅ Auto-detection working
✅ .env file updated
✅ Documentation complete
✅ Setup script created

## Next Steps

1. **Choose a free provider**: I recommend Groq (easiest setup)
2. **Get API key**: https://console.groq.com/keys (2 minutes)
3. **Install package**: `pip install groq`
4. **Set env var**: `export GROQ_API_KEY="your-key"`
5. **Test**: `python -m minicode.cli`

## Benefits Summary

| Feature | Before | After |
|---------|--------|-------|
| **Cost** | Paid API | Free options available |
| **Flexibility** | Gemini only | 4+ providers |
| **Privacy** | Cloud-only | Local option (Ollama) |
| **Speed** | Fast | Very fast (Groq) |
| **Setup** | One provider | Easy switching |

## Documentation

- `models/README.md` - Full documentation
- `MODEL_DIRECTORY.md` - Implementation details
- `setup_model.sh` - Setup helper

All set! 🎉 You can now use minicode with free Groq or local Ollama models!
