# Context Engineering for Agent-First Codebases

Read this when the user needs help structuring documentation, making a repo legible
for agents, or debugging context-related agent failures.

---

## The Docs Structure

The goal is **progressive disclosure**: agents find exactly what they need for the
current task without wading through irrelevant material.

```
docs/
├── _map.md                    ← REQUIRED: single entry point for agents
├── architecture/
│   ├── overview.md            ← high-level system design (keep under 200 lines)
│   ├── layers.md              ← dependency layer rules (CRITICAL — see constraints ref)
│   └── decisions/             ← Architecture Decision Records
│       └── YYYY-MM-title.md
├── domains/
│   └── <domain-name>/
│       ├── README.md          ← domain entry: what it does, its boundaries, key types
│       └── design.md          ← design specs, data models, edge cases
├── execution-plans/
│   └── <task-type>.md         ← step-by-step agent workflows for common task types
└── golden-principles.md       ← quality standards used by GC agents
```

### The `_map.md` File (Most Important)

This is the file agents read first. It must be maintained as the authoritative
navigation index. Think of it as a directory listing with one-line descriptions.

```markdown
# Codebase Map

## Architecture
- [overview](architecture/overview.md) — System design, major components, data flow
- [layers](architecture/layers.md) — Dependency rules all code must follow
- [decisions/](architecture/decisions/) — Why we made key architectural choices

## Domains
- [payments](domains/payments/README.md) — Stripe integration, billing, invoicing
- [users](domains/users/README.md) — Auth, profiles, permissions
- [notifications](domains/notifications/README.md) — Email, push, in-app alerts

## Common Task Execution Plans
- [add-feature](execution-plans/add-feature.md) — Standard flow for new features
- [add-integration](execution-plans/add-integration.md) — External API integrations
- [fix-bug](execution-plans/fix-bug.md) — Diagnosis → fix → test → verify cycle

## Key Principles
- [golden-principles](golden-principles.md) — Quality standards and non-negotiables
```

Linters should enforce that every cross-reference in `_map.md` points to a real file.
A dead link in `_map.md` means agents navigate to nothing.

---

## Execution Plans

Execution plans are the most overlooked and highest-leverage context artifact.
They pre-specify *how* to approach a class of task, so agents don't invent approaches.

```markdown
# Execution Plan: Add a New Feature

## Phase 1: Design (before writing any code)
1. Read the relevant domain README to understand current boundaries
2. Write a brief design note: what changes, what new types/schemas are needed
3. Identify which layers will be affected (consult layers.md)
4. Add an ADR if this changes existing patterns

## Phase 2: Implementation
1. Start from the bottom layer (Types) and work upward
2. Add boundary schemas first, then implement logic
3. Write unit tests for boundary functions as you go
4. Update domain README if behavior changes

## Phase 3: Verification
1. Run CI locally: linting, structural tests, unit tests
2. If the feature has a UI component: navigate in browser, verify visually
3. Check logs/traces to confirm the happy path produces expected signals

## Phase 4: Documentation
1. Update docs/_map.md if new files were added
2. Update CHANGELOG or release notes if user-facing
```

---

## Dynamic Context: What Agents Need to Self-Validate

Static documentation isn't enough — agents need to observe the results of their own
actions. Grant agents read access to:

- **Test output**: agents iterate until tests pass, not just until they think they're done
- **Logs and traces**: agents can verify their fix produced the expected log line
- **Browser access**: for UI tasks, agents navigate and visually confirm changes
- **CI pipeline results**: agents read failure details and adjust without asking

Why this matters: an agent that can't see feedback behaves like a developer who
writes code, commits it, and never runs it. Observable outcomes close the loop.

---

## Linting Cross-References

Because docs rot fast in high-throughput agent environments, validate mechanically:

```javascript
// Custom lint rule or CI script: validate all markdown cross-references
// Run on every PR that touches docs/

const fs = require('fs');
const path = require('path');
const glob = require('glob');

const docsDir = path.join(__dirname, 'docs');
const mdFiles = glob.sync(`${docsDir}/**/*.md`);

mdFiles.forEach(file => {
  const content = fs.readFileSync(file, 'utf8');
  const links = [...content.matchAll(/\[.*?\]\((.*?\.md.*?)\)/g)];
  links.forEach(([_, href]) => {
    const target = path.resolve(path.dirname(file), href.split('#')[0]);
    if (!fs.existsSync(target)) {
      console.error(`DEAD LINK in ${file}: ${href}`);
      process.exit(1);
    }
  });
});
```

---

## Signs Your Context Engineering Needs Work

- Agents frequently ask clarifying questions that are answered in docs
- Agent-generated code ignores established domain patterns
- Different agent runs produce structurally different (inconsistent) implementations
- Agents reinvent utilities or abstractions that already exist in the codebase
- `_map.md` hasn't been updated in more than a week despite new PRs
