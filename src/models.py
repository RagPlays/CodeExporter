from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceFile:
    rel_path: str
    text: str


@dataclass(frozen=True)
class Segment:
    rel_path: str
    index: int
    total: int
    text: str


@dataclass(frozen=True)
class ScanEntry:
    """One thing found while walking the tree. An empty reason means 'candidate'."""
    path: Path
    reason: str = ""
    is_dir: bool = False


@dataclass(frozen=True)
class FileReport:
    """What happened to one file (or skipped directory), for terminal output."""
    rel_path: str
    included: bool
    reason: str = ""
    is_dir: bool = False
