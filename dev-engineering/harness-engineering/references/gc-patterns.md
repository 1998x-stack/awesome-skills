# Entropy & Garbage Collection for Agent-First Codebases

Read this when the user's codebase is accumulating "AI slop," quality is drifting,
docs are going stale, or they need automated cleanup systems.

---

## Why Entropy Is Inevitable (and That's OK)

High-throughput agent coding produces entropy as a side effect:
- Redundant implementations of the same pattern
- Orphaned services and dead code
- Documentation that references things that moved or were deleted
- Gradual drift from architectural standards ("golden principles")

This isn't a failure of agents — it's a property of any high-volume system.
The solution isn't to slow down; it's to build automated counter-pressure.

---

## The Golden Principles Document

`docs/golden-principles.md` is the authoritative quality standard GC agents use
as their evaluation benchmark. Write it before setting up GC agents.

```markdown
# Golden Principles

These are the non-negotiable quality standards for this codebase.
They are used by automated garbage collection agents to identify and fix drift.

## Code Quality
- Functions have a single responsibility (prefer < 30 lines)
- No dead code paths — remove rather than comment out
- No TODO comments older than 2 weeks — convert to issues or delete
- All public APIs have JSDoc/docstrings

## Architecture
- Dependency layers strictly respected (see docs/architecture/layers.md)
- All data at domain boundaries is parsed via schema (see architecture/layers.md)
- No inline configuration — all config goes through the config layer
- No circular dependencies anywhere in the codebase

## Documentation
- docs/_map.md is always current (every new file added to docs/ appears here)
- ADRs exist for any non-obvious design decision
- Domain READMEs describe current behavior (not intended behavior)
- All markdown cross-references resolve to real files

## Testing
- All boundary-parsing functions have unit tests
- All happy paths for external integrations have integration tests
- Error paths tested for anything that makes a network call
- No test stubs left in production code

## Observability
- All service entry points emit a structured log line
- Errors include correlation IDs
- Slow operations (>500ms) emit timing metrics
```

---

## GC Agent Patterns

### Pattern 1: Scheduled Audit + PR Agent

The core loop: a recurring Codex task reads golden-principles.md, scans the codebase,
and opens targeted PRs for each violation found.

```yaml
# .codex/tasks/gc-audit.yaml

name: garbage-collection-audit
schedule: "0 2 * * *"  # 2am daily
description: |
  Scan the codebase against docs/golden-principles.md.

  For EACH violation found:
  1. Classify severity: critical (blocks functionality), major (degrades quality), minor (style)
  2. Open a focused PR that fixes ONLY that violation
  3. PR title format: "gc: [severity] fix <what was fixed>"
  4. Add a brief PR description explaining which golden principle was violated

  After scanning, update docs/_quality-report.md with:
  - Timestamp of this audit
  - Count of violations by severity per domain
  - Quality grade per domain (A/B/C based on violation density)

  Be conservative: if you're not sure something is a violation, skip it.
  It's better to miss a violation than to make an incorrect "fix."
```

### Pattern 2: Doc Consistency Agent

```yaml
name: doc-consistency-check
schedule: "0 3 * * 1"  # Monday 3am weekly
description: |
  1. Verify every cross-reference in docs/ resolves to a real file
  2. Check docs/_map.md lists every file in docs/ (no orphaned docs)
  3. For each domain in docs/domains/, verify its README.md matches
     the actual module's exports and behavior
  4. Update stale docs in-place, open a PR with all changes batched
```

### Pattern 3: Dead Code Agent

```yaml
name: dead-code-cleanup
schedule: "0 4 * * 0"  # Sunday 4am weekly
description: |
  Find and remove:
  - Exported functions never imported anywhere
  - Services with no callers
  - Config keys never read
  - Test utilities used in no test files

  For each dead item found: open a small PR to delete it.
  Include evidence in the PR description (e.g., "searched all imports, zero results").
  Never delete anything that's been modified in the past 30 days — it may be in progress.
```

---

## Quality Report Template

Maintain `docs/_quality-report.md` — auto-updated by GC agents, human-readable:

```markdown
# Quality Report

_Auto-updated by GC audit agent. Last run: 2026-02-27 02:03 UTC_

## Summary
| Domain       | Grade | Critical | Major | Minor | Trend |
|-------------|-------|----------|-------|-------|-------|
| payments    | A     | 0        | 0     | 1     | ↔     |
| users       | B+    | 0        | 1     | 3     | ↑     |
| orders      | A-    | 0        | 0     | 2     | ↑     |
| notifications| B    | 0        | 2     | 4     | ↓     |

## Grading Scale
- **A**: 0 critical, 0 major, ≤2 minor violations
- **B**: 0 critical, ≤2 major, ≤5 minor violations  
- **C**: 0 critical, >2 major OR >5 minor violations
- **D**: Any critical violations

## Open GC PRs
- [gc: minor - remove dead notifications helper](link)
- [gc: major - add boundary parsing to orders/external](link)
```

---

## When to Manually Intervene

GC agents handle routine drift. These situations warrant human judgment:

- Violations that span multiple domains (systemic architectural issue)
- GC agent producing incorrect "fixes" repeatedly (golden principles need refinement)
- Grade trending down despite GC activity (underlying pattern needs addressing)
- A new category of violation appearing frequently (golden principles need a new rule)

When a new category of violation appears regularly, update `golden-principles.md`
to explicitly name it. The next GC run will catch all existing instances.

---

## Tuning GC Agents

Start conservative — GC agents should open small, focused PRs rather than large
sweeping changes. Signs your GC agent needs tuning:

- PRs are too large to review easily → add "fix one violation per PR" instruction
- PRs are being rejected frequently → golden-principles.md is too strict or ambiguous
- GC misses obvious violations → add explicit examples to golden-principles.md
- GC agents are running too often → reduce schedule frequency, start weekly not daily
