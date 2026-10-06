# minicode

A minimal coding agent for the terminal — about 1,100 lines of Python. It has
exactly one tool, `bash`, and it remembers your repo between sessions.

Three things make it different from the usual agent:

- **One tool.** No `read_file`, no `write_file`, no `edit_file`. `cat`, `sed`,
  `grep` and `git` already exist, and the model already knows them.
- **Memory that survives restarts.** Markdown in `.minicode/memory/`, loaded
  into the system prompt on start, written back on exit.
- **Bring your own model.** Gemini, Groq, or fully local via Ollama.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Then set a key for whichever provider you want — see below.

## Models

The provider is auto-detected from the environment, in this order:

| Priority | Condition | Provider |
| --- | --- | --- |
| 1 | `GROQ_API_KEY` is set | Groq (`llama-3.3-70b-versatile`) |
| 2 | `OLLAMA_BASE_URL` is set, or `ollama` is installed | Ollama, local (`llama3.3:70b`) |
| 3 | `GEMINI_API_KEY` is set | Gemini (`gemini-3.1-flash-lite`) |

```bash
export GEMINI_API_KEY=...      # or GROQ_API_KEY, or run Ollama locally
export MODEL=gemini-3.1-flash  # override the default model name
```

Groq and OpenAI-compatible endpoints need their own package
(`pip install groq`, `pip install openai`); Gemini and Ollama work with the
base requirements. The Groq client has no function calling, so it parses bash
commands out of the text instead.

## Use

```bash
.venv/bin/python3 -m minicode.cli              # interactive
.venv/bin/python3 -m minicode.cli -p "add a test for parse_args"
.venv/bin/python3 -m minicode.cli --yolo       # no approval prompts
```

In the REPL: `/help`, `/clear`, `/yolo`, `/cwd [path]`, `/exit`.

Every bash command asks for approval first (`y` / `N` / `a` to always allow
that tool for the session). `--yolo` and `/yolo` skip the prompt.

Other environment variables:

| Variable | Effect |
| --- | --- |
| `MINICODE_MODEL` | provider to use, bypassing auto-detection (default `gemini`) |
| `MINICODE_MAX_TURNS` | stop an unattended run after N turns (`0` = no cap) |

## Tools

| Tool | Runs | Notes |
| --- | --- | --- |
| `bash` | locally | non-interactive, 120s default timeout; needs approval |

That's the whole toolkit. The system prompt teaches the model to read with
`cat`/`head`/`tail`, write with `cat > file << 'EOF'`, edit with `sed -i`, and
search with `grep`.

## Memory

Context persists across sessions as markdown in `.minicode/memory/`
(gitignored), loaded into the system prompt when a session starts and written
back when it ends:

| File | Holds | Lifetime |
| --- | --- | --- |
| `project.md` | facts about the repo, e.g. files touched often | accumulates |
| `session.md` | what the last session did | overwritten each session |

A session starts with empty session memory and reads `session.md` as read-only
context about the *previous* run, so it does not grow without bound. Both files
keep the newest 20 items per heading, across at most 20 headings. The agent
records commands, file accesses and task outcomes as it works. `/clear` drops
both the conversation and the session memory. Pass `enable_memory=False` to
`Agent` to turn it off.

## Layout

One package per concern; each `__init__.py` is that package's public surface.

```
minicode/
  agent/     config.py    model choice, run limits, system prompt
             loop.py      the agent loop
  cli/       app.py       REPL, approval prompts, argument parsing
             colors.py    ANSI escapes
             __main__.py  python -m minicode.cli
  memory/    store.py     markdown memory, loaded at start and saved at exit
  models/    base.py      the BaseModel interface
             factory.py   create_model / auto_detect_model
             gemini.py groq.py ollama.py openai.py
  tools/     bash.py      the bash tool
             registry.py  schemas, lookup by name, input validation
```

Import from the package, not the module inside it — `from minicode.agent import
Agent`, `from minicode.tools import CLIENT_TOOLS`. The layout inside a package
can change without touching callers.

## How the loop works

`Agent.run` creates a chat with the system prompt (plus memory), then repeats:
stream a turn → print the text → if the turn produced function calls, run each
one and send the result back → go again. It stops when a turn comes back
without function calls, or when `MINICODE_MAX_TURNS` is hit.

Providers sit behind `BaseModel`, so the loop never names a vendor. A new
provider needs five methods — `create_chat`, `send_message_stream`, `get_text`,
`get_function_calls`, `format_function_response` — and an entry in
`models/factory.py`.

`validate_input` checks a tool's input before anything runs, because a
streamed, partially-parsed input can arrive truncated.

## Known rough edges

- `-m/--model` is parsed but has no effect: the CLI passes it as `model` without
  a `model_type`, and `Agent.__init__` only reaches `create_model` when
  `model_type` is given, so auto-detection always wins. Use `GROQ_API_KEY` /
  `GEMINI_API_KEY` / `OLLAMA_BASE_URL` and `MODEL` instead.
- `requirements.txt` lists `anthropic`, which nothing imports, and omits what
  the code actually needs: `google-genai`, `python-dotenv`, `requests`.
- `models/openai.py` exists but is not wired into `create_model`.
