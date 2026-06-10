#!/usr/bin/env python3
"""Auto-link unlinked wiki term mentions across all wiki pages.

Algorithm:
1. Build term dictionary from all wiki page titles + aliases
2. Sort terms by length descending (longest-match-first)
3. For each wiki page, find bare mentions of terms in body text
4. Insert [[wikilinks]], skipping protected zones and self-references
5. Output JSON summary

Usage:
  python relink.py [--dry-run]
"""

import json
import re
import sys
from pathlib import Path

from wiki_utils import VAULT_DIR, WIKI_DIR, WIKI_SUBDIRS, parse_frontmatter

MIN_TERM_LEN = 2        # minimum length for CJK/mixed terms
MIN_EN_TERM_LEN = 5     # minimum length for ASCII-only (English) terms


def _is_ascii_term(term: str) -> bool:
    """Return True if every character in term is ASCII (English/abbreviation)."""
    return all(c.isascii() for c in term)


def _term_ok(term: str) -> bool:
    """Return True if term meets the minimum-length requirement."""
    if _is_ascii_term(term):
        return len(term) >= MIN_EN_TERM_LEN
    return len(term) >= MIN_TERM_LEN


def collect_terms() -> dict[str, str]:
    """Build {term: page_name} from all wiki page titles + aliases.

    page_name is the filename stem (used in [[page_name]]).
    Longer terms shadow shorter ones at same position (handled in apply phase).

    English (ASCII-only) terms shorter than MIN_EN_TERM_LEN are excluded to
    avoid false matches like 'rg' → ripgrep, 'fd' → fd, 'uv' → uv, etc.
    """
    terms: dict[str, str] = {}
    for subdir in WIKI_SUBDIRS:
        d = WIKI_DIR / subdir
        if not d.exists():
            continue
        for f in d.iterdir():
            if not f.suffix == ".md":
                continue
            page_name = f.stem
            text = f.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)

            # Title = filename stem
            if _term_ok(page_name):
                terms[page_name] = page_name

            if not fm:
                continue

            # Aliases
            aliases = fm.get("aliases")
            if isinstance(aliases, list):
                for a in aliases:
                    a = str(a).strip()
                    if _term_ok(a) and a not in terms:
                        terms[a] = page_name
            elif isinstance(aliases, str):
                a = aliases.strip()
                if _term_ok(a) and a not in terms:
                    terms[a] = page_name

    return terms


def find_protected_zones(text: str, body_start: int) -> list[tuple[int, int]]:
    """Find character ranges in text that must not be modified.

    Returns sorted list of (start, end) tuples (absolute positions in text).
    Protected zones:
    - Frontmatter (0 to body_start)
    - Existing [[wikilinks]]
    - Code blocks (``` ... ```) and inline code (` ... `)
    - Heading lines (# ...)
    - ## 来源 section through ## 相关 section (or EOF)
    """
    zones: list[tuple[int, int]] = []

    # Frontmatter
    if body_start > 0:
        zones.append((0, body_start))

    body = text[body_start:]

    # Existing wikilinks
    for m in re.finditer(r'\[\[[^\]]+\]\]', body):
        zones.append((body_start + m.start(), body_start + m.end()))

    # Fenced code blocks
    for m in re.finditer(r'```.*?```', body, re.DOTALL):
        zones.append((body_start + m.start(), body_start + m.end()))

    # Inline code
    for m in re.finditer(r'`[^`]+`', body):
        zones.append((body_start + m.start(), body_start + m.end()))

    # Heading lines
    for m in re.finditer(r'^#+\s+.*$', body, re.MULTILINE):
        zones.append((body_start + m.start(), body_start + m.end()))

    # ## 来源 section to end (includes ## 相关)
    source_match = re.search(r'^## 来源', body, re.MULTILINE)
    if source_match:
        zones.append((body_start + source_match.start(), len(text)))

    # Sort and merge overlapping zones
    zones.sort()
    merged: list[tuple[int, int]] = []
    for s, e in zones:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    return merged


def is_protected(pos: int, length: int, zones: list[tuple[int, int]]) -> bool:
    """Check if range [pos, pos+length) overlaps any protected zone."""
    end = pos + length
    for zs, ze in zones:
        if pos < ze and end > zs:
            return True
        if zs >= end:
            break
    return False


def relink_page(
    text: str,
    sorted_terms: list[tuple[str, str]],
    self_page: str,
    self_aliases: set[str],
) -> tuple[str, int]:
    """Add [[wikilinks]] to unlinked term mentions in a single page.

    Returns (new_text, links_added).
    """
    # Find body start (after frontmatter)
    body_start = 0
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            body_start = end + 3

    zones = find_protected_zones(text, body_start)
    consumed: list[tuple[int, int]] = []  # positions already linked
    replacements: list[tuple[int, int, str]] = []  # (start, end, replacement)

    for term, page_name in sorted_terms:
        # Skip self-references
        if page_name == self_page:
            continue

        # Find all occurrences of term in text (case-sensitive)
        start = body_start
        while start < len(text):
            idx = text.find(term, start)
            if idx == -1:
                break
            term_end = idx + len(term)

            # Check: not inside a protected zone
            if is_protected(idx, len(term), zones):
                start = term_end
                continue

            # Check: not overlapping an already-consumed position
            overlap = False
            for cs, ce in consumed:
                if idx < ce and term_end > cs:
                    overlap = True
                    break
            if overlap:
                start = term_end
                continue

            # Build link text
            if term == page_name:
                link = f"[[{term}]]"
            else:
                link = f"[[{page_name}|{term}]]"

            replacements.append((idx, term_end, link))
            consumed.append((idx, term_end))
            start = term_end

    if not replacements:
        return text, 0

    # Apply replacements in reverse order (so indices don't shift)
    replacements.sort(key=lambda r: r[0], reverse=True)
    result = text
    for start, end, link in replacements:
        result = result[:start] + link + result[end:]

    return result, len(replacements)


def get_body_start(text: str) -> int:
    """Find where body starts (after frontmatter)."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return end + 3
    return 0


def main():
    dry_run = "--dry-run" in sys.argv

    # 1. Collect all terms
    terms = collect_terms()

    # 2. Sort by term length descending (longest-match-first)
    sorted_terms = sorted(terms.items(), key=lambda kv: len(kv[0]), reverse=True)

    # 3. Process each wiki page
    pages_scanned = 0
    pages_modified = 0
    total_links_added = 0
    details: list[dict] = []

    for subdir in WIKI_SUBDIRS:
        d = WIKI_DIR / subdir
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if not f.suffix == ".md":
                continue
            pages_scanned += 1
            page_name = f.stem
            text = f.read_text(encoding="utf-8")

            # Collect self-terms (title + aliases) to skip
            fm, _ = parse_frontmatter(text)
            self_aliases = {page_name}
            if fm:
                aliases = fm.get("aliases")
                if isinstance(aliases, list):
                    for a in aliases:
                        self_aliases.add(str(a).strip())
                elif isinstance(aliases, str) and aliases.strip():
                    self_aliases.add(aliases.strip())

            new_text, count = relink_page(text, sorted_terms, page_name, self_aliases)

            if count > 0:
                if not dry_run:
                    f.write_text(new_text, encoding="utf-8")
                pages_modified += 1
                total_links_added += count
                details.append({"page": f"{subdir}/{page_name}", "links_added": count})

    result = {
        "status": "ok",
        "dry_run": dry_run,
        "terms_count": len(terms),
        "pages_scanned": pages_scanned,
        "pages_modified": pages_modified,
        "links_added": total_links_added,
    }
    if details:
        result["details"] = details

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
