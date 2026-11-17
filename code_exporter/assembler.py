from .formatter import render_banner, render_footer, render_segment


def _assemble_chunk(index, total, segments, preamble):
    body = "".join(render_segment(segment) for segment in segments)
    return f"{render_banner(index, total)}{preamble}{body}{render_footer(index, total)}"


def assemble(chunks, preamble):
    total = len(chunks)
    return [
        _assemble_chunk(index, total, segments, preamble if index == 1 else "")
        for index, segments in enumerate(chunks, 1)
    ]
