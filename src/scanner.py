import os
from pathlib import Path

from . import filters
from .config import BYTES_PER_KB
from .models import ScanEntry


def _is_tool(path, settings):
    return path.resolve() in settings.skip_paths


def _dir_skip_reason(path, settings):
    if _is_tool(path, settings):
        return "export tool"
    if filters.matches_any(path, settings.root, settings.excluded_dirs):
        return "excluded directory"
    return ""


def _file_skip_reason(path, settings):
    if not path.is_file():
        return "not a regular file"
    if _is_tool(path, settings):
        return "export tool"
    if filters.matches_any(path, settings.root, settings.excluded_files):
        return "excluded file pattern"
    if not filters.is_included_type(path, settings.extensions, settings.names):
        return "extension not selected"
    if filters.is_output_artifact(path, settings.output):
        return "previous export output"
    if path.stat().st_size > settings.max_file_bytes:
        return f"larger than {settings.max_file_bytes // BYTES_PER_KB} KB"
    return ""


def scan(settings):
    """Walk ROOT recursively, yielding every file and every skipped directory."""
    for current, dirs, files in os.walk(settings.root):
        base = Path(current)
        kept = []
        for name in sorted(dirs):
            reason = _dir_skip_reason(base / name, settings)
            if reason:
                yield ScanEntry(base / name, reason, is_dir=True)
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(files):
            path = base / name
            yield ScanEntry(path, _file_skip_reason(path, settings))
