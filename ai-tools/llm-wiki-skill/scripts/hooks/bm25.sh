#!/bin/bash
# PostToolUse hook: update BM25 index after wiki file write
# Reads tool_input.file_path from stdin JSON (Claude Code hooks protocol)
set -euo pipefail

FILE=$(cat | python3 -c 'import sys,json; print(json.load(sys.stdin)["tool_input"]["file_path"])' 2>/dev/null || echo "")

if [ -z "$FILE" ]; then
    exit 0
fi

# Resolve SKILL_DIR from this script's location
SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# Discover wiki root from FILE path by walking up
WIKI_ROOT="$FILE"
while [ ! -f "$WIKI_ROOT/.wiki-root" ] && [ "$WIKI_ROOT" != "/" ] && [ "$WIKI_ROOT" != "." ]; do
    WIKI_ROOT="$(dirname "$WIKI_ROOT")"
done

if [ ! -f "$WIKI_ROOT/.wiki-root" ]; then
    exit 0
fi

cd "$WIKI_ROOT" && bash "$SKILL_DIR/scripts/wiki.sh" bm25_index update "$FILE"
