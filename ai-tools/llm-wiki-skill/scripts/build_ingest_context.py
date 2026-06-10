#!/usr/bin/env python3
"""Build compact context package for ingest subagents.

Scans wiki state and schema files, outputs a single JSON object
that gives an ingest subagent everything it needs without reading
multiple files.

Usage:
    python3 scripts/build_ingest_context.py
    python3 scripts/build_ingest_context.py --topic AI工程
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from wiki_utils import VAULT_DIR, WIKI_DIR, WIKI_SUBDIRS, SKILL_DIR, parse_frontmatter

def read_layered(filename: str, user_dir: Path, skill_dir: Path) -> Optional[str]:
    """Read file with user override priority: user_dir > skill_dir."""
    user_path = user_dir / filename
    if user_path.exists():
        return user_path.read_text(encoding="utf-8")
    skill_path = skill_dir / "schemas" / filename
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")
    return None


def build_compact_schema() -> str:
    """Merge entity-types, relationship-types, quality-rules -- layered override."""
    user_schema = VAULT_DIR / "_schema"
    skill_schema = SKILL_DIR / "schemas"

    parts = []
    for filename, label in [
        ("entity-types.md", "Entity Types"),
        ("relationship-types.md", "Relationship Types"),
        ("quality-rules.md", "Quality Rules"),
    ]:
        text = read_layered(filename, user_schema, skill_schema)
        if text:
            _, body = parse_frontmatter(text)
            parts.append(f"### {label}\n" + body.strip())

    return "\n\n".join(parts)


def build_template() -> str:
    """Read wiki-page template -- layered override."""
    user_tpl = VAULT_DIR / "templates" / "wiki-page.md"
    if user_tpl.exists():
        return user_tpl.read_text(encoding="utf-8")
    skill_tpl = SKILL_DIR / "templates" / "wiki-page.md"
    if skill_tpl.exists():
        return skill_tpl.read_text(encoding="utf-8")
    return ""


def load_topic_pages(topics: list[str]) -> set[str]:
    """Load page names for given topics from topic-to-wiki.json."""
    topic_map_path = VAULT_DIR / ".claude" / "topic-to-wiki.json"
    if topic_map_path.exists():
        data = json.loads(topic_map_path.read_text(encoding="utf-8"))
        result = set()
        for topic in topics:
            result.update(data.get("topics", {}).get(topic, []))
        return result
    return set()


def build(topic_filter: list[str] | None = None):
    if not WIKI_DIR.exists():
        print(json.dumps({"error": "wiki/ directory not found"}))
        sys.exit(2)

    pages = scan_existing_pages()
    schema = build_compact_schema()
    template = build_template()

    # Apply topic filter
    if topic_filter:
        allowed = load_topic_pages(topic_filter)
        pages = [p for p in pages if p["name"] in allowed]

    # Stats
    entities = sum(1 for p in pages if p["type"] == "entity")
    concepts = sum(1 for p in pages if p["type"] == "concept")

    # Build page list string (compact: one line per page, no aliases to save tokens)
    page_lines = []
    for p in pages:
        page_lines.append(f"- {p['name']} [{p['type']}]")
    existing_pages_text = "\n".join(page_lines)

    output = {
        "status": "ok",
        "stats": {
            "total_pages": len(pages),
            "entities": entities,
            "concepts": concepts,
        },
        "existing_pages": existing_pages_text,
        "schema_compact": schema,
        "template": template,
    }

    if topic_filter:
        output["topic_filter"] = topic_filter

    print(json.dumps(output, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Build ingest context package")
    parser.add_argument("--topic", type=str, help="Filter to topic(s), comma-separated (e.g. 'AI工程,Agent系统')")
    args = parser.parse_args()

    topic_filter = args.topic.split(",") if args.topic else None
    build(topic_filter=topic_filter)


if __name__ == "__main__":
    main()
