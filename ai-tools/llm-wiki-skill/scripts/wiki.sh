#!/usr/bin/env bash
# wiki.sh -- Wrapper for all wiki Python scripts.
#
# Resolves CWD to the user's wiki root (via .wiki-root marker) and
# PYTHONPATH to the skill's scripts/ directory.
#
# Usage: bash scripts/wiki.sh <script_name> [args...]

set -euo pipefail

# Resolve symlinks to find the real script location (skill's scripts/)
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
    DIR="$(cd "$(dirname "$SOURCE")" && pwd)"
    SOURCE="$(readlink "$SOURCE")"
    [[ "$SOURCE" != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd "$(dirname "$SOURCE")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Discover user's wiki root by walking up from CWD
find_wiki_root() {
    local dir="$PWD"
    while true; do
        if [ -f "$dir/.wiki-root" ]; then
            echo "$dir"
            return 0
        fi
        if [ "$dir" = "/" ]; then
            break
        fi
        dir="$(dirname "$dir")"
    done
    # Fallback: env var
    if [ -n "${LLM_WIKI_ROOT:-}" ] && [ -d "$LLM_WIKI_ROOT" ]; then
        echo "$LLM_WIKI_ROOT"
        return 0
    fi
    echo "ERROR: Wiki root not found. Set LLM_WIKI_ROOT or run /llm-wiki:init" >&2
    return 1
}

VAULT_DIR="$(find_wiki_root)"

if [ $# -lt 1 ]; then
    echo "Usage: bash scripts/wiki.sh <script_name> [args...]"
    echo ""
    echo "Available scripts:"
    for f in "$SCRIPT_DIR"/*.py; do
        name=$(basename "$f" .py)
        [ "$name" = "wiki_utils" ] && continue
        [ "$name" = "__init__" ] && continue
        echo "  $name"
    done
    exit 1
fi

SCRIPT_NAME="$1"
shift

TARGET="$SCRIPT_DIR/${SCRIPT_NAME}.py"

if [ ! -f "$TARGET" ]; then
    echo "Error: script not found: $TARGET" >&2
    exit 1
fi

cd "$VAULT_DIR"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}"
exec python3 "$TARGET" "$@"
