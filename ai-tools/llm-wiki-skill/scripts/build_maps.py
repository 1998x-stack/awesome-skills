#!/usr/bin/env python3
"""Generate per-topic map files from topic-to-wiki.json.

Each map contains a topic overview + page list with confidence scores.
Replaces both the old LLM-driven maps generation and the guidelines system.

Usage:
    python3 scripts/build_maps.py              # generate all maps
    python3 scripts/build_maps.py --topic AI   # generate one topic
    python3 scripts/build_maps.py --json       # output stats as JSON
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from wiki_utils import VAULT_DIR, WIKI_DIR, WIKI_SUBDIRS, MAPS_DIR, parse_frontmatter

TOPIC_MAP_PATH = VAULT_DIR / ".claude" / "topic-to-wiki.json"


def load_topic_mapping() -> dict[str, list[str]]:
    """Load topic -> [page_names] from topic-to-wiki.json."""
    if TOPIC_MAP_PATH.exists():
        data = json.loads(TOPIC_MAP_PATH.read_text(encoding="utf-8"))
        return data.get("topics", {})
    return {}


def read_page_info(name: str) -> dict | None:
    """Read frontmatter + overview for a wiki page by stem name."""
    for subdir in WIKI_SUBDIRS:
        fp = WIKI_DIR / subdir / f"{name}.md"
        if fp.exists():
            text = fp.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            if fm is None:
                continue
            overview = ""
            m = re.search(r"## 概述\s*\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
            if m:
                overview = m.group(1).strip().split("\n")[0][:80]
            elif body.strip():
                for line in body.split("\n"):
                    if line.startswith("# "):
                        continue
                    if line.strip():
                        overview = line.strip()[:80]
                        break
            return {
                "name": name,
                "type": fm.get("type", "unknown"),
                "confidence": fm.get("confidence"),
                "overview": overview,
            }
    return None


def generate_map(topic: str, page_names: list[str]) -> str:
    """Generate map markdown for one topic."""
    today = datetime.now().strftime("%Y-%m-%d")

    pages = []
    for name in sorted(page_names):
        info = read_page_info(name)
        if info:
            pages.append(info)

    concepts = [p for p in pages if p["type"] == "concept"]
    entities = [p for p in pages if p["type"] == "entity"]
    syntheses = [p for p in pages if p["type"] == "synthesis"]
    qa_insights = [p for p in pages if p["type"] == "qa-insight"]

    total = len(pages)

    # Overview from top concept names
    top_names = [p["name"] for p in concepts[:4]]
    overview_hint = "、".join(top_names) if top_names else topic

    lines = [
        "---",
        "type: map",
        f'topic: "{topic}"',
        f"page_count: {total}",
        f"updated: {today}",
        "---",
        "",
        f"# {topic}",
        "",
        "## 概述",
        "",
        f"{topic} 相关概念与实体的集群。核心主题：{overview_hint}。",
        "",
    ]

    def add_section(title: str, items: list[dict]):
        if not items:
            return
        lines.append(f"## {title}")
        lines.append("")
        for p in items:
            conf = f" (confidence: {p['confidence']})" if p["confidence"] else ""
            ov = f" — {p['overview']}" if p["overview"] else ""
            lines.append(f"- [[{p['name']}]]{ov}{conf}")
        lines.append("")

    add_section("概念", concepts)
    add_section("实体", entities)
    add_section("综合分析", syntheses)
    add_section("QA 洞见", qa_insights)

    return "\n".join(lines)


def build(topics_filter: list[str] | None = None, as_json: bool = False):
    """Generate map files."""
    topic_map = load_topic_mapping()
    # Count total wiki pages -- skip topic clustering if too few
    wiki_page_count = sum(1 for _ in WIKI_DIR.rglob("*.md"))
    if wiki_page_count < 20:
        msg = f"Insufficient pages for topic clustering ({wiki_page_count} < 20). Skipping."
        if as_json:
            print(json.dumps({"status": "skipped", "reason": "insufficient_pages",
                              "page_count": wiki_page_count, "threshold": 20}, ensure_ascii=False))
        else:
            print(f"SKIPPED: {msg}")
        return
    if not topic_map:
        msg = "No topic mapping found (need .claude/topic-to-wiki.json)"
        if as_json:
            print(json.dumps({"status": "error", "message": msg}))
        else:
            print(f"ERROR: {msg}")
        return

    if topics_filter:
        topic_map = {k: v for k, v in topic_map.items() if k in topics_filter}

    MAPS_DIR.mkdir(parents=True, exist_ok=True)

    # If no filter, clean out old maps first
    if not topics_filter:
        for old in MAPS_DIR.glob("*.md"):
            old.unlink()

    generated = {}
    for topic, page_names in sorted(topic_map.items()):
        content = generate_map(topic, page_names)
        out_path = MAPS_DIR / f"{topic}.md"
        out_path.write_text(content, encoding="utf-8")
        generated[topic] = len(page_names)

    if as_json:
        print(json.dumps({
            "status": "ok",
            "maps_dir": str(MAPS_DIR),
            "topics": generated,
            "total_topics": len(generated),
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Generated {len(generated)} maps in {MAPS_DIR}/")
        for topic, count in sorted(generated.items()):
            print(f"  {topic}: {count} pages")


def main():
    parser = argparse.ArgumentParser(description="Generate per-topic map files")
    parser.add_argument("--topic", type=str, help="Generate only for specific topic(s), comma-separated")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    topics_filter = args.topic.split(",") if args.topic else None
    build(topics_filter=topics_filter, as_json=args.json)


if __name__ == "__main__":
    main()
