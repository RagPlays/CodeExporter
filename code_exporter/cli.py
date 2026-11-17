import argparse
import sys
from pathlib import Path

from . import config, filters
from .pipeline import run


def build_parser():
    parser = argparse.ArgumentParser(
        prog=Path(sys.argv[0]).name,
        description="Export source code into AI-friendly text chunks.",
    )
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("-o", "--output", type=Path, help="output .txt path")
    parser.add_argument("-e", "--ext", nargs="+", default=[], metavar="EXT",
                        help="only these extensions (py .cpp h)")
    parser.add_argument("-n", "--name", nargs="+", default=[], metavar="FILE",
                        help="also include these exact filenames (CMakeLists.txt)")
    parser.add_argument("-x", "--exclude-dir", nargs="+", default=[], metavar="DIR",
                        help="folder names, paths or globs to skip")
    parser.add_argument("--exclude-file", nargs="+", default=[], metavar="PATTERN",
                        help="file globs to skip (*.min.js)")
    parser.add_argument("--no-default-excludes", action="store_true",
                        help="do not skip .git, node_modules, build, ...")
    parser.add_argument("-c", "--chunk-size", type=int, default=config.DEFAULT_CHUNK_CHARS,
                        help="max characters per chunk")
    parser.add_argument("--max-file-kb", type=int, default=config.DEFAULT_MAX_FILE_KB,
                        help="skip files larger than this")
    parser.add_argument("--split-output", action="store_true",
                        help="write one .txt per chunk")
    parser.add_argument("--raw", action="store_true",
                        help="keep whitespace untouched")
    parser.add_argument("--no-tree", action="store_true",
                        help="omit the project structure")
    return parser


def _default_output(root):
    return Path.cwd() / f"{root.name}{config.OUTPUT_SUFFIX}"


def build_settings(args):
    root = args.root.resolve()
    default_dirs = () if args.no_default_excludes else config.DEFAULT_EXCLUDED_DIRS
    script_name = Path(sys.argv[0]).name
    package_name = Path(__file__).parent.name
    return config.Settings(
        root=root,
        output=(args.output or _default_output(root)).resolve(),
        extensions=frozenset(filters.normalize_extension(e) for e in args.ext),
        names=frozenset(n.lower() for n in args.name),
        excluded_dirs=(*default_dirs, package_name, *args.exclude_dir),
        excluded_files=(script_name, *args.exclude_file),
        chunk_chars=args.chunk_size,
        max_file_bytes=args.max_file_kb * config.BYTES_PER_KB,
        split_output=args.split_output,
        compact=not args.raw,
        include_tree=not args.no_tree,
    )


def format_report(result):
    if not result.file_count:
        return "No matching files found."
    outputs = "\n".join(f"  {path}" for path in result.outputs)
    summary = f"{result.file_count} files, {result.chunk_count} chunks, ~{result.token_estimate:,} tokens"
    return f"{summary}\n{outputs}"


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.root.is_dir():
        print(f"Not a directory: {args.root}", file=sys.stderr)
        return 1
    result = run(build_settings(args))
    print(format_report(result))
    return 0 if result.file_count else 1
