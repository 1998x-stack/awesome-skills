#!/usr/bin/env python3
"""Build wiki/keywords.txt — jieba custom dictionary from wiki page metadata.

Scans all wiki pages, extracts title/aliases/tags from frontmatter,
and writes a jieba user-dict file for improved Chinese tokenization.

Usage:
    python3 scripts/build_keywords.py          # Build keywords.txt
"""

import json
import re
import sys
from pathlib import Path

from wiki_utils import VAULT_DIR, WIKI_DIR, WIKI_SUBDIRS, parse_frontmatter, extract_title

KEYWORDS_PATH = WIKI_DIR / "keywords.txt"

# Frequency weights by source type (higher = stronger segmentation hint)
FREQ_TITLE = 5
FREQ_ALIAS = 3
FREQ_TAG = 2

MIN_LENGTH = 2

# Patterns that should never appear as jieba keywords
_BAD_ALIAS_RE = re.compile(r'^\d{4}-{1,2}\d{0,4}$')  # year ranges like 1707--1783, 1926-


def _is_valid_keyword(s: str) -> bool:
    if len(s) < MIN_LENGTH:
        return False
    if _BAD_ALIAS_RE.match(s):
        return False
    return True


def collect_keywords() -> dict[str, int]:
    """Scan wiki pages and collect keywords with frequency weights.

    Returns dict mapping keyword -> max frequency.
    """
    keywords: dict[str, int] = {}

    for subdir in WIKI_SUBDIRS:
        dirpath = WIKI_DIR / subdir
        if not dirpath.exists():
            continue
        for fp in sorted(dirpath.glob("*.md")):
            text = fp.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)

            # Title — from frontmatter or first heading
            title = ""
            if fm and fm.get("title"):
                title = str(fm["title"]).strip().strip("'\"")
            else:
                title = extract_title(text)
            if title and _is_valid_keyword(title):
                keywords[title] = max(keywords.get(title, 0), FREQ_TITLE)

            if not fm:
                continue

            # Aliases
            aliases = fm.get("aliases", [])
            if isinstance(aliases, list):
                for alias in aliases:
                    alias = str(alias).strip()
                    if _is_valid_keyword(alias):
                        keywords[alias] = max(keywords.get(alias, 0), FREQ_ALIAS)

            # Tags
            tags = fm.get("tags", [])
            if isinstance(tags, list):
                for tag in tags:
                    tag = str(tag).strip()
                    if _is_valid_keyword(tag):
                        keywords[tag] = max(keywords.get(tag, 0), FREQ_TAG)

    return keywords


def build():
    if not WIKI_DIR.exists():
        print(json.dumps({"error": "wiki/ directory not found"}))
        sys.exit(2)

    keywords = collect_keywords()

    # Count by source type for reporting
    titles = sum(1 for f in keywords.values() if f == FREQ_TITLE)
    aliases = sum(1 for f in keywords.values() if f == FREQ_ALIAS)
    tags = sum(1 for f in keywords.values() if f == FREQ_TAG)

    # Write jieba user dict: "word freq word_type"
    lines = []
    for word in sorted(keywords):
        freq = keywords[word]
        lines.append(f"{word} {freq} n")

    KEYWORDS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": "ok",
        "path": str(KEYWORDS_PATH.relative_to(VAULT_DIR)),
        "total_keywords": len(keywords),
        "titles": titles,
        "aliases": aliases,
        "tags": tags,
    }, ensure_ascii=False))


if __name__ == "__main__":
    build()
