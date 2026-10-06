# minicode

A minimal coding agent for the terminal — about 500 lines of Python. It reads
and writes files, runs shell commands (so: git add / commit / push), and
searches the web.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## Use

```bash
.venv/bin/python3 -m minicode.cli              # interactive
.venv/bin/python3 -m minicode.cli -p "add a test for parse_args"
.venv/bin/python3 -m minicode.cli --yolo       # no approval prompts
```

In the REPL: `/help`, `/clear`, `/yolo`, `/cwd [path]`, `/exit`.

Every write, edit, and shell command asks for approval first (`y` / `N` /
`a` to always allow that tool for the session). `read_file` and web search
run without asking.

## Tools

| Tool | Runs | Notes |
| --- | --- | --- |
| `read_file` | locally | line-numbered, with `offset`/`limit` |
| `write_file` | locally | creates parent dirs, overwrites whole file |
| `edit_file` | locally | one unique exact-string replacement |
| `bash` | locally | non-interactive; this is how git works |

## Layout

One package per concern; each `__init__.py` is that package's public surface.

```
minicode/
  agent/     config.py    model choice, run limits, system prompt
             loop.py      the streaming agent loop
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
keep the newest 20 items per heading. `/clear` drops both the conversation and
the session memory. Pass `enable_memory=False` to `Agent` to turn it off.

## How the loop works

`Agent.run` appends the user message, then repeats: stream a request to
`claude-opus-5-5` with adaptive thinking → append the assistant turn →
if it ended with `tool_use` blocks, run them all and append every result in
one user message → go again. It stops when a turn ends without tool calls.
`pause_turn` (a long server-side search) is resumed by re-sending; `refusal`
and `max_tokens` end the turn with a note.

Two details worth knowing if you extend it:

- Client tools set `eager_input_streaming`, so large inputs stream as they are
  generated rather than arriving in one burst. The tradeoff is that the parsed
  input can be truncated, so `validate_input` checks it before anything runs.
- Tool results for one assistant turn must go back in a *single* user message.
  Splitting them teaches the model to stop making parallel calls.
