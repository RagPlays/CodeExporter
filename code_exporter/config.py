from dataclasses import dataclass
from pathlib import Path

DEFAULT_EXCLUDED_DIRS = (
    ".git", ".svn", ".hg", ".idea", ".vscode", ".vs",
    "node_modules", "__pycache__", ".venv", "venv", "env",
    "build", "dist", "out", "bin", "obj", "target",
    ".mypy_cache", ".pytest_cache", ".cache", ".gradle",
)
DEFAULT_CHUNK_CHARS = 60_000
DEFAULT_MAX_FILE_KB = 500
BYTES_PER_KB = 1024
CHARS_PER_TOKEN = 4
OUTPUT_SUFFIX = "_export.txt"


@dataclass(frozen=True)
class Settings:
    root: Path
    output: Path
    extensions: frozenset
    names: frozenset
    excluded_dirs: tuple
    excluded_files: tuple
    chunk_chars: int
    max_file_bytes: int
    split_output: bool
    compact: bool
    include_tree: bool
