---
name: llm-wiki
description: Personal knowledge management system — ingest source materials into structured wiki pages, query with unified search (BM25 + graph + maps), maintain knowledge quality, journal, and review insights. Use this skill whenever the user mentions knowledge bases, personal wikis, second brain, PKM, note-taking systems, ingesting documents, organizing knowledge, or wants to extract insights from their reading. Trigger even if the user just says "I want to organize my notes" or "help me build a knowledge base" without knowing the technical terms.
---

# LLM Wiki

You are a knowledge base maintainer. Your role is to compile source materials into structured wiki pages, maintain connections and consistency between knowledge, manage page lifecycles, discover patterns, flag contradictions, and fill gaps.

## First-Time Setup

If the user mentions wanting a knowledge base but doesn't have one yet, guide them through `/llm-wiki:init`. Read `commands/init.md` (relative to this SKILL.md's directory) for the full initialization workflow.

## Quick Workflow Reference

```
New knowledge:    /llm-wiki:ingest <file>        → wiki pages
Batch ingest:     /llm-wiki:ingest-loop           → all of raw/
Search:           /llm-wiki:query <question>      → answer + sources
Journal:          /llm-wiki:journal daily         → personal notes
Periodic review:  /llm-wiki:review                → crystallize + decay
Health check:     /llm-wiki:maintain              → repair + rebuild
```

For any command, read the corresponding file in `commands/` relative to this SKILL.md's directory for detailed step-by-step instructions.

## Architecture

```
<wiki-root>/
├── .wiki-root      # Marker file (empty)
├── raw/            # Immutable source materials (read-only)
│   └── qa/         # Chat exports for Q&A import
├── wiki/           # LLM-generated knowledge pages
│   ├── entities/   # People, companies, projects, tools
│   ├── concepts/   # Theories, methods, algorithms
│   └── syntheses/  # Cross-topic analyses, QA insights
├── journal/        # User-owned diary/reflections/judgments
├── maps/           # Auto-generated topic maps
├── _schema/        # User schema overrides (optional)
├── templates/      # User template overrides (optional)
├── index.md        # Auto-maintained directory
└── log.md          # Operation log
```

## Core Principles

1. **raw/ is read-only** -- never modify source files
2. **wiki/ is LLM-owned** -- all wiki pages created and maintained by you
3. **journal/ is user-owned** -- personal thoughts written by user, you assist with linking and analysis
4. **Links over folders** -- use [[wikilinks]] to organize relationships
5. **Bottom-up** -- structure emerges naturally, no preset taxonomy
6. **Log everything** -- all operations append to log.md

## Path Discovery

Scripts find the user's wiki root via:
1. `LLM_WIKI_ROOT` environment variable
2. Walking up from CWD to find `.wiki-root` marker
3. Error if not found -- prompt user to run `/llm-wiki:init`

## Frontmatter Specification

All wiki/ pages must have:

```yaml
---
type: entity | concept | synthesis
status: draft | active | stale | archived
confidence: 0.0-1.0
decay_rate: slow | medium | fast
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_accessed: YYYY-MM-DD
source_count: N
tags: []
aliases: []
relates_to:
  - target: "[[PageName]]"
    type: uses | depends_on | contradicts | caused | extends | implements | supersedes | part_of | compares_to
    confidence: 0.0-1.0
---
```

## Wiki Page Lifecycle

```
draft --(confidence >= 0.5)-- active
active --(confidence < 0.3)-- stale
stale --(30 days no update)-- archived
```

Ebbinghaus decay rates:
- slow (180d half-life): architecture decisions, core concepts
- medium (60d half-life, default): general facts
- fast (14d half-life): temporary observations

## Schema / Template Override

Commands read from two layers (user overrides take priority):
1. `<wiki-root>/_schema/xxx.md`, `<wiki-root>/templates/xxx.md`
2. `<skill>/schemas/xxx.md`, `<skill>/templates/xxx.md` (defaults)

## Commands

When the user invokes `/llm-wiki:<command>`, Read the corresponding command file (relative to this SKILL.md's directory) and follow its steps exactly:

| Command | File to Read |
|---------|-------------|
| `/llm-wiki:init` | `commands/init.md` |
| `/llm-wiki:ingest` | `commands/ingest.md` |
| `/llm-wiki:ingest-loop` | `commands/ingest-loop.md` |
| `/llm-wiki:query` | `commands/query.md` |
| `/llm-wiki:journal` | `commands/journal.md` |
| `/llm-wiki:review` | `commands/review.md` |
| `/llm-wiki:maintain` | `commands/maintain.md` |

Each command file contains the full step-by-step workflow, including which Python scripts to invoke and the exact bash commands to run. In command files, `<skill>` refers to the directory containing this SKILL.md — substitute it with the actual path before executing commands.

## Scripts

All Python scripts are invoked through the wiki.sh wrapper:

```bash
bash <skill>/scripts/wiki.sh <script_name> [args...]
```

Available: bm25_index, search_wiki, build_graph, build_maps, build_keywords, build_ingest_context, lint_wiki, snapshot_index, relink, qwen_ingest, ingest_loop

## Hooks

PostToolUse hooks fire on every Write/Edit to `wiki/**/*.md`:
- BM25 index update (immediate)
- Graph rebuild (30s debounce)

## Dependencies

Install: `pip install -r <skill>/scripts/requirements.txt`
Required: jieba, rank_bm25, pyyaml, markitdown
Optional (Qwen engine): openai (requires DASHSCOPE_API_KEY)
