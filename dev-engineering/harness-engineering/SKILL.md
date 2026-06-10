---
name: harness-engineering
description: >
  Apply Harness Engineering principles to design agent-first software environments
  where AI agents (Codex, Claude Code, etc.) do the actual coding. Use this skill
  whenever someone asks about: setting up a codebase for AI agents, agent-first
  architecture, making a repo legible for AI coding agents, architectural constraints
  for agent-generated code, preventing "AI slop" or codebase entropy, Codex agent
  scaffolding, context engineering for agents, agent feedback loops, structuring
  docs for AI agents, garbage collection in AI-generated codebases, or wants to
  scale AI coding throughput. Also trigger when someone mentions building a
  harness, rails, or guardrails for AI coding agents, or asks how OpenAI's
  Harness team shipped 1M lines with 3 engineers.
---

# Harness Engineering Skill

Harness Engineering is the discipline of **designing environments, constraints, and
feedback loops** that enable AI agents to write production-quality software
autonomously — with humans acting as environment architects rather than primary coders.

The OpenAI Harness team shipped ~1,000,000 lines of code, 1,500+ PRs, in 5 months
with 3 engineers and zero hand-written code. The methodology is replicable.

---

## The Three Pillars

Before diving in, identify which pillar(s) the user needs help with:

1. **Context Engineering** — making the repo navigable and legible for agents
2. **Architectural Constraints** — mechanical guardrails that scale to any code volume
3. **Entropy & Garbage Collection** — automated systems that fight codebase decay

Read the relevant reference file(s) for deep guidance:
- `references/context-engineering.md` → docs structure, progressive disclosure, dynamic context
- `references/architectural-constraints.md` → dependency layers, boundary parsing, linters
- `references/gc-patterns.md` → golden principles, GC agents, quality grading

---

## Core Mental Models

### The Map, Not the Manual

Agents have finite context windows. A monolithic `AGENTS.md` with all rules fails because:
- It crowds out task context, code, and relevant docs
- It becomes stale fast — agents can't tell what's still valid
- Agents pattern-match locally rather than navigate with intent

**Instead**: Give agents a navigable knowledge structure where they can find exactly
what they need for the current task and nothing more.

### Enforce Invariants, Not Implementations

The most powerful constraints are **mechanically verifiable and globally enforced** —
not style guides or suggestions. The difference:

| Enforce (CI-gated, automatic) | Don't Enforce (let agents decide) |
|-------------------------------|----------------------------------|
| Dependency direction          | Which library to use             |
| Boundary data parsing exists  | Internal implementation style    |
| Cross-reference validity      | Function naming conventions      |
| No circular dependencies      | File organization within a module|

Why this works: a linter rule applied once protects a million lines simultaneously.
Human review can only protect what it sees.

### Agent Struggles = Missing Capability (Not a Signal to Hand-Code)

When an agent can't complete a task, the productive response is never "I'll just
write it myself." That breaks the harness model. Instead:

```
Agent fails or produces poor output
        ↓
Diagnose: What's missing?
  → Tool/access? (can it read logs, run tests?)
  → Documentation? (does the domain have a README?)
  → Abstraction? (is there a reusable pattern missing?)
  → Constraint? (does a linter rule need to be added?)
  → Task clarity? (is the execution plan too vague?)
        ↓
Have the agent build that missing capability first
        ↓
Retry the task — now with better infrastructure
```

Every diagnosed gap, fixed once, benefits every subsequent agent task.

---

## Quick Setup Path

Two scenarios: **greenfield** (new codebase) and **retrofit** (existing codebase).

### Greenfield

**Step 1: Initialize the docs structure**
```bash
mkdir -p docs/{architecture/decisions,domains,execution-plans}
touch docs/_map.md docs/golden-principles.md docs/_quality-report.md
touch docs/architecture/{overview,layers}.md
```
See `references/context-engineering.md` for what goes in each file.

**Step 2: Define your dependency layers** (before writing any code)
See `references/architectural-constraints.md` for the layer model.

**Step 3: Install structural testing and boundary parsing enforcement**
```bash
# Node/TypeScript
npm install --save-dev dependency-cruiser
# Python
pip install import-linter
```

**Step 4: Grant agents observability access** (logs, CI output, test results)
Agents without feedback behave like developers who never run their code.

**Step 5: Set up the Garbage Collection agent**
Schedule a recurring Codex task against `golden-principles.md`.
See `references/gc-patterns.md`.

**Step 6: Start at Autonomy Level 1** — agent codes, you review every PR.

---

### Retrofit (Existing Codebase)

Retrofitting a mature codebase requires an incremental path — don't try to
establish all constraints at once on existing code.

**Week 1 — Document what exists:**
- Write `docs/_map.md` reflecting current structure (even if messy)
- Write `docs/architecture/layers.md` describing *intended* layers
  (not current state — where you want to get to)
- Write `docs/golden-principles.md` with 5-10 key quality standards

**Week 2 — Enforce going-forward only:**
- Install structural testing, configure it to only check *new files* initially
  (dependency-cruiser `--include-only` flag)
- Add boundary parsing requirement to PR template — not yet a hard CI gate
- Start running agents at Level 1 on a non-critical domain

**Week 3–4 — Tighten and expand:**
- Enable hard CI gate for dependency direction (existing violations are
  "known debt," new violations are blocked)
- Expand to 2–3 more domains
- Add first GC agent run against golden-principles

**Month 2+ — Full adoption:**
- Expand structural tests to entire codebase
- GC agent running weekly, cleaning legacy violations
- Move to Autonomy Level 2 for domains with clean constraint coverage

---

## Autonomy Levels

| Level | Who Codes | Who Reviews | Move Up When... |
|-------|-----------|-------------|-----------------|
| 1 | Agent | All PRs | Structural tests catch violations reliably |
| 2 | Agent | Architecture PRs only | <5% of agent PRs need rework |
| 3 | Agent + CI loop | High-risk changes only | Agent self-review catches issues pre-human |
| 4 | Agent handles lifecycle | Human sets goals | GC agents maintain quality automatically |

**Agent self-review** (required before moving to Level 3): Configure agents to review
their own PRs against `golden-principles.md` before requesting human review. They should
flag any violations they find and either fix them or explain why they're intentional.
This filters out low-quality PRs before they reach human reviewers.

---

## Diagnosing Common Problems

**"Agent keeps producing inconsistent code"**
→ Missing constraint. Identify the pattern and encode it as a linter rule or structural test.

**"Agent gets lost in the codebase on large tasks"**
→ Context Engineering problem. Check `docs/_map.md` is current; break task into smaller execution plans.

**"Codebase quality is degrading over time"**
→ No entropy management. Implement GC agents. See `references/gc-patterns.md`.

**"Agent can't self-validate its changes"**
→ Missing observability access. Grant agent read access to logs/traces/test output.

**"PRs are low quality / need heavy rework"**
→ Either execution plans are too vague, or agent lacks domain documentation.
  Create/update `docs/domains/<domain>/README.md` and an execution plan template.

**"Human review is the bottleneck (too many PRs)"**
→ Triage by risk, not by volume:

| PR Type | Review Strategy |
|---------|-----------------|
| DB migrations | Require explicit async human approval |
| New domain additions | Require architecture review |
| Cross-domain changes | Require human review |
| Feature code in constrained domains | Agent self-review sufficient |
| Test additions | CI-only (must pass, no human needed) |
| Doc updates | Automated link-check CI gate |

Move routine-category PRs to agent self-review. Human attention is a finite resource —
spend it where structural tests and CI can't substitute.
