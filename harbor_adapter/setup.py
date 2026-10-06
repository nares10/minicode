#!/usr/bin/env python3
"""
Setup script for integrating minicode with Harbor.
This script helps configure the adapter for use with Harbor.
"""

import os
import sys
from pathlib import Path


def check_environment():
    """Check if required environment variables are set."""
    print("Checking environment variables...")
    
    required = ["GEMINI_API_KEY"]
    optional = ["MODEL", "MINICODE_PATH"]
    
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
            print(f"  ❌ {var} is not set")
        else:
            print(f"  ✓ {var} is set")
    
    for var in optional:
        if os.getenv(var):
            print(f"  ✓ {var} is set ({os.getenv(var)})")
        else:
            print(f"  ⚠ {var} is not set (will use default)")
    
    if missing:
        print(f"\n❌ Missing required environment variables: {', '.join(missing)}")
        print("\nSet them with:")
        for var in missing:
            print(f"  export {var}='your-value'")
        return False
    
    return True


def setup_harbor_integration():
    """Instructions for Harbor integration."""
    print("\n" + "="*60)
    print("HARBOR INTEGRATION OPTIONS")
    print("="*60)
    
    print("\nOption 1: Local Harbor (modify Harbor source)")
    print("-" * 60)
    print("1. Copy minicode_agent.py to Harbor's agents directory:")
    print("   cp minicode_agent.py /path/to/harbor/src/harbor/agents/installed/")
    print("\n2. Add to AgentName enum in src/harbor/models/agent/name.py:")
    print("   MINICODE = 'minicode'")
    print("\n3. Add to factory in src/harbor/agents/factory.py:")
    print("   from harbor.agents.installed.minicode_agent import MinicodeAgent")
    print("   AgentName.MINICODE: MinicodeAgent")
    
    print("\n\nOption 2: External Agent (without modifying Harbor)")
    print("-" * 60)
    print("Use the agent directly in your own evaluation scripts.")
    print("See README.md for examples.")
    
    print("\n\nOption 3: Hosted Harbor (ACP)")
    print("-" * 60)
    print("1. Push this adapter to GitHub")
    print("2. Connect repository in Harbor profile settings")
    print("3. Use harbor-agent.json manifest")
    print("4. Submit jobs through Harbor web interface")


def print_usage_example():
    """Print example usage command."""
    print("\n" + "="*60)
    print("EXAMPLE USAGE")
    print("="*60)
    
    gemini_key = os.getenv("GEMINI_API_KEY", "your-api-key")
    model = os.getenv("MODEL", "gemini-3.1-flash-lite")
    minicode_path = os.getenv("MINICODE_PATH", "/path/to/minicode")
    
    print(f"\nharbor run \\")
    print(f"  --dataset terminal-bench@2.0 \\")
    print(f"  --agent minicode \\")
    print(f"  --model google/{model} \\")
    print(f"  --n-concurrent 2 \\")
    print(f"  --ve GEMINI_API_KEY=\"{gemini_key}\" \\")
    print(f"  --ae MINICODE_PATH=\"{minicode_path}\"")


def main():
    """Main setup function."""
    print("="*60)
    print("MINICODE HARBOR ADAPTER SETUP")
    print("="*60)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Print integration options
    setup_harbor_integration()
    
    # Print usage example
    print_usage_example()
    
    print("\n" + "="*60)
    print("Setup complete! See README.md for detailed documentation.")
    print("="*60)


if __name__ == "__main__":
    main()
