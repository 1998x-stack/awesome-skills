#!/usr/bin/env python3
"""Knowledge graph JSON builder for the Obsidian wiki vault.

Scans wiki/ for markdown pages, extracts nodes from frontmatter and
edges from both frontmatter relates_to and body [[wikilinks]], then
outputs a deduplicated graph with connected-component analysis.

Usage:
    python3 scripts/build_graph.py [--output vault/graph.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

from wiki_utils import WIKI_DIR, WIKILINK_RE, parse_frontmatter, strip_wikilink

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def label_to_id(label: str, label_to_path: dict) -> str | None:
    """Resolve a display label to its relative path id."""
    return label_to_path.get(label)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_graph(wiki_dir: Path):
    md_files = sorted(wiki_dir.rglob("*.md"))

    # --- Pass 1: build nodes, map label -> path ---
    nodes = {}          # id (rel path) -> node dict
    label_to_path = {}  # display label -> rel path

    for fp in md_files:
        rel = fp.relative_to(wiki_dir.parent).as_posix()  # e.g. "wiki/concepts/牛顿法.md"
        label = fp.stem  # display name without .md

        text = fp.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)

        node = {
            "id": rel,
            "label": label,
            "type": fm.get("type", "unknown") if fm else "unknown",
            "confidence": fm.get("confidence", None) if fm else None,
            "tags": fm.get("tags", []) if fm else [],
            "edge_count": 0,
        }
        nodes[rel] = node
        label_to_path[label] = rel

    # --- Pass 2: extract edges ---
    # Directed relations preserve source→target order.
    # Undirected relations (wikilink, related_to) dedup via sorted key.
    DIRECTED_RELATIONS = {"contradicts", "supersedes", "extends", "implements", "caused", "depends_on"}
    edge_set = {}  # key -> edge dict

    def add_edge(src_id: str, tgt_id: str, relation: str, bidirectional: bool = False):
        if relation in DIRECTED_RELATIONS:
            key = (src_id, tgt_id, relation)
        else:
            key = (tuple(sorted([src_id, tgt_id])), relation)
        if key not in edge_set:
            edge_set[key] = {
                "source": src_id,
                "target": tgt_id,
                "relation": relation,
                "bidirectional": bidirectional,
            }

    for fp in md_files:
        rel = fp.relative_to(wiki_dir.parent).as_posix()
        text = fp.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)

        # Frontmatter relates_to
        if fm:
            for entry in fm.get("relates_to", []) or []:
                if not isinstance(entry, dict):
                    continue
                target_label = strip_wikilink(entry.get("target", ""))
                relation = entry.get("type", "related_to")
                tgt_id = label_to_id(target_label, label_to_path)
                if tgt_id and tgt_id != rel:
                    add_edge(rel, tgt_id, relation)

        # Body wikilinks
        for m in WIKILINK_RE.finditer(body):
            target_label = m.group(1).strip()
            tgt_id = label_to_id(target_label, label_to_path)
            if tgt_id and tgt_id != rel:
                add_edge(rel, tgt_id, "wikilink")

    edges = list(edge_set.values())

    # --- Update edge counts ---
    for e in edges:
        if e["source"] in nodes:
            nodes[e["source"]]["edge_count"] += 1
        if e["target"] in nodes:
            nodes[e["target"]]["edge_count"] += 1

    # --- Connected components (BFS) ---
    adj = defaultdict(set)
    for e in edges:
        adj[e["source"]].add(e["target"])
        adj[e["target"]].add(e["source"])

    visited = set()
    components = []

    for nid in nodes:
        if nid in visited:
            continue
        # BFS
        queue = deque([nid])
        comp_nodes = []
        while queue:
            cur = queue.popleft()
            if cur in visited:
                continue
            visited.add(cur)
            comp_nodes.append(cur)
            for nb in adj[cur]:
                if nb not in visited:
                    queue.append(nb)
        components.append(comp_nodes)

    orphans = [c[0] for c in components if len(c) == 1 and nodes[c[0]]["edge_count"] == 0]

    comp_list = []
    for i, comp_nodes in enumerate(sorted(components, key=len, reverse=True)):
        comp_list.append({
            "id": i,
            "size": len(comp_nodes),
            "nodes": sorted(comp_nodes),
        })

    node_list = sorted(nodes.values(), key=lambda n: n["id"])

    graph = {
        "metadata": {
            "generated": datetime.now(timezone.utc).isoformat(),
            "total_nodes": len(node_list),
            "total_edges": len(edges),
            "orphan_count": len(orphans),
            "component_count": len(components),
        },
        "nodes": node_list,
        "edges": edges,
        "orphans": orphans,
        "components": comp_list,
    }

    return graph


def main():
    parser = argparse.ArgumentParser(description="Build knowledge graph JSON from wiki vault")
    parser.add_argument(
        "--output",
        default=str(WIKI_DIR.parent / "graph.json"),
        help="Output path for graph.json (default: vault/graph.json)",
    )
    args = parser.parse_args()

    if not WIKI_DIR.is_dir():
        print(f"ERROR: wiki directory not found at {WIKI_DIR}", file=sys.stderr)
        sys.exit(1)

    graph = build_graph(WIKI_DIR)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "status": "ok",
        "nodes": graph["metadata"]["total_nodes"],
        "edges": graph["metadata"]["total_edges"],
        "orphans": graph["metadata"]["orphan_count"],
        "components": graph["metadata"]["component_count"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))



if __name__ == "__main__":
    main()
