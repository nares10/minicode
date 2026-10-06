#!/bin/bash
# Setup script for minicode model configuration

echo "=========================================="
echo "Minicode Model Setup"
echo "=========================================="
echo ""

# Check which API keys are set
if [ -n "$GROQ_API_KEY" ]; then
    echo "✓ GROQ_API_KEY is set (recommended - free, fast)"
fi

if [ -n "$OLLAMA_BASE_URL" ] || command -v ollama &> /dev/null; then
    echo "✓ Ollama is available (local, free)"
fi

if [ -n "$GEMINI_API_KEY" ]; then
    echo "✓ GEMINI_API_KEY is set"
fi

if [ -n "$OPENAI_API_KEY" ]; then
    echo "✓ OPENAI_API_KEY is set"
fi

echo ""
echo "=========================================="
echo "Quick Setup Options"
echo "=========================================="
echo ""
echo "1. Groq (FREE, Recommended)"
echo "   - Sign up: https://console.groq.com"
echo "   - Get API key: https://console.groq.com/keys"
echo "   - Run: export GROQ_API_KEY='your-key'"
echo ""
echo "2. Ollama (FREE, Local)"
echo "   - Install: curl -fsSL https://ollama.com/install.sh | sh"
echo "   - Pull model: ollama pull llama3.1:8b"
echo "   - Run: export OLLAMA_BASE_URL='http://localhost:11434'"
echo ""
echo "3. Gemini (Paid)"
echo "   - Get key: https://ai.google.dev"
echo "   - Run: export GEMINI_API_KEY='your-key'"
echo ""
echo "=========================================="
echo "Current Configuration"
echo "=========================================="
echo "MODEL=${MODEL:-auto-detect}"
echo ""

# Test the setup
echo "Testing model detection..."
python3 -c "
from minicode.models import auto_detect_model
try:
    model = auto_detect_model()
    print(f'✓ Model client created successfully')
    print(f'  Type: {type(model).__name__}')
except Exception as e:
    print(f'✗ Error: {e}')
    print('')
    print('Please set one of these environment variables:')
    print('  export GROQ_API_KEY=\"your-key\"')
    print('  export OLLAMA_BASE_URL=\"http://localhost:11434\"')
    print('  export GEMINI_API_KEY=\"your-key\"')
"
