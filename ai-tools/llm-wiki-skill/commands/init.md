# /llm-wiki:init -- Initialize a new knowledge base

Initialize the current directory as an llm-wiki knowledge base.

## Detection

1. Check current directory
   - No `.obsidian/` -> full initialization (copy all init-kit contents)
   - Has `.obsidian/` -> Obsidian injection mode (merge directories, don't overwrite existing files)

## Steps

1. Copy directory structure from `<skill>/resources/init-kit/` to current directory:
   - `.wiki-root` (marker file)
   - `raw/`, `raw/qa/`
   - `wiki/entities/`, `wiki/concepts/`, `wiki/syntheses/`
   - `journal/daily/`, `journal/reflections/`, `journal/judgments/`, `journal/growth/`
   - `maps/`
   - `index.md` (initial skeleton), `log.md` (empty)
   - `_schema/` (empty, for user overrides)
   - `templates/` (empty, for user overrides)

2. Write `.wiki-root` marker file (empty file)

3. Run `pip install -r <skill>/scripts/requirements.txt`

4. Write `.claude/settings.local.json` with PostToolUse hooks:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash <absolute-path-to-skill>/scripts/hooks/bm25.sh"
          },
          {
            "type": "command",
            "command": "bash <absolute-path-to-skill>/scripts/hooks/graph.sh"
          }
        ]
      }
    ]
  }
}
```

Replace `<absolute-path-to-skill>` with the actual skill installation path.

5. Output completion message:

```
LLM Wiki initialized in <directory>.

Next steps:
1. Put source materials in raw/ (markdown, PDF, DOCX, etc.)
2. Run /llm-wiki:ingest <file> to extract knowledge
3. Run /llm-wiki:query <question> to search your knowledge base
```
