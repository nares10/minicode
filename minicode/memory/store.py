"""Memory system for minicode.

Stores context in markdown files under .minicode/memory/ so it survives
across sessions:

- project.md   facts about the repo that stay useful (accumulates)
- session.md   what the last session did (overwritten each session)

project.md is loaded and kept. session.md is loaded as read-only context
about the *previous* session; this session starts with an empty session
memory and overwrites the file when it ends.
"""

from pathlib import Path
from datetime import datetime

# Caps so the files cannot grow without bound.
MAX_ITEMS = 20
MAX_SECTIONS = 20


class Memory:
    """Memory system for storing agent context."""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = Path(workspace_dir)
        self.memory_dir = self.workspace_dir / ".minicode" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.project_memory = {}
        self.session_memory = {}
        self.previous_session = {}
        self._load_memory()

    @property
    def project_file(self) -> Path:
        return self.memory_dir / "project.md"

    @property
    def session_file(self) -> Path:
        return self.memory_dir / "session.md"

    def _load_memory(self):
        """Load memory from markdown files. Called at session start."""
        self.project_memory = self._parse_markdown(self.project_file)
        # Last session's notes are context, not something to append to.
        self.previous_session = self._parse_markdown(self.session_file)
        self.session_memory = {}

    def _parse_markdown(self, file_path: Path) -> dict:
        """Parse markdown file into memory dict."""
        if not file_path.exists():
            return {}

        try:
            content = file_path.read_text()
        except OSError:
            return {}

        memory = {}
        current_section = None

        for line in content.split("\n"):
            if line.startswith("## "):
                current_section = line[3:].strip()
                memory[current_section] = []
            elif current_section and line.strip():
                memory[current_section].append(line.strip().lstrip("- "))

        return memory

    def _save_markdown(self, file_path: Path, memory: dict, title: str):
        """Save memory dict to markdown file, newest items last, capped."""
        lines = [f"# {title}", "", f"_updated {datetime.now():%Y-%m-%d %H:%M:%S}_", ""]

        for section in list(memory)[-MAX_SECTIONS:]:
            lines.append(f"## {section}")
            lines.append("")
            for item in memory[section][-MAX_ITEMS:]:
                lines.append(f"- {item}")
            lines.append("")

        try:
            file_path.write_text("\n".join(lines))
        except OSError as e:
            # Losing memory must never take down the session.
            print(f"[memory] could not write {file_path}: {e}")

    def save(self):
        """Save all memory to markdown files. Called at session end."""
        self._save_markdown(self.project_file, self.project_memory, "Project memory")
        self._save_markdown(self.session_file, self.session_memory, "Last session")

    def add_project_info(self, key: str, value: str):
        """Add information to project memory."""
        if key not in self.project_memory:
            self.project_memory[key] = []
        if value not in self.project_memory[key]:
            self.project_memory[key].append(value)

    def add_session_info(self, key: str, value: str):
        """Add information to session memory."""
        if key not in self.session_memory:
            self.session_memory[key] = []
        if value not in self.session_memory[key]:
            self.session_memory[key].append(value)

    def get_memory_text(self) -> str:
        """Get memory as formatted text for the system prompt."""
        if not self.project_memory and not self.previous_session:
            return ""

        lines = ["## Memory from Previous Sessions", ""]

        if self.project_memory:
            lines.append("### Project Information")
            for section, items in self.project_memory.items():
                lines.append(f"**{section}:**")
                for item in items[-5:]:
                    lines.append(f"- {item}")
                lines.append("")

        if self.previous_session:
            lines.append("### What the last session did")
            for section, items in self.previous_session.items():
                lines.append(f"**{section}:**")
                for item in items[-3:]:
                    lines.append(f"- {item}")
                lines.append("")

        return "\n".join(lines)

    def record_command(self, command: str, result: str):
        """Record a command and its result."""
        self.add_session_info("Recent Commands", f"{command} -> {result[:100]}")

    def record_file_access(self, file_path: str):
        """Record file access."""
        self.add_project_info("Commonly Accessed Files", file_path)

    def record_task(self, task: str, outcome: str):
        """Record a task and its outcome."""
        self.add_session_info("Completed Tasks", f"{task[:120]}: {outcome[:100]}")

    def clear_session_memory(self):
        """Clear session-specific memory."""
        self.session_memory = {}
        self.previous_session = {}
