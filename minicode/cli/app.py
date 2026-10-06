"""The REPL: approval prompts, output formatting, argument parsing."""

from __future__ import annotations

import argparse
import os
import sys

from google.genai import errors

from ..agent import MODEL, Agent, preview
from .colors import BOLD, CYAN, DIM, OFF, RED, YELLOW


HELP = """commands:
  /help           show this
  /clear          forget the conversation so far
  /yolo           stop asking for approval this session
  /cwd [path]     show or change the working directory
  /exit           quit
anything else is sent to the model."""


class Session:
    def __init__(self, yolo: bool, model: str = MODEL):
        self.yolo = yolo
        self.always: set[str] = set()
        self.in_thinking = False
        self.agent = Agent(cwd=os.getcwd(), approve=self.approve, model=model)

    # -- output ------------------------------------------------------------

    def on_text(self, text: str) -> None:
        if self.in_thinking:
            sys.stdout.write(OFF + "\n")
            self.in_thinking = False
        sys.stdout.write(text)
        sys.stdout.flush()

    def on_thinking(self, text: str) -> None:
        if not self.in_thinking:
            sys.stdout.write(DIM)
            self.in_thinking = True
        sys.stdout.write(text)
        sys.stdout.flush()

    def on_tool(self, name: str, data: dict) -> None:
        if self.in_thinking:
            sys.stdout.write(OFF + "\n")
            self.in_thinking = False
        print(f"\n{CYAN}• {name}{OFF} {DIM}{preview(name, data)}{OFF}")

    # -- approval ----------------------------------------------------------

    def approve(self, name: str, data: dict) -> bool:
        if self.yolo or name in self.always:
            return True
        if not sys.stdin.isatty():
            print(f"{YELLOW}  (no terminal to ask; declined){OFF}")
            return False
        if name in ("write_file", "edit_file"):
            print(f"{DIM}  {_diff_hint(name, data)}{OFF}")
        try:
            answer = input(f"{YELLOW}  run this? [y/N/a=always {name}] {OFF}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return False
        if answer == "a":
            self.always.add(name)
            return True
        return answer in ("y", "yes")

    # -- turns -------------------------------------------------------------

    def send(self, text: str) -> None:
        try:
            self.agent.run(text, self.on_text, self.on_thinking, self.on_tool)
        except errors.APIError as e:
            print(f"\n{RED}API error {e.code}: {e.message}{OFF}")
        except Exception as e:
            print(f"\n{RED}Error: {e}{OFF}")
        finally:
            if self.in_thinking:
                sys.stdout.write(OFF)
                self.in_thinking = False
            print()

    def command(self, line: str) -> bool:
        """Handle a /command. Returns False to quit."""
        parts = line.split(maxsplit=1)
        name, arg = parts[0], (parts[1] if len(parts) > 1 else "")
        if name in ("/exit", "/quit"):
            return False
        if name == "/help":
            print(HELP)
        elif name == "/clear":
            self.agent.chat = None
            if self.agent.memory:
                self.agent.memory.clear_session_memory()
            print(f"{DIM}conversation and session memory cleared{OFF}")
        elif name == "/yolo":
            self.yolo = True
            print(f"{YELLOW}approval prompts off for this session{OFF}")
        elif name == "/cwd":
            if arg:
                try:
                    os.chdir(os.path.expanduser(arg))
                    self.agent.cwd = os.getcwd()
                except OSError as e:
                    print(f"{RED}{e}{OFF}")
            print(os.getcwd())
        else:
            print(f"unknown command: {name} (try /help)")
        return True


def _diff_hint(name: str, data: dict) -> str:
    if name == "write_file":
        content = data.get("content", "")
        return f"{len(content)} chars, {content.count(chr(10)) + 1} lines"
    old, new = data.get("old_string", ""), data.get("new_string", "")
    return f"-{old.count(chr(10)) + 1} / +{new.count(chr(10)) + 1} lines"


def main() -> int:
    parser = argparse.ArgumentParser(prog="minicode", description=__doc__)
    parser.add_argument("-p", "--prompt", help="run one prompt and exit")
    parser.add_argument(
        "-m",
        "--model",
        default=MODEL,
        help=f"model id (default {MODEL}; also settable with MINICODE_MODEL)",
    )
    parser.add_argument(
        "--yolo",
        action="store_true",
        help="run every tool without asking for approval",
    )
    args = parser.parse_args()

    session = Session(yolo=args.yolo, model=args.model)

    try:
        if args.prompt:
            session.send(args.prompt)
            return 0

        print(f"{BOLD}minicode{OFF} {DIM}{args.model} in {os.getcwd()} — /help for commands{OFF}")
        while True:
            try:
                line = input(f"{BOLD}> {OFF}").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return 0
            if not line:
                continue
            if line.startswith("/"):
                if not session.command(line):
                    return 0
                continue
            session.send(line)
    finally:
        session.agent.cleanup()


if __name__ == "__main__":
    sys.exit(main())
