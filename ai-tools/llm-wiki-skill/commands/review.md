# /llm-wiki:review -- Periodic review, crystallization, and memory consolidation

Review knowledge base health and patterns, crystallize insights, manage page decay.

## Usage

```
/llm-wiki:review              # Weekly review (default)
/llm-wiki:review monthly      # Monthly review
/llm-wiki:review quarterly    # Quarterly review
```

## Steps

### 0. System Health Check
- Read `log.md` for last `maintain` timestamp -> if > 7 days, remind user
- Compare current wiki page count vs last snapshot -> if > 20 pages difference, suggest maintain

### 1. Gather Materials
- Scan past 7/30/90 days of journal entries (daily notes, reflections, judgments)

### 2. Pattern Discovery
- Identify concepts mentioned 3+ days
- Discover new cross-domain connections
- Flag topics with growing mention frequency

### 3. Crystallization
- If session connected 3+ concepts forming a new insight -> create `wiki/syntheses/` page
- Update `index.md` and `log.md`

### 4. Journal -> Wiki Link Scan
- Scan recent journal entries for [[wiki page links]]
- If a page is referenced 3+ days AND confidence < 0.5 -> suggest promoting confidence or adding content

### 5. !insight Processing
- Scan journal entries for `!insight` markers
- For each unprocessed !insight: create or update a wiki page
- Content is extracted from the marked paragraph

### 6. Memory Decay (Ebbinghaus)
- Scan all wiki pages with `status: active`
- Apply decay formula: `new_confidence = confidence * 0.5^(days/half_life)`
  - slow (180d half-life): architecture decisions, core concepts
  - medium (60d half-life): general facts
  - fast (14d half-life): temporary observations
- Pages with confidence < 0.3 -> mark `status: stale`
- stale pages with 30+ days no update -> mark `status: archived`

### 7. Adaptive Automation
- Analyze operation frequency from log.md
- If same operation at similar time for 3+ consecutive days -> propose cron task
- If X days since last maintain -> remind user
- User confirms -> write cron config to `.claude/settings.local.json`

## Output Format

```
Review Complete (YYYY-MM-DD)

Health:
  Last maintain: N days ago -- OK / Reminder
  Pages: N (+N since last snapshot)

Patterns:
  - [[Topic]] mentioned 5 times this week

Crystallized:
  - Created wiki/syntheses/New Insight.md

!insight Processed:
  - Created wiki/concepts/Condition Number vs Stability.md

Decay Applied:
  - N pages decayed, M marked stale, K archived

Automation Proposed:
  - Daily journal at 22:57? Confirm to set cron.
```
