#!/usr/bin/env python3
"""Batch ingest scanner with hash-based tracking and breakpoint resume.

Scans raw/ for files not yet ingested (by content hash), processes each
via the ingest command, and runs relink on completion.

Usage:
    python3 scripts/ingest_loop.py                # Claude engine (default)
    python3 scripts/ingest_loop.py --engine=qwen   # Qwen API engine
    python3 scripts/ingest_loop.py --reset         # Clear state and restart
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from wiki_utils import VAULT_DIR

STATE_FILE = VAULT_DIR / "raw" / ".ingest-state.json"
RAW_DIR = VAULT_DIR / "raw"

SUPPORTED_EXTS = {".md", ".pdf", ".docx", ".pptx", ".xlsx", ".html", ".epub", ".csv", ".jsonl"}


def file_hash(path: Path) -> str:
    """SHA256 first 16 hex chars of file content."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_state() -> dict:
    """Load ingest state, return {} if absent or corrupt."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def scan_files() -> list[Path]:
    """Find all supported files under raw/ (excluding hidden files and state file)."""
    files = []
    for fp in sorted(RAW_DIR.rglob("*")):
        if fp.is_file() and fp.suffix.lower() in SUPPORTED_EXTS:
            if fp.name.startswith("."):
                continue
            files.append(fp)
    return files


def main():
    engine = "claude"
    reset = False
    args = sys.argv[1:]
    for a in args:
        if a == "--engine=qwen":
            engine = "qwen"
        elif a == "--reset":
            reset = True

    if reset and STATE_FILE.exists():
        STATE_FILE.unlink()

    state = load_state()
    all_files = scan_files()

    # Discover new/changed files (hash-based)
    pending = []
    for fp in all_files:
        rel = str(fp.relative_to(VAULT_DIR))
        current_hash = file_hash(fp)
        entry = state.get(rel)
        if entry is None:
            pending.append(fp)
        elif entry.get("hash") != current_hash and entry.get("status") != "failed":
            pending.append(fp)

    if not pending:
        print(json.dumps({"status": "up_to_date", "files_checked": len(all_files)}))
        return

    print(json.dumps({"status": "processing", "pending": len(pending), "total": len(all_files)},
                     ensure_ascii=False))

    script_dir = Path(__file__).resolve().parent
    processed = 0
    failed = 0
    for i, fp in enumerate(pending):
        rel = str(fp.relative_to(VAULT_DIR))
        current_hash = file_hash(fp)
        existing = state.get(rel, {})

        # Skip if previously failed (already retried once)
        if existing.get("status") == "failed":
            print(f"  SKIP (previously failed): {rel}")
            continue

        print(f"  [{i + 1}/{len(pending)}] Ingesting: {rel}")

        if engine == "qwen":
            env = os.environ.copy()
            env["PYTHONPATH"] = str(script_dir)
            result = subprocess.run(
                [sys.executable, str(script_dir / "qwen_ingest.py"),
                 "--raw", str(fp)],
                capture_output=True, text=True, cwd=str(VAULT_DIR),
                env=env,
            )

            if result.returncode == 0:
                state[rel] = {"hash": current_hash, "status": "done", "engine": engine}
                processed += 1
            else:
                prev_status = existing.get("status")
                if prev_status == "retry":
                    state[rel] = {"hash": current_hash, "status": "failed", "engine": engine,
                                  "error": result.stderr[:200] if result.stderr else "unknown"}
                    failed += 1
                    print(f"  FAILED (after retry): {rel}")
                else:
                    print(f"  RETRY: {rel}")
                    result2 = subprocess.run(
                        [sys.executable, str(script_dir / "qwen_ingest.py"),
                         "--raw", str(fp)],
                        capture_output=True, text=True, cwd=str(VAULT_DIR),
                        env=env,
                    )
                    if result2.returncode == 0:
                        state[rel] = {"hash": current_hash, "status": "done", "engine": engine}
                        processed += 1
                    else:
                        state[rel] = {"hash": current_hash, "status": "failed", "engine": engine,
                                      "error": result2.stderr[:200] if result2.stderr else "unknown"}
                        failed += 1
                        print(f"  FAILED: {rel}")
        else:
            # Claude engine: user invokes /llm-wiki:ingest manually
            print(f"  NOTE: Use /llm-wiki:ingest {rel} to process this file")
            state[rel] = {"hash": current_hash, "status": "pending", "engine": engine}
            processed += 1

        save_state(state)

    # Clean stale entries (files that no longer exist)
    current_rels = {str(fp.relative_to(VAULT_DIR)) for fp in all_files}
    stale = [r for r in state if r not in current_rels]
    for r in stale:
        del state[r]
    if stale:
        save_state(state)

    # Auto-relink after batch ingest
    print("--- Running relink ---")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(script_dir)
    subprocess.run(
        [sys.executable, str(script_dir / "relink.py")],
        cwd=str(VAULT_DIR),
        env=env,
    )

    print(json.dumps({"status": "complete", "processed": processed, "failed": failed,
                      "stale_cleaned": len(stale)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
