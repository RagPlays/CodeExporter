from .models import Segment

PLACEHOLDER_INDEX = 999_999
READING_GUIDE = (
    "Each file starts with a line '=== FILE: <relative path> ==='.\n"
    "A file split over several parts is marked '(part i/n)'; treat the parts as one file.\n"
    "Wait for the chunk marked END OF EXPORT before answering.\n"
)


def render_header(rel_path, index, total):
    part = f" (part {index}/{total})" if total > 1 else ""
    return f"=== FILE: {rel_path}{part} ==="


def render_segment(segment):
    body = segment.text if segment.text.endswith("\n") else segment.text + "\n"
    header = render_header(segment.rel_path, segment.index, segment.total)
    return f"{header}\n{body}\n"


def render_banner(index, total):
    return f"##### CHUNK {index}/{total} #####\n"


def render_footer(index, total):
    note = "END OF EXPORT" if index == total else f"CONTINUES IN CHUNK {index + 1}"
    return f"##### END OF CHUNK {index}/{total} - {note} #####\n"


def render_preamble(project, file_count, tree):
    sections = [f"PROJECT: {project}", f"FILES: {file_count}", READING_GUIDE]
    if tree:
        sections += ["STRUCTURE:", tree]
    return "\n".join(sections) + "\n\n"


def segment_overhead(rel_path):
    placeholder = Segment(rel_path, PLACEHOLDER_INDEX, PLACEHOLDER_INDEX, "")
    return len(render_segment(placeholder))


def frame_overhead():
    banner = render_banner(PLACEHOLDER_INDEX, PLACEHOLDER_INDEX)
    footer = render_footer(PLACEHOLDER_INDEX, PLACEHOLDER_INDEX)
    return len(banner) + len(footer)
