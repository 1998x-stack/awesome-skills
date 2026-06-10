# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **curated meta-repository** that aggregates 1600+ agent skills from multiple independent projects and communities, organized into 9 functional categories. There is no unified build, test, or lint system — each sub-directory is its own standalone project.

## Directory Organization

### Functional Categories

| Category | Contents |
|----------|----------|
| **guidelines-mindsets/** | musk-guidelines, sunge-guidelines, history-guidelines, bottom-up-innovation, andrej-karpathy-skills |
| **design-creative/** | claude-design, html-ppt, html-design-manager, gptimage2-prompt-builder, kadike-prompt, manim, remotion-best-practices, short-video-script |
| **game-development/** | game-design, game-design-analyst, godot-engine, prefab-search |
| **ai-tools/** | autonomous-research, dashscope-asr, graphify, manim-math, model-pricing-visualizer, product-self-knowledge, prompt-optimizer, prompt-refiner, search-quality-evaluator, sympy, system-prompt-calibrator |
| **dev-engineering/** | harness-engineering, long-running-agent-harness, lua, mattpocock-skills, notion-client, playwright-automation, ralph-loop, superpowers, taptap-maker-issue-builder, vercel-skills |
| **document-generation/** | anthropic-skills, file-reading, pdf-reading |
| **platform-ecosystems/** | openai-skills, sina7x24 |
| **life-automation/** | benepass-reimbursement, call-to-book, cancel-unsubscribe, event-planning, file-expenses, file-form, financial-calculator, grocery-shopping, hire-help, meal-delivery, prescription-refill, return-refund |
| **domain-expertise/** | civil-lawyer, gaokao-advisor, learn |

### Large Self-Contained Collections

- `ECC/` — Everything Claude Code plugin (865+ skills, agents, hooks, commands). Node.js ≥18, CommonJS. Tests via `node tests/run-all.js`.
- `awesome-copilot/` — Cross-platform agent skills (513+ skills). Has its own `package.json`.
- `gstack/` — GStack ecosystem with agents, browser integration. Uses Bun.
- `get-shit-done/` — GSD structured development workflow toolkit.
- `servers/` — TypeScript MCP server project.
- `spec-kit/` — Spec-kit with `pyproject.toml` (Python).

## Common Skill Formats

**Standalone skills** follow this pattern:
- `SKILL.md` — YAML frontmatter (`name`, `description`) followed by markdown instructions. The `description` field is critical for auto-triggering — it defines when the skill applies.
- Optional: `references/`, `scripts/`, `examples/`, `assets/` subdirectories.

**Collection skills** (inside `skills/` directories within each project) follow each project's own conventions. Many use the same `SKILL.md` or `skills/<name>/SKILL.md` pattern with YAML frontmatter.

## When Editing This Repo

1. **Respect sub-project boundaries.** Collections like `dev-engineering/superpowers/` and `ECC/` have their own CLAUDE.md, conventions, and contribution rules. Read that project's CLAUDE.md before modifying anything inside it.
2. **Categorization:** New standalone skills go into the appropriate category folder. Do not create new categories without discussion.
3. **No duplicates.** Before adding a skill, check if it already exists in another category or collection.
4. **Standalone skills** follow the `SKILL.md` + frontmatter pattern. The description in frontmatter determines auto-triggering behavior.
5. **README.md** maps the directory structure. Update it when adding or moving skills.
6. **No root-level tooling exists.** `git` is the only common tool across all sub-projects.
