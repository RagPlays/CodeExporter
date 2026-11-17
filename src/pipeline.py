from dataclasses import dataclass, field

from .assembler import assemble
from .config import CHARS_PER_TOKEN
from .formatter import render_preamble
from .loader import load_file
from .models import FileReport
from .packer import pack
from .scanner import scan
from .segmenter import segment_file
from .tree import render_tree
from .writer import write_output


@dataclass(frozen=True)
class ExportResult:
    outputs: list
    file_count: int
    chunk_count: int
    char_count: int
    reports: list = field(default_factory=list)

    @property
    def token_estimate(self):
        return self.char_count // CHARS_PER_TOKEN


def _build_preamble(files, settings):
    tree = render_tree([f.rel_path for f in files]) if settings.include_tree else ""
    return render_preamble(settings.root.name, len(files), tree)


def _collect(settings):
    files, reports = [], []
    for entry in scan(settings):
        rel = entry.path.relative_to(settings.root).as_posix()
        if entry.reason:
            reports.append(FileReport(rel, False, entry.reason, entry.is_dir))
            continue
        file, reason = load_file(entry.path, settings.root, settings.compact)
        if file:
            files.append(file)
        reports.append(FileReport(rel, file is not None, reason))
    reports.sort(key=lambda report: report.rel_path.lower())
    return files, reports


def run(settings):
    files, reports = _collect(settings)
    if not files:
        return ExportResult([], 0, 0, 0, reports)
    preamble = _build_preamble(files, settings)
    segments = [s for f in files for s in segment_file(f, settings.chunk_chars)]
    chunks = pack(segments, settings.chunk_chars, len(preamble))
    texts = assemble(chunks, preamble)
    outputs = write_output(texts, settings)
    return ExportResult(outputs, len(files), len(chunks), sum(map(len, texts)), reports)
