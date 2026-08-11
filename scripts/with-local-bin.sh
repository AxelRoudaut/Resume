#!/usr/bin/env bash
# Run a command with the user-local binary directories on PATH.
#
# Editors spawn git — and therefore pre-commit — without sourcing the login
# shell profile, so tools installed to ~/.local/bin by `just init` (uv, biome)
# are absent from PATH and the hooks fail with "Executable `uv` not found",
# even though committing from a terminal works fine. Prepending the usual
# user-local locations makes the hooks behave identically from a terminal and
# from an editor's Source Control panel.
#
# Usage: scripts/with-local-bin.sh <command> [args...]
set -euo pipefail

for dir in "$HOME/.local/bin" "$HOME/.cargo/bin" /usr/local/bin; do
    if [ -d "$dir" ]; then
        case ":$PATH:" in
            *":$dir:"*) ;;
            *) PATH="$dir:$PATH" ;;
        esac
    fi
done
export PATH

if ! command -v "$1" >/dev/null 2>&1; then
    echo "$1 not found — run 'just init' to install the project tooling." >&2
    exit 1
fi

exec "$@"
