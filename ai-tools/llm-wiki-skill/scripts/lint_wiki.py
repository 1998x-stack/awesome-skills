#!/usr/bin/env python3
"""Wiki lint checker — validates frontmatter, links, and index consistency."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from wiki_utils import VAULT_DIR, WIKI_DIR, MAPS_DIR, INDEX_FILE, parse_frontmatter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOCMAP_FILE = VAULT_DIR / "index" / "BM25" / "docmap.json"

REQUIRED_FIELDS = {"type", "status", "confidence", "created", "tags", "relates_to"}

SEVERITY_ERROR = "error"
SEVERITY_WARN = "warning"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collect_wiki_files(single: Optional[str] = None) -> List[Path]:
    """Return list of wiki .md files to check."""
    if single:
        p = Path(single)
        if not p.is_absolute():
            p = VAULT_DIR / p
        return [p] if p.exists() else []
    return sorted(WIKI_DIR.rglob("*.md"))


def load_index_links() -> Set[str]:
    """Return set of page names listed in index.md.

    Supports two formats:
    - Wikilink: [[Name]] or [[Name|Alias]] (used in older verbose format)
    - Plain text: comma-separated names in the ## 全部页面 section (slim format)
    """
    if not INDEX_FILE.exists():
        return set()
    text = INDEX_FILE.read_text(encoding="utf-8")
    # Wikilink format
    names = set(re.findall(r"\[\[([^\]|]+?)(?:\|[^\]]*?)?\]\]", text))
    # Plain text format: extract the ## 全部页面 section and parse comma-separated names
    m = re.search(r"## 全部页面\s*\n+(.+?)(?:\n##|\Z)", text, re.DOTALL)
    if m:
        raw = m.group(1).strip()
        for name in raw.split(","):
            name = name.strip()
            if name:
                names.add(name)
    return names


def load_docmap() -> Optional[dict]:
    """Load BM25 docmap.json, return None if absent."""
    if not DOCMAP_FILE.exists():
        return None
    try:
        return json.loads(DOCMAP_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_file(path: Path, index_links: Set[str], all_pages: Set[str],
               docmap: Optional[dict], do_fix: bool,
               cached_text: Optional[str] = None) -> List[dict]:
    """Run all per-file checks. Return list of finding dicts."""
    findings: List[dict] = []
    text = cached_text if cached_text is not None else path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    page_name = path.stem
    rel = str(path.relative_to(VAULT_DIR))

    # F2: invalid YAML frontmatter
    if meta is None:
        findings.append(dict(
            file=rel, check="F2", severity=SEVERITY_ERROR,
            message="Invalid or missing YAML frontmatter", fixed=False))
        # Can't do further frontmatter checks
        meta = {}

    # F1: missing required fields
    if meta:
        missing = REQUIRED_FIELDS - set(meta.keys())
        if missing:
            findings.append(dict(
                file=rel, check="F1", severity=SEVERITY_ERROR,
                message="Missing frontmatter fields: %s" % ", ".join(sorted(missing)),
                fixed=False))

    # F3: overview > 200 chars
    overview_match = re.search(r"## 概述\s*\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
    if overview_match:
        overview_text = overview_match.group(1).strip()
        if len(overview_text) > 200:
            findings.append(dict(
                file=rel, check="F3", severity=SEVERITY_WARN,
                message="Overview section is %d chars (limit 200)" % len(overview_text),
                fixed=False))

    # F4: empty sections (skip h1 page title, skip parent sections with sub-headings)
    sections = [(m.group(), m.start()) for m in re.finditer(r"^(#{2,3} .+)", body, re.MULTILINE)]
    for i, (hdr, hdr_pos) in enumerate(sections):
        start = hdr_pos + len(hdr)
        end = sections[i + 1][1] if i + 1 < len(sections) else len(body)
        content = body[start:end].strip()
        if not content:
            # Skip parent h2 sections that have h3 children
            if hdr.startswith("## ") and i + 1 < len(sections) and sections[i + 1][0].startswith("### "):
                continue
            findings.append(dict(
                file=rel, check="F4", severity=SEVERITY_WARN,
                message="Empty section: %s" % hdr.strip(), fixed=False))

    # B1: broken [[links]]
    links = re.findall(r"\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]", body)
    for link in links:
        # Skip raw/ links — they point outside wiki
        if link.startswith("raw/"):
            continue
        if link not in all_pages:
            findings.append(dict(
                file=rel, check="B1", severity=SEVERITY_WARN,
                message="Broken link: [[%s]]" % link, fixed=False))

    # B2: page missing from BM25 docmap
    if docmap is not None:
        docmap_paths = set()
        if isinstance(docmap, dict):
            for v in docmap.values():
                if isinstance(v, dict) and "path" in v:
                    docmap_paths.add(v["path"])
                elif isinstance(v, str):
                    docmap_paths.add(v)
        if rel not in docmap_paths:
            findings.append(dict(
                file=rel, check="B2", severity=SEVERITY_WARN,
                message="Page not in BM25 docmap", fixed=False))

    # I1: page not in index.md
    if page_name not in index_links:
        findings.append(dict(
            file=rel, check="I1", severity=SEVERITY_WARN,
            message="Page not listed in index.md", fixed=False))

    return findings


def check_orphans(all_pages: Set[str], wiki_files: List[Path],
                   file_texts: Optional[Dict[str, str]] = None) -> List[dict]:
    """O1: pages with no inbound links from other wiki pages.

    If file_texts is provided, reuses already-read content to avoid re-reading files.
    """
    findings: List[dict] = []
    # Build inbound link map
    inbound: Dict[str, int] = {name: 0 for name in all_pages}
    for p in wiki_files:
        body = file_texts.get(str(p)) if file_texts else None
        if body is None:
            body = p.read_text(encoding="utf-8")
        links = re.findall(r"\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]", body)
        for link in links:
            if link in inbound:
                inbound[link] += 1

    for name, count in sorted(inbound.items()):
        if count == 0:
            matches = [f for f in wiki_files if f.stem == name]
            rel = str(matches[0].relative_to(VAULT_DIR)) if matches else name
            findings.append(dict(
                file=rel, check="O1", severity=SEVERITY_WARN,
                message="Orphan page — no inbound wiki links", fixed=False))

    return findings


def check_stale_index(index_links: Set[str], all_pages: Set[str]) -> List[dict]:
    """I2: entries in index.md that have no corresponding wiki file.

    Skips maps/ references — those are valid links to maps/*.md, not wiki pages.
    """
    findings: List[dict] = []
    for name in sorted(index_links - all_pages):
        if name.startswith("maps/"):
            continue  # maps/ links in the stats table are intentional
        findings.append(dict(
            file="index.md", check="I2", severity=SEVERITY_WARN,
            message="Stale index entry: [[%s]]" % name, fixed=False))
    return findings


def check_maps_consistency(all_pages: Set[str]) -> List[dict]:
    """M1/M2: check maps/*.md files reference valid wiki pages and cover all pages."""
    findings: List[dict] = []
    if not MAPS_DIR.exists():
        return findings

    mapped_pages: Set[str] = set()
    for mp in sorted(MAPS_DIR.glob("*.md")):
        text = mp.read_text(encoding="utf-8")
        links = set(re.findall(r"\[\[([^\]|]+?)(?:\|[^\]]*?)?\]\]", text))
        rel = str(mp.relative_to(VAULT_DIR))
        for link in links:
            if link not in all_pages:
                findings.append(dict(
                    file=rel, check="M1", severity=SEVERITY_WARN,
                    message="Map references non-existent page: [[%s]]" % link, fixed=False))
            mapped_pages.add(link)

    # M2: pages not in any map
    unmapped = all_pages - mapped_pages
    if unmapped:
        findings.append(dict(
            file="maps/", check="M2", severity=SEVERITY_WARN,
            message="%d pages not in any map: %s" % (len(unmapped), ", ".join(sorted(unmapped)[:10])),
            fixed=False))

    return findings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Lint wiki pages")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues (future)")
    parser.add_argument("--file", type=str, default=None, help="Lint single file")
    parser.add_argument("--json", action="store_true", dest="json_out",
                        help="Output JSON")
    args = parser.parse_args()

    wiki_files = collect_wiki_files(args.file)
    all_pages = {p.stem for p in sorted(WIKI_DIR.rglob("*.md"))}
    index_links = load_index_links()
    docmap = load_docmap()

    findings: List[dict] = []

    # Cache file contents to avoid double reads in orphan check
    file_texts: Dict[str, str] = {}
    for wf in wiki_files:
        file_texts[str(wf)] = wf.read_text(encoding="utf-8")

    for wf in wiki_files:
        findings.extend(check_file(wf, index_links, all_pages, docmap, args.fix,
                                   cached_text=file_texts.get(str(wf))))

    # Global checks only when scanning all files
    if args.file is None:
        all_wiki_files = list(WIKI_DIR.rglob("*.md"))
        # Read any files not yet cached (shouldn't happen in full scan)
        for wf in all_wiki_files:
            if str(wf) not in file_texts:
                file_texts[str(wf)] = wf.read_text(encoding="utf-8")
        findings.extend(check_orphans(all_pages, all_wiki_files, file_texts))
        findings.extend(check_stale_index(index_links, all_pages))
        findings.extend(check_maps_consistency(all_pages))

    errors = [f for f in findings if f["severity"] == SEVERITY_ERROR]
    warnings = [f for f in findings if f["severity"] == SEVERITY_WARN]

    if args.json_out:
        report = {
            "total_files": len(wiki_files),
            "errors": len(errors),
            "warnings": len(warnings),
            "checks": findings,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        if not findings:
            print("OK — %d files, no issues." % len(wiki_files))
        else:
            for f in findings:
                sev = "ERR " if f["severity"] == SEVERITY_ERROR else "WARN"
                print("[%s] %s %s: %s" % (sev, f["check"], f["file"], f["message"]))
            print("\n%d files scanned. %d error(s), %d warning(s)." % (
                len(wiki_files), len(errors), len(warnings)))

    if errors:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
