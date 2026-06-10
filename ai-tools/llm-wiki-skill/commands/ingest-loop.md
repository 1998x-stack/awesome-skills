# /llm-wiki:ingest-loop -- Batch ingest all files in raw/

Scan raw/ for unprocessed files and process them in sequence.

## Usage

```
/llm-wiki:ingest-loop                # Default (Claude engine, interactive)
/llm-wiki:ingest-loop --engine=qwen  # Qwen API engine (non-interactive)
/llm-wiki:ingest-loop --reset        # Clear state and restart
```

## Steps

1. Run `bash <skill>/scripts/wiki.sh ingest_loop [--engine=qwen] [--reset]`
2. The script:
   - Scans `raw/` for supported files (.md/.pdf/.docx/.pptx/.xlsx/.html/.epub/.csv/.jsonl)
   - Computes SHA256 hash (first 16 chars) for each file
   - Compares against `raw/.ingest-state.json` to find new/changed files
   - Processes each file via ingest (Claude engine) or qwen_ingest.py (Qwen engine)
   - Retries once on failure, then marks as failed
   - Auto-completes: skips deleted files, cleans stale state entries
3. After all files processed: runs `relink.py` automatically to add [[wikilinks]]
4. Output: JSON summary with processed/failed/skipped counts

## State File

`raw/.ingest-state.json` tracks each file:
```json
{
  "raw/articles/example.md": {
    "hash": "abc123def4567890",
    "status": "done",
    "engine": "claude"
  }
}
```

Status values: `done`, `pending`, `failed`, `retry`
