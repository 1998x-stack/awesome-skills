# Coding Agent — Session Protocol

## The Mandatory Startup Ritual

Every coding agent session MUST begin with this exact sequence.
No exceptions. No shortcuts.

```
┌─────────────────────────────────────────────────────────────┐
│  MANDATORY STARTUP (before any implementation work)         │
│                                                             │
│  1. pwd                    → confirm working directory      │
│  2. git log --oneline -10  → understand recent history      │
│  3. cat claude-progress.txt→ read session handoff notes     │
│  4. query features.json    → find highest-priority pending  │
│  5. bash init.sh           → start environment              │
│  6. SMOKE TEST             → verify core user flow works    │
│  7. SELECT ONE FEATURE     → confirm which feature to build │
└─────────────────────────────────────────────────────────────┘
```

### Why the Smoke Test is Non-Negotiable

Without a smoke test, the coding agent may spend an entire session building on
a broken foundation. Common scenario:
- Session N left a half-implemented auth flow with a syntax error
- Session N+1 starts, reads progress, begins work on chat features
- 45 minutes later: realizes the app hasn't worked since session N
- Has to revert and fix, wasting the entire session

**The smoke test catches this in <2 minutes at session start.**

---

## Coding Agent Prompt Template

```markdown
You are continuing development on [PROJECT_NAME].

MANDATORY STARTUP SEQUENCE — Do these steps in order before any implementation:

1. Run: pwd
2. Run: git log --oneline -10
3. Run: cat claude-progress.txt
4. Run: python3 -c "
import json
with open('features.json') as f:
    data = json.load(f)
pending = [x for x in data['features'] if not x['passes']]
pending.sort(key=lambda x: x['priority'])
print(f'PENDING: {len(pending)} features remaining')
for f in pending[:5]:
    print(f\"  [{f['priority']}] {f['id']}: {f['description']}\")
"
5. Run: bash init.sh
6. SMOKE TEST: Open a browser to http://localhost:3000 and verify the core
   user flow works end-to-end. For a chat app: start a chat, send a message,
   verify response. If it's broken, fix it before doing anything else.

IMPLEMENTATION RULES:
- Work on EXACTLY ONE feature from features.json (highest priority pending)
- State which feature you're working on before starting
- Test each feature with browser automation after implementing it
- It is UNACCEPTABLE to remove or modify existing passing tests
- If a bug persists after 2 fix attempts: git revert and note in progress.txt

SESSION COMPLETION REQUIREMENTS:
Before this session can end, you must:
□ Completed one feature with passing E2E test
□ Updated features.json: set passes: true for completed feature
□ git commit with descriptive message (include feature ID)
□ Updated claude-progress.txt with session summary
□ Verified codebase is in mergeable state (no syntax errors, tests pass)
□ Checked: are there more features.json with passes: false? If yes, continue.
□ Only stop when context window is getting full OR all features pass
```

---

## The Clean State Protocol

### What "Clean State" Means

At the end of every session (or before context runs out):

| Requirement | How to Verify |
|------------|---------------|
| Code compiles | Run build command, check for errors |
| No broken tests | Run test suite, all should pass |
| Changes committed | `git status` shows clean tree |
| Progress documented | claude-progress.txt has session entry |
| Features updated | features.json reflects current passes status |

### Git Workflow for Coding Agents

```bash
# After implementing and testing a feature:
git add -A
git commit -m "feat(auth-001): implement user registration with email/password

- Added /api/auth/register endpoint
- Created RegisterForm component
- Added input validation and error messages
- E2E test passes: user can register and reach dashboard"

# If something goes badly wrong:
git revert HEAD  # undo last commit
# or
git stash        # save broken work, return to clean state
```

---

## Progress File Update Format

After each session, append to `claude-progress.txt`:

```
### Session [N] — [DATE] [TIME]
Feature worked on: [feature-id] — [description]
Status: [COMPLETED | PARTIAL | REVERTED]

Changes made:
- [bullet: what was changed]
- [bullet: what was changed]

Test result: [PASS | FAIL | N/A]

Next session should:
- Start with feature: [feature-id]
- [Any special notes: known issues, environment quirks, etc.]

Features completed this session: [N]
Total features remaining: [N]
```

---

## Handling Edge Cases

### Context Window Running Out Mid-Feature

If the model detects it's running low on context while implementing a feature:

1. **Don't leave half-implemented code** — either complete it or revert
2. If reverting: `git stash` or `git checkout -- .`
3. Update progress.txt: "Session ended early — [feature-id] not completed, code reverted"
4. Commit the clean state: `git commit -m "checkpoint: clean state before context limit"`

### Bug That Can't Be Fixed

```
Attempt 1 fails → Try different approach
Attempt 2 fails → git revert to last clean commit
Note in progress.txt: "BLOCKED: [feature-id] — [description of issue]"
Mark feature priority: -1 (skip for now)
Move to next feature
```

### Conflicting Requirements

If features.json requirements seem to conflict:
1. Note the conflict in progress.txt
2. Make the simplest implementation that satisfies both
3. Add a comment in code explaining the tradeoff
4. Don't modify features.json requirements — those are the source of truth

---

## Autonomy Levels

| Level | Human Reviews | Move Up When |
|-------|--------------|--------------|
| 1 | Every commit | Smoke tests catch issues reliably |
| 2 | Completed features only | <5% of features need rework |
| 3 | End of session summaries | Agent self-review catches issues |
| 4 | Only when agent flags blockers | E2E test suite is comprehensive |
