import argparse
import functools
import sys
from pathlib import Path

from . import __version__, config, filters
from .pipeline import run
from .report import format_report, use_color

DESCRIPTION = """\
Export a project's source code into AI-friendly text chunks.

ExportCode walks ROOT recursively (every subfolder is included), reads all
text files it finds and writes them, with a project tree and clear file
markers, into one or more .txt files sized to fit an AI chat window.

While running it lists every file it found, with a '+' for exported files
and a '-' (plus the reason) for skipped ones such as binaries, images,
oversized files and excluded folders.
"""

EPILOG = """\
examples:
  %(prog)s                          export the current folder (all subfolders)
  %(prog)s ~/proj -e py md          only .py and .md files
  %(prog)s ~/proj -e cpp h -n CMakeLists.txt
                                    (C++ sources plus an exact filename)
  %(prog)s . -x tests docs/old      skip folders by name or path
  %(prog)s . --exclude-file "*.min.js" "*.lock"
  %(prog)s . -c 30000 --split-output
                                    (smaller chunks, one .txt per chunk)
  %(prog)s . -q                     only print the summary

notes:
  Put ROOT before options that take several values (-e, -n, -x,
  --exclude-file), or end them with '--', otherwise ROOT is read as a value.
  Folders skipped by default: {excludes}.
  Use --no-default-excludes to include them. Set NO_COLOR to disable colors.
  Exit status: 0 on success, 1 if nothing was exported or ROOT is invalid.
  See also: man ExportCode
"""


def build_parser():
    formatter = functools.partial(
        argparse.RawDescriptionHelpFormatter, max_help_position=30, width=88
    )
    parser = argparse.ArgumentParser(
        prog=Path(sys.argv[0]).name,
        usage="%(prog)s [options] [ROOT]",
        description=DESCRIPTION,
        epilog=EPILOG.format(excludes=", ".join(config.DEFAULT_EXCLUDED_DIRS)),
        formatter_class=formatter,
    )
    parser.add_argument("root", nargs="?", default=".", type=Path, metavar="ROOT",
                        help="project folder to export (default: current folder)")
    parser.add_argument("-V", "--version", action="version",
                        version=f"%(prog)s {__version__}")

    select = parser.add_argument_group("selecting files")
    select.add_argument("-e", "--ext", nargs="+", default=[], metavar="EXT",
                        help="only these extensions (py .cpp h); default: all text files")
    select.add_argument("-n", "--name", nargs="+", default=[], metavar="FILE",
                        help="also include these exact filenames (CMakeLists.txt)")
    select.add_argument("-x", "--exclude-dir", nargs="+", default=[], metavar="DIR",
                        help="folder names, paths or globs to skip")
    select.add_argument("--exclude-file", nargs="+", default=[], metavar="PATTERN",
                        help="file globs to skip (*.min.js)")
    select.add_argument("--no-default-excludes", action="store_true",
                        help="do not skip .git, node_modules, build, ...")
    select.add_argument("--max-file-kb", type=int, default=config.DEFAULT_MAX_FILE_KB,
                        metavar="KB",
                        help="skip files larger than this (default: %(default)s)")

    output = parser.add_argument_group("output")
    output.add_argument("-o", "--output", type=Path, metavar="PATH",
                        help="output .txt path (default: ./<root name>_export.txt)")
    output.add_argument("-c", "--chunk-size", type=int, default=config.DEFAULT_CHUNK_CHARS,
                        metavar="CHARS",
                        help="max characters per chunk (default: %(default)s)")
    output.add_argument("--split-output", action="store_true",
                        help="write one .txt per chunk (name_1.txt, name_2.txt, ...)")
    output.add_argument("--raw", action="store_true",
                        help="keep whitespace untouched")
    output.add_argument("--no-tree", action="store_true",
                        help="omit the project structure")

    display = parser.add_argument_group("terminal display")
    display.add_argument("-q", "--quiet", action="store_true",
                         help="do not list files, only print the summary")
    display.add_argument("--hide-skipped", action="store_true",
                         help="list only exported files, not skipped ones")
    return parser


def _default_output(root):
    return Path.cwd() / f"{root.name}{config.OUTPUT_SUFFIX}"


def _tool_paths():
    """Resolved paths of this tool, so it never exports itself (by location, not name)."""
    paths = {Path(__file__).resolve().parent}
    script = Path(sys.argv[0])
    if script.is_file():
        paths.add(script.resolve())
    return frozenset(paths)


def build_settings(args):
    root = args.root.resolve()
    default_dirs = () if args.no_default_excludes else config.DEFAULT_EXCLUDED_DIRS
    return config.Settings(
        root=root,
        output=(args.output or _default_output(root)).resolve(),
        extensions=frozenset(filters.normalize_extension(e) for e in args.ext),
        names=frozenset(n.lower() for n in args.name),
        excluded_dirs=(*default_dirs, *args.exclude_dir),
        excluded_files=tuple(args.exclude_file),
        skip_paths=_tool_paths(),
        chunk_chars=args.chunk_size,
        max_file_bytes=args.max_file_kb * config.BYTES_PER_KB,
        split_output=args.split_output,
        compact=not args.raw,
        include_tree=not args.no_tree,
        show_files=not args.quiet,
        show_skipped=not args.hide_skipped,
    )


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.root.is_dir():
        print(f"Not a directory: {args.root}", file=sys.stderr)
        return 1
    settings = build_settings(args)
    if settings.show_files:
        print(f"Scanning {settings.root} (recursive)\n")
    result = run(settings)
    print(format_report(result, settings, color=use_color()))
    return 0 if result.file_count else 1
