#!/bin/bash
# PostToolUse hook: rebuild graph.json after wiki file write (30s debounce)
set -euo pipefail

FILE=$(cat | python3 -c 'import sys,json; print(json.load(sys.stdin)["tool_input"]["file_path"])' 2>/dev/null || echo "")

if [ -z "$FILE" ]; then
    exit 0
fi

SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

WIKI_ROOT="$FILE"
while [ ! -f "$WIKI_ROOT/.wiki-root" ] && [ "$WIKI_ROOT" != "/" ] && [ "$WIKI_ROOT" != "." ]; do
    WIKI_ROOT="$(dirname "$WIKI_ROOT")"
done

if [ ! -f "$WIKI_ROOT/.wiki-root" ]; then
    exit 0
fi

GRAPH="$WIKI_ROOT/graph.json"
if [ -f "$GRAPH" ]; then
    AGE=$(( $(date +%s) - $(stat -f %m "$GRAPH" 2>/dev/null || stat -c %Y "$GRAPH" 2>/dev/null || echo 0) ))
    if [ "$AGE" -lt 30 ] 2>/dev/null; then
        exit 0
    fi
fi

cd "$WIKI_ROOT" && bash "$SKILL_DIR/scripts/wiki.sh" build_graph
