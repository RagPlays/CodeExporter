from .formatter import frame_overhead, render_segment


def pack(segments, chunk_chars, first_reserved):
    limit = chunk_chars - frame_overhead()
    chunks, current, size = [], [], first_reserved
    for segment in segments:
        length = len(render_segment(segment))
        if (current or size) and size + length > limit:
            chunks.append(current)
            current, size = [], 0
        current.append(segment)
        size += length
    if current:
        chunks.append(current)
    return chunks
