---
name: long-running-agent-harness
description: >
  Design and implement effective harnesses for long-running AI agents that must
  work across multiple context windows. Use this skill whenever someone asks about:
  building agents that span multiple sessions, preventing agents from losing progress
  across context windows, session handoff design, progress tracking for AI agents,
  multi-session agent architecture, initializer/coding-agent patterns, agent memory
  externalization, context compaction strategies, claude-progress.txt patterns,
  features.json task lists, preventing agents from prematurely declaring completion,
  incremental agent workflows, E2E testing for agents, or any scenario where an AI
  agent needs to maintain state and make consistent progress over hours or days.
  Also trigger for: "agent keeps forgetting", "agent loses context", "agent one-shots
  the entire task", "how do I keep agents on track", "agent session management".
---

# Long-Running Agent Harness Skill

Based on Anthropic's engineering research: agents working on complex, multi-hour tasks
face two core failure modes — **one-shotting** (trying to do everything at once) and
**premature completion** (declaring done after partial progress). This skill provides
patterns to solve both.

---

## Core Mental Model: The Shift-Worker Problem

Long-running agents are like engineers working in shifts where **each new engineer
arrives with zero memory of previous shifts**. The harness must externalize all
state so any fresh session can immediately orient and make progress.

```
Session 1 → [context exhausted] → Session 2 → [context exhausted] → Session 3
Without harness: each session starts blind, wastes time reconstructing state
With harness:    each session reads files, orients in <2min, continues work
```

---

## The Dual-Agent Architecture

Two roles with **different initial prompts** (same underlying model + tools):

### Role 1: Initializer Agent (first session only)

Creates the foundational artifacts. Read `references/initializer.md` for full details.

Key outputs:
- `init.sh` — reproducible environment startup + smoke test script
- `features.json` — 100–200+ specific, testable requirements (use JSON, not Markdown)
- `claude-progress.txt` — session-to-session handoff log
- Initial git commit establishing clean baseline

### Role 2: Coding Agent (every subsequent session)

Makes incremental progress. Read `references/coding-agent.md` for full details.

**Fixed startup ritual** (non-negotiable, every session):
1. `run pwd` → confirm working directory
2. `read git log` → understand recent commits
3. `read claude-progress.txt` → understand current state
4. `read features.json` → identify highest-priority incomplete feature
5. `run init.sh` → start environment
6. **Smoke test** → verify basic functionality works before touching anything
7. Pick ONE feature → work on it, test it, commit it

---

## The Four Externalization Files

| File | Purpose | Format |
|------|---------|--------|
| `init.sh` | Reproducible environment bootstrap | Shell script |
| `features.json` | Structured task backlog with pass/fail | JSON (not Markdown!) |
| `claude-progress.txt` | Cross-session memory log | Plain text |
| Git history | Reversible code states + audit trail | VCS |

**Key principle**: Never rely on context window for cross-session state.
Everything important lives in files that outlast any session.

---

## Critical Prompt Constraints

When building prompts for coding agents, use **explicit, strong-toned constraints**:

```
✓ "Work on only ONE feature at a time from features.json"
✓ "It is UNACCEPTABLE to remove or modify existing passing tests"
✓ "Every session must end with a git commit in a mergeable state"
✓ "If you cannot fix a bug in 2 attempts, use git revert and move on"
✓ "Do not declare the project complete unless all features.json passes: true"
```

Strong language is intentional — models naturally optimize for apparent progress
over verified, incremental progress. Constraints redirect this tendency.

---

## Testing: E2E Over Code Review

The failure pattern: agent writes code, reviews it, thinks it's correct, marks done.
The fix: require browser/UI automation testing (Puppeteer MCP or equivalent).

```
Implement feature → Browser automation test → Screenshots/DOM validation
                                    ↓
                         Pass → update features.json, commit
                         Fail → debug, retry, or revert
```

Read `references/testing-patterns.md` for test tooling recommendations.

---

## Diagnosing Common Failures

**"Agent one-shots the whole project and runs out of context"**
→ features.json with explicit one-feature-at-a-time constraint is missing

**"Agent marks features done but they're broken"**
→ No E2E testing tools; agent is self-evaluating from code review only

**"New session spends 30+ minutes figuring out state"**
→ progress.txt is missing, outdated, or too vague; add structured session summary

**"Agent prematurely declares project complete"**
→ features.json incomplete or agent has no instruction to check it before finishing

**"Bad code from last session breaks the next session"**
→ Smoke test at session start not implemented; add mandatory E2E check before new work

**"Compaction is causing agent to forget key constraints"**
→ Critical constraints must live in persistent files (progress.txt, features.json),
  not just in conversation history that gets compressed away

---

## Quick Start Template

For a new long-running agent project:

```markdown
# Initializer Agent Prompt

You are setting up a software project that will be built incrementally across
multiple AI agent sessions. Your job is ONLY to set up the environment — do NOT
start implementing features.

Create these files:
1. init.sh — starts dev server, runs smoke test, prints "READY" on success
2. features.json — expand the user's request into 50–200 specific features,
   each with: id, category, description, test_steps[], passes: false, priority: int
3. claude-progress.txt — create with header "# Project: [name]\n## Session Log\n"
4. Make an initial git commit: "Initial project setup by initializer agent"

User's request: {{USER_REQUEST}}
```

```markdown
# Coding Agent Prompt

You are continuing work on a software project. Previous agents have made progress.

MANDATORY STARTUP SEQUENCE (do this before anything else):
1. run pwd
2. git log --oneline -10
3. cat claude-progress.txt
4. cat features.json | python3 -c "import json,sys; f=json.load(sys.stdin)['features']; [print(x['id'], x['description']) for x in f if not x['passes']]"
5. bash init.sh
6. Test the core user flow end-to-end (open browser, use the app, verify it works)

RULES:
- Work on exactly ONE feature at a time (highest priority with passes: false)
- Test every feature using browser automation after implementing it
- It is UNACCEPTABLE to remove or modify existing passing tests
- End every session with: git commit, updated claude-progress.txt, clean codebase
- If stuck on a bug after 2 attempts, git revert and note it in progress.txt
- Do not finish until you check features.json — if any passes: false, keep working
```

---

## Reference Files

- `references/initializer.md` — Full initializer agent guide + feature list design
- `references/coding-agent.md` — Coding agent startup ritual + session protocol  
- `references/testing-patterns.md` — E2E testing tools, Puppeteer MCP setup
- `references/context-strategies.md` — Compaction vs. externalization tradeoffs
