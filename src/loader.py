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
    """Return (SourceFile, "") on success, or (None, reason) when skipped."""
    try:
        data = path.read_bytes()
    except OSError:
        return None, "unreadable"
    text = _decode(data)
    if text is None:
        return None, "binary file"
    text = normalize(text, compact)
    if not text.strip():
        return None, "empty file"
    return SourceFile(path.relative_to(root).as_posix(), text), ""
