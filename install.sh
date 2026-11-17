#!/usr/bin/env bash
# Install (or remove) the `exportcode` command for the current user.
#
#   ./install.sh               install
#   ./install.sh --uninstall   remove
#
# This creates symlinks that point back to this folder, so keep the folder
# where it is (or run this script again after moving it). No root needed.

set -euo pipefail

NAME="exportcode"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SCRIPT="$HERE/ExportCode.py"
MAN_SOURCE="$HERE/man/ExportCode.1"

BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
MAN_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/man/man1"
BIN_LINK="$BIN_DIR/$NAME"
MAN_LINK="$MAN_DIR/$NAME.1"

say() { printf '%s\n' "$*"; }
die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

remove_link() {
    # Only remove links that point into this folder, never someone else's file.
    local link="$1" target="$2"
    if [ -L "$link" ] && [ "$(readlink "$link")" = "$target" ]; then
        rm -f "$link"
        say "Removed $link"
    elif [ -e "$link" ] || [ -L "$link" ]; then
        say "Left $link alone (it does not point to this folder)"
    fi
}

uninstall() {
    remove_link "$BIN_LINK" "$SCRIPT"
    remove_link "$MAN_LINK" "$MAN_SOURCE"
    say "Done."
}

install() {
    remove_link "$BIN_LINK"
    remove_link "$MAN_LINK"
    say "Done."
}

install() {
    command -v python3 >/dev/null 2>&1 || die "python3 was not found. Install Python 3.8 or newer."
    python3 -c 'import sys; sys.exit(sys.version_info < (3, 8))' \
        || die "Python 3.8 or newer is required (found $(python3 -V 2>&1))."
    [ -f "$SCRIPT" ] || die "Cannot find $SCRIPT. Run this script from the project folder."

    chmod +x "$SCRIPT"

    mkdir -p "$BIN_DIR"
    ln -sfn "$SCRIPT" "$BIN_LINK"
    say "Installed command: $BIN_LINK -> $SCRIPT"

    if [ -f "$MAN_SOURCE" ]; then
        mkdir -p "$MAN_DIR"
        ln -sfn "$MAN_SOURCE" "$MAN_LINK"
        say "Installed man page: $MAN_LINK"
    fi

    case ":$PATH:" in
        *":$BIN_DIR:"*)
            say ""
            say "Ready. Try:  $NAME --help    or    man $NAME"
            ;;
        *)
            say ""
            say "$BIN_DIR is not in your PATH yet. Add this line to ~/.bashrc or ~/.zshrc,"
            say "then open a new terminal:"
            say ""
            say "    export PATH=\"$BIN_DIR:\$PATH\""
            ;;
    esac
}

case "${1:-}" in
    "")                  install ;;
    -u|--uninstall)      uninstall ;;
    -h|--help)           sed -n '2,8p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' ;;
    *)                   die "Unknown option: $1 (use --uninstall or --help)" ;;
esac
