# Minicode Harbor Adapter

This adapter allows the [minicode](../minicode) terminal coding agent to be evaluated using the [Harbor](https://github.com/harbor-framework/harbor) framework.

## What is Harbor?

Harbor is a framework for evaluating and optimizing AI agents and language models. It provides:
- Agent evaluation against benchmarks like Terminal-Bench, SWE-Bench, and more
- Parallel execution across environments (local and cloud)
- Trajectory visualization and analysis
- Custom agent integration

## Installation

### Option 1: Local Harbor Installation (Modify Harbor Source)

To use this adapter with a local Harbor installation:

1. **Copy the agent file to Harbor's agents directory:**
   ```bash
   cp minicode_agent.py /path/to/harbor/src/harbor/agents/installed/
   ```

2. **Register the agent in Harbor's agent name enum:**
   Edit `/path/to/harbor/src/harbor/models/agent/name.py` and add:
   ```python
   class AgentName(str, Enum):
       # ... existing agents ...
       MINICODE = "minicode"
   ```

3. **Register the agent in the factory:**
   Edit `/path/to/harbor/src/harbor/agents/factory.py` and add:
   ```python
   from harbor.agents.installed.minicode_agent import MinicodeAgent

   class AgentFactory:
       _AGENT_MAP = {
           # ... existing agents ...
           AgentName.MINICODE: MinicodeAgent,
       }
   ```

4. **Run Harbor with minicode:**
   ```bash
   harbor run \
     --dataset terminal-bench@2.0 \
     --agent minicode \
     --model google/gemini-3.1-flash-lite \
     --n-concurrent 4 \
     --ve GEMINI_API_KEY="$GEMINI_API_KEY" \
     --ae MINICODE_PATH="/path/to/minicode"
   ```

### Option 2: Use as External Agent (Without Modifying Harbor)

For local evaluation without modifying Harbor source:

1. **Set environment variables:**
   ```bash
   export GEMINI_API_KEY="your-api-key"
   export MODEL="gemini-3.1-flash-lite"
   export MINICODE_PATH="/home/naresh-dewasi/projects/ai_code/minicode"
   ```

2. **Create a custom evaluation script:**
   ```python
   import asyncio
   from harbor_adapter.minicode_agent import MinicodeAgent
   from harbor.environments.local import LocalEnvironment
   from harbor.models.agent.context import AgentContext

   async def evaluate():
       agent = MinicodeAgent(
           logs_dir=Path("./logs"),
           model_name="google/gemini-3.1-flash-lite"
       )
       
       env = LocalEnvironment()
       context = AgentContext()
       
       await agent.setup(env)
       await agent.run("List files in current directory", env, context)
       
       print(f"Exit code: {context.exit_code}")
       print(f"Output: {context.stdout}")

   asyncio.run(evaluate())
   ```

### Option 3: Hosted Harbor (ACP)

For use with Harbor's hosted service via ACP (Agent Control Protocol):

1. **Push this adapter to a GitHub repository**
2. **Connect the repository in your Harbor profile settings**
3. **Use the harbor-agent.json manifest** to configure the agent
4. **Submit jobs through Harbor's web interface**

## Configuration

### Environment Variables

- `GEMINI_API_KEY` (required): Your Google Gemini API key
- `MODEL` (optional): Model to use (default: `gemini-3.1-flash-lite`)
- `MINICODE_PATH` (optional): Path to minicode installation (default: `/minicode`)

### Supported Models

- `gemini-3.1-flash-lite` - Recommended for high-volume, cost-efficient evaluation
- `gemini-3.6-flash` - Previous-generation Flash model
- `gemini-3.5-flash` - Legacy Flash model
- Other Gemini models supported by the Google GenAI SDK

## Usage Examples

### Basic Evaluation

```bash
harbor run \
  --dataset terminal-bench@2.0 \
  --agent minicode \
  --model google/gemini-3.1-flash-lite \
  --n-concurrent 2
```

### With Custom Task Filter

```bash
harbor run \
  --dataset terminal-bench@2.0 \
  --agent minicode \
  --model google/gemini-3.1-flash-lite \
  --filter "task_name=git_commit" \
  --n-concurrent 1
```

### Multiple Attempts

```bash
harbor run \
  --dataset terminal-bench@2.0 \
  --agent minicode \
  --model google/gemini-3.1-flash-lite \
  --n-attempts 3 \
  --n-concurrent 2
```

## Development

### Testing the Adapter Locally

```bash
# Set up environment
export GEMINI_API_KEY="your-key"
export MODEL="gemini-3.1-flash-lite"
export MINICODE_PATH="/home/naresh-dewasi/projects/ai_code/minicode"

# Test with a simple instruction
python -c "
import asyncio
from minicode_agent import MinicodeAgent
from harbor.environments.local import LocalEnvironment
from harbor.models.agent.context import AgentContext

async def test():
    agent = MinicodeAgent(logs_dir=Path('./logs'))
    env = LocalEnvironment()
    context = AgentContext()
    await agent.setup(env)
    await agent.run('echo hello', env, context)
    print(context.stdout)

asyncio.run(test())
"
```

## Troubleshooting

### Agent Not Found

If Harbor doesn't recognize the `minicode` agent:
- Verify the agent is registered in `AgentName` enum
- Check the factory mapping includes `MinicodeAgent`
- Restart Harbor to reload the agent registry

### API Key Issues

If you get authentication errors:
- Ensure `GEMINI_API_KEY` is set in the environment
- Check the API key is valid and has sufficient quota
- Verify the key is passed with `--ve GEMINI_API_KEY="$GEMINI_API_KEY"`

### Path Issues

If minicode can't be found:
- Set `MINICODE_PATH` to the absolute path of your minicode installation
- Ensure the path is accessible from within the Harbor container
- For local evaluation, use the absolute path on your host machine

## License

This adapter follows the same license as the minicode project.

## References

- [Harbor Framework](https://github.com/harbor-framework/harbor)
- [Harbor Documentation](https://www.harborframework.com/docs)
- [Minicode](../minicode)
- [Google GenAI SDK](https://googleapis.github.io/python-genai/)
