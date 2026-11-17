import os
from pathlib import Path

from . import filters


def _keep_dir(directory, settings):
    return not filters.matches_any(directory, settings.root, settings.excluded_dirs)


def _keep_file(path, settings):
    return (
        path.is_file()
        and not filters.matches_any(path, settings.root, settings.excluded_files)
        and filters.is_included_type(path, settings.extensions, settings.names)
        and not filters.is_output_artifact(path, settings.output)
        and path.stat().st_size <= settings.max_file_bytes
    )


def scan(settings):
    for current, dirs, files in os.walk(settings.root):
        base = Path(current)
        dirs[:] = sorted(d for d in dirs if _keep_dir(base / d, settings))
        for name in sorted(files):
            path = base / name
            if _keep_file(path, settings):
                yield path
