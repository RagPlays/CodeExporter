# ExportCode

Turn a project folder into AI-friendly text. ExportCode walks a directory, reads every text file in it (subfolders included), and writes them into one or more `.txt` files with a project tree and clear file markers. The output is split into chunks sized to fit an AI chat window, so you can paste a whole codebase into a conversation piece by piece.

- Pure Python, no dependencies
- Recursive by default, with sensible excludes (`.git`, `node_modules`, `build`, ...)
- Lists every file it saw and tells you why anything was skipped
- Long files are split at line breaks where possible and continued across chunks with `(part i/n)` markers
- Works on Linux and Windows

## Contents

- [Quick start](#quick-start)
- [Install as a command](#install-as-a-command)
  - [Linux](#linux)
  - [Windows](#windows)
- [Usage](#usage)
- [Options](#options)
- [What you see in the terminal](#what-you-see-in-the-terminal)
- [What ends up in the export](#what-ends-up-in-the-export)
- [What gets skipped](#what-gets-skipped)
- [Project layout](#project-layout)
- [Troubleshooting](#troubleshooting)

## Quick start

You need **Python 3.8 or newer**. Without installing anything:

```bash
python3 ExportCode.py /path/to/project      # Linux
py ExportCode.py C:\path\to\project         # Windows
```

This writes `<project name>_export.txt` into your **current directory**. To get a short `exportcode` command that works from anywhere, follow the next section.

## Install as a command

The installers don't copy anything. They create a small launcher that points back to this folder, so **keep the project folder where it is**. If you move it, run the installer again. Neither installer needs administrator rights.

### Linux

From the project folder:

```bash
bash install.sh
```

This does two things:

1. Symlinks `ExportCode.py` to `~/.local/bin/exportcode`
2. Symlinks the man page to `~/.local/share/man/man1/exportcode.1`

If `~/.local/bin` isn't in your `PATH` yet, the script prints the line to add to `~/.bashrc` or `~/.zshrc`. Most distributions (Fedora included) already have it. Then:

```bash
exportcode --help
man exportcode
```

To remove it again:

```bash
bash install.sh --uninstall
```

<details>
<summary>Manual install (no script)</summary>

```bash
mkdir -p ~/.local/bin ~/.local/share/man/man1
chmod +x ExportCode.py
ln -sf "$PWD/ExportCode.py" ~/.local/bin/exportcode
ln -sf "$PWD/man/ExportCode.1" ~/.local/share/man/man1/exportcode.1
```

It has to be a symlink (or a wrapper script), not a copy of `ExportCode.py` alone, because the script imports the `src/` folder next to it.

</details>

### Windows

Open PowerShell in the project folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

(The `-ExecutionPolicy Bypass` part only applies to this one run. It avoids the "running scripts is disabled" error.)

This does three things:

1. Finds a working Python 3.8+ (`py -3`, `python` or `python3`)
2. Creates `%LOCALAPPDATA%\ExportCode\bin\exportcode.cmd`, which runs `ExportCode.py` from this folder
3. Adds that folder to your **user** `PATH`

Open a **new** terminal (the old one doesn't see the PATH change), then:

```powershell
exportcode --help
```

It works in both PowerShell and `cmd.exe`. To remove it:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Uninstall
```

The man page is Linux-only. On Windows, `exportcode --help` shows the same information.

<details>
<summary>Manual install (no script)</summary>

Create `exportcode.cmd` in a folder that is on your `PATH` (for example `%USERPROFILE%\bin`) with this content, adjusting the path:

```bat
@echo off
py -3 "C:\Tools\ExportCode\ExportCode.py" %*
```

</details>

## Usage

```text
exportcode [options] [ROOT]
```

`ROOT` is the project folder and defaults to the current directory. All subfolders are included, except the default excludes.

```bash
# Export the current folder
exportcode

# Export another project, only Python and Markdown files
exportcode ~/projects/myapp -e py md

# C++ project: sources plus an exact filename, skipping tests
exportcode ~/projects/engine -e cpp h -n CMakeLists.txt -x tests

# Skip minified and lock files
exportcode . --exclude-file "*.min.js" "*.lock"

# Smaller chunks, one .txt per chunk, summary only
exportcode . -c 30000 --split-output -q

# Choose the output file
exportcode . -o ~/Desktop/myapp.txt
```

> **Tip:** Put `ROOT` *before* options that take several values (`-e`, `-n`, `-x`, `--exclude-file`). Those options consume every following word, so `exportcode -e py ~/proj` would treat `~/proj` as an extension. Ending the list with `--` also works.

## Options

| Option | Description |
| --- | --- |
| `ROOT` | Project folder to export (default: current folder) |
| `-e`, `--ext EXT...` | Only these extensions (`py`, `.cpp`, `h`). Default: all text files |
| `-n`, `--name FILE...` | Also include these exact filenames (e.g. `CMakeLists.txt`) |
| `-x`, `--exclude-dir DIR...` | Folder names, paths or globs to skip |
| `--exclude-file PATTERN...` | File globs to skip (e.g. `*.min.js`) |
| `--no-default-excludes` | Don't skip `.git`, `node_modules`, `build`, ... |
| `--max-file-kb KB` | Skip files larger than this (default: 500) |
| `-o`, `--output PATH` | Output file (default: `./<root name>_export.txt`) |
| `-c`, `--chunk-size CHARS` | Max characters per chunk (default: 60000, roughly 15,000 tokens) |
| `--split-output` | Write one file per chunk: `name_1.txt`, `name_2.txt`, ... (zero-padded from 10 chunks up) |
| `--raw` | Keep whitespace untouched (default trims trailing spaces and extra blank lines) |
| `--no-tree` | Leave the project structure out of the first chunk |
| `-q`, `--quiet` | Don't list files, print only the summary |
| `--hide-skipped` | List only exported files |
| `-V`, `--version` | Show the version |
| `-h`, `--help` | Show help |

Extension matching is case-insensitive, and the leading dot is optional. Set the `NO_COLOR` environment variable to turn off terminal colors.

**Exit status:** `0` if at least one file was exported, `1` if `ROOT` isn't a folder or nothing matched.

## What you see in the terminal

Every file found under `ROOT` is listed by its relative path. `+` means exported, `-` means skipped, with the reason in brackets. Excluded folders are listed once instead of file by file.

```text
Scanning /home/me/myapp (recursive)

  + ./afolder/file1
  - ./assets/image.png  (binary file)
  - ./empty.txt         (empty file)
  + ./file2
  - ./node_modules/     (excluded directory)
  + ./src/mod.py
  + ./sub/deep/c.py

5 files exported, 2 files skipped, 1 directory excluded, 1 chunk, ~134 tokens
  /home/me/myapp_export.txt
```

The token figure is an estimate (characters divided by 4).

## What ends up in the export

The first chunk starts with a short preamble: project name, file count, reading instructions for the AI, and the project tree. Each file follows, introduced by a marker line.

```text
##### CHUNK 1/2 #####
PROJECT: myapp
FILES: 12
Each file starts with a line '=== FILE: <relative path> ==='.
A file split over several parts is marked '(part i/n)'; treat the parts as one file.
Wait for the chunk marked END OF EXPORT before answering.

STRUCTURE:
src/
  cli.py
  pipeline.py
README.md

=== FILE: README.md ===
...file contents...

=== FILE: src/cli.py ===
...file contents...

##### END OF CHUNK 1/2 - CONTINUES IN CHUNK 2 #####
```

The final chunk ends with `END OF EXPORT`, which the reading instructions tell the AI to wait for. Paste the chunks into the chat in order.

With the default single output file, chunks are written one after another in the same `.txt` file, so you copy one chunk (from its `##### CHUNK` line to its `##### END OF CHUNK` line) at a time. Use `--split-output` if you'd rather have one file per chunk.

## What gets skipped

Skip reasons shown in the terminal:

| Reason | Meaning |
| --- | --- |
| `excluded directory` | Matches a default exclude or `-x` |
| `excluded file pattern` | Matches `--exclude-file` |
| `extension not selected` | Filtered out by `-e` / `-n` |
| `larger than N KB` | Bigger than `--max-file-kb` |
| `binary file` | Contains NUL bytes (images, archives, executables, ...) |
| `empty file` | Only whitespace |
| `previous export output` | Looks like an earlier export written next to the output path |
| `export tool` | ExportCode's own script and `src/` folder, so it never exports itself |
| `not a regular file` / `unreadable` | Broken symlinks, permission problems |

**Default excluded folders**, skipped at any depth: `.git`, `.svn`, `.hg`, `.idea`, `.vscode`, `.vs`, `node_modules`, `__pycache__`, `.venv`, `venv`, `env`, `build`, `dist`, `out`, `bin`, `obj`, `target`, `.mypy_cache`, `.pytest_cache`, `.cache`, `.gradle`.

If one of these holds real code in your project (say a source folder named `bin` or `env`), use `--no-default-excludes`, optionally combined with `-x` for the ones you do want to skip. Note that a project's own `src/` folder is *not* excluded.

## Project layout

```text
ExportCode.py        entry point
install.sh           Linux installer
install.ps1          Windows installer
man/ExportCode.1     man page
src/
  cli.py             argument parsing, help text, settings
  config.py          defaults and the Settings dataclass
  scanner.py         recursive walk, decides what to skip and why
  loader.py          reads and normalizes files, detects binaries
  segmenter.py       splits long files into pieces
  packer.py          groups pieces into chunks
  assembler.py       adds banners, preamble and footers
  formatter.py       text templates for markers and headers
  tree.py            renders the project structure
  writer.py          writes the output file(s)
  report.py          terminal listing and summary
  pipeline.py        ties the steps together
  models.py          small data classes
  filters.py         extension, glob and output-file checks
```

The flow is `scan` → `load` → `segment` → `pack` → `assemble` → `write`, with `report` printing what happened.

## Troubleshooting

**`exportcode: command not found` (Linux)**
`~/.local/bin` isn't in your `PATH`. Add `export PATH="$HOME/.local/bin:$PATH"` to `~/.bashrc` (or `~/.zshrc`) and open a new terminal. Check with `echo $PATH`.

**`exportcode` is not recognized (Windows)**
Open a *new* terminal after installing, since existing windows don't pick up the PATH change. If it still fails, check that `%LOCALAPPDATA%\ExportCode\bin` appears in your user PATH (Settings, then "Edit environment variables for your account").

**"running scripts is disabled on this system" (Windows)**
Use the command from the install section, which includes `-ExecutionPolicy Bypass`.

**It stopped working after I moved the folder**
The launcher points at the old location. Run the installer again from the new one.

**`man exportcode` finds nothing**
Make sure `~/.local/bin` is in your `PATH` (man derives `~/.local/share/man` from it), or read the page directly with `man ./man/ExportCode.1`.

**Python not found / too old**
Install Python 3.8 or newer. On Windows, get it from [python.org](https://www.python.org/downloads/) and tick "Add python.exe to PATH".

**A file I expected is missing**
Run without `-q`: every skipped file is listed with its reason. Common causes are a default excluded folder, the `--max-file-kb` limit, or an `-e` filter.
