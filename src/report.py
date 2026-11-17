import os
import sys

GREEN = "\033[32m"
DIM = "\033[2m"
RESET = "\033[0m"


def use_color(stream=None):
    stream = stream or sys.stdout
    return stream.isatty() and "NO_COLOR" not in os.environ


def display_path(report):
    return f"./{report.rel_path}{'/' if report.is_dir else ''}"


def _paint(text, code, color):
    return f"{code}{text}{RESET}" if color else text


def format_file_list(reports, show_skipped, color):
    shown = [r for r in reports if r.included or show_skipped]
    width = max((len(display_path(r)) for r in shown), default=0)
    lines = []
    for report in shown:
        path = display_path(report)
        if report.included:
            lines.append(_paint(f"  + {path}", GREEN, color))
        else:
            lines.append(_paint(f"  - {path.ljust(width)}  ({report.reason})", DIM, color))
    return "\n".join(lines)


def _count(number, singular, plural):
    return f"{number} {singular if number == 1 else plural}"


def format_summary(result):
    skipped_files = sum(1 for r in result.reports if not r.included and not r.is_dir)
    skipped_dirs = sum(1 for r in result.reports if r.is_dir)
    parts = [f"{_count(result.file_count, 'file', 'files')} exported"]
    if skipped_files:
        parts.append(f"{_count(skipped_files, 'file', 'files')} skipped")
    if skipped_dirs:
        parts.append(f"{_count(skipped_dirs, 'directory', 'directories')} excluded")
    parts += [_count(result.chunk_count, "chunk", "chunks"), f"~{result.token_estimate:,} tokens"]
    return ", ".join(parts)


def format_report(result, settings, color=False):
    sections = []
    if settings.show_files and result.reports:
        listing = format_file_list(result.reports, settings.show_skipped, color)
        if listing:
            sections.append(listing)
    if not result.file_count:
        sections.append("No matching files found.")
    else:
        outputs = "\n".join(f"  {path}" for path in result.outputs)
        sections.append(f"{format_summary(result)}\n{outputs}")
    return "\n\n".join(sections)
