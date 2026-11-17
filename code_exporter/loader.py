import re

from .models import SourceFile

PRIMARY_ENCODING = "utf-8-sig"
FALLBACK_ENCODING = "latin-1"
NULL_BYTE = b"\x00"
BLANK_RUNS = re.compile(r"\n{3,}")


def _decode(data):
    if NULL_BYTE in data:
        return None
    try:
        return data.decode(PRIMARY_ENCODING)
    except UnicodeDecodeError:
        return data.decode(FALLBACK_ENCODING)


def normalize(text, compact):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not compact:
        return text
    stripped = "\n".join(line.rstrip() for line in text.split("\n"))
    return BLANK_RUNS.sub("\n\n", stripped).strip("\n")


def load_file(path, root, compact):
    try:
        text = _decode(path.read_bytes())
    except OSError:
        return None
    if text is None:
        return None
    text = normalize(text, compact)
    if not text.strip():
        return None
    return SourceFile(path.relative_to(root).as_posix(), text)


def load_files(paths, root, compact):
    loaded = (load_file(path, root, compact) for path in paths)
    return [file for file in loaded if file]
