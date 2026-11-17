from .formatter import frame_overhead, segment_overhead
from .models import Segment


def _bounded_lines(text, limit):
    for line in text.splitlines(keepends=True):
        if len(line) <= limit:
            yield line
        else:
            yield from (line[i:i + limit] for i in range(0, len(line), limit))


def _break_index(buffer):
    floor = len(buffer) // 2
    for i in range(len(buffer) - 1, floor - 1, -1):
        if not buffer[i].strip():
            return i + 1
    return len(buffer)


def split_text(text, limit):
    pieces, buffer, size = [], [], 0
    for line in _bounded_lines(text, limit):
        while buffer and size + len(line) > limit:
            cut = _break_index(buffer)
            pieces.append("".join(buffer[:cut]))
            buffer = buffer[cut:]
            size = sum(map(len, buffer))
        buffer.append(line)
        size += len(line)
    if buffer:
        pieces.append("".join(buffer))
    return pieces


def segment_file(file, chunk_chars):
    limit = max(chunk_chars - frame_overhead() - segment_overhead(file.rel_path), 1)
    pieces = split_text(file.text, limit)
    return [Segment(file.rel_path, i, len(pieces), p) for i, p in enumerate(pieces, 1)]
