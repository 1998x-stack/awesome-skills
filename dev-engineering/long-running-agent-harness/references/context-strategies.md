# Context Strategies: Compaction vs. Externalization

## The Context Engineering Problem

As sessions grow longer, models experience **context degradation**:
- Earlier constraints get buried under newer tool outputs
- Reasoning about priorities becomes muddled
- The agent "forgets" rules it acknowledged 50 tool calls ago

Longer context windows don't fully solve this — more tokens means
more competition for model attention, not less degradation.

---

## Strategy Comparison

| Strategy | Mechanism | Strengths | Weaknesses |
|----------|-----------|-----------|------------|
| **Auto-compaction** | Threshold-triggered LLM summary | Seamless, no user action | Recursive summary degradation, info loss |
| **Manual /compact** | User-triggered summary | User controls timing | Requires user discipline, often forgotten |
| **Handoff** (Amp-style) | New thread with curated context | Clean break, selective | Requires user decision-making |
| **File externalization** | State in persistent files | Lossless, auditable | Requires agent write discipline |
| **Hybrid** (Anthropic) | Compaction + external files | Redundancy, resilience | More moving parts |

---

## Anthropic's Approach: Externalization First

The key insight: **don't fight context limits, route around them**.

Instead of trying to perfectly preserve conversation history across context resets,
ensure that all critical state exists in external files that survive any context reset.

```
Context Window (volatile)           External Files (persistent)
┌─────────────────────────┐         ┌──────────────────────────┐
│ - Current task details  │         │ features.json            │
│ - Tool call history     │    ←──  │ claude-progress.txt      │
│ - Reasoning chain       │ Agent   │ git history              │
│ - Previous responses    │ reads   │ init.sh                  │
└─────────────────────────┘         └──────────────────────────┘
        ↑ Volatile, compressible              ↑ Persistent, lossless
```

**Result**: When the context resets (compaction or new session), the agent
reads files and reconstructs full situational awareness. Nothing is truly lost.

---

## Compaction: When and How

Compaction is still useful within a session (between explicit session boundaries).

### Threshold-Based Compaction

Trigger compaction when tokens reach ~80–85% of context limit:

```python
def should_compact(token_usage, context_limit, threshold=0.85):
    return token_usage / context_limit > threshold
```

### Good Compaction Prompt

```
You are performing a CONTEXT CHECKPOINT COMPACTION.
Create a handoff summary for another LLM that will resume this task.

Include:
- Current feature being worked on (from features.json)
- What has been implemented so far in this session
- Current state: does the code compile? Do tests pass?
- Files modified in this session (with brief description of changes)
- Next immediate step (specific, actionable)
- Any constraints or gotchas discovered

Be concise and structured. The next LLM will resume exactly where you left off.
```

### Compaction + External File Redundancy

After compacting, instruct the agent to:
1. Write a brief summary to `claude-progress.txt` before the compaction occurs
2. Make a git commit if the code is in a clean state
3. Then compact

This creates a "double safety net" — the compact summary AND the files.

---

## Recursive Summary Degradation

A real problem observed in production (Codex team at OpenAI):

```
Compact 1: Full session → Summary A (accurate, detailed)
Compact 2: Summary A + more work → Summary B (some detail lost)
Compact 3: Summary B + more work → Summary C (significant distortion)
Compact 4: Summary C + more work → Summary D (early context garbled)
```

Mitigation strategies:
1. **Prefer session boundaries over in-session compaction** when possible
2. **Write to external files before each compaction** to preserve ground truth
3. **Limit compaction depth**: start a new session rather than compact 3+ times
4. **Include key constraints explicitly** in each compaction prompt so they survive

---

## Stable vs. Variable Context

Optimize context by separating content that changes vs. stays constant:

```
Stable Prefix (load once, rarely changes)     Variable Suffix (changes every turn)
┌─────────────────────────────────────────┐   ┌───────────────────────────────┐
│ System prompt                           │   │ Recent tool calls             │
│ features.json (mostly stable)           │ + │ Last few agent messages       │
│ init.sh content                         │   │ Current task context          │
│ Core constraints                        │   │ Test results from this turn   │
└─────────────────────────────────────────┘   └───────────────────────────────┘
        ↑ Benefits from prefix caching               ↑ Updated each turn
```

This architecture allows inference engines to reuse cached computations for
the stable prefix, reducing both latency and cost on long sessions.

---

## Practical Decision Tree

```
Is this task completable in one context window? (~100k tokens)
  ├── YES → No harness needed, just a good prompt
  └── NO → Need multi-session harness
        │
        Does the task have clear subtasks?
        ├── YES → Use features.json pattern
        └── NO → Break down task first, then use features.json
              │
              Is there a meaningful state to track?
              ├── YES → Add claude-progress.txt
              └── NO → Maybe features.json is enough
                    │
                    Does the task modify files/code?
                    ├── YES → Add git-based recovery
                    └── NO → Use flat file state only
```
