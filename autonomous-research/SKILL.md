---
name: autonomous-research
description: "Autonomous deep research on any topic. Use this skill whenever the user asks to research, investigate, analyze, deep-dive into, survey, or explore ANY topic — whether academic, technical, market, scientific, competitive, historical, or conceptual. Also trigger when the user says 'look into', 'find out about', 'what's the state of', 'compare X vs Y', or asks broad questions that require synthesizing information from multiple sources. Even if the user doesn't say 'research' explicitly, if the task requires gathering, evaluating, and synthesizing information from multiple angles, this skill applies. Do NOT trigger for simple factual questions that can be answered in one sentence."
---

# Autonomous Research

An autonomous research agent inspired by [autoresearch](https://github.com/karpathy/autoresearch). Where autoresearch lets AI autonomously experiment with neural network training, this skill lets AI autonomously research any topic — gathering sources, evaluating evidence, cross-referencing findings, and producing a structured research artifact.

The core philosophy from autoresearch applies: **define constraints and objectives clearly, then let the agent run autonomously**. The human scopes the research; the agent executes it end-to-end without stopping to ask.

---

## Phase 1: Think (Topic Analysis)

When the user provides a research topic, analyze it before doing anything else. Identify:

- **Core question**: What is the user actually trying to understand?
- **Domain**: Academic? Technical? Market? Scientific? Policy? Competitive?
- **Dimensions**: What are the 3-5 key axes this topic can be explored along?
- **Ambiguity**: What's unclear that would change the research direction?

Then generate **3-5 multiple-choice scoping questions** to narrow the research. These questions serve the same purpose as the `program.md` setup phase — they establish the "sandbox" before the autonomous loop begins.

### Scoping Question Design

Each question should resolve a genuine ambiguity. Avoid questions with obvious answers. Good questions change what you search for; bad questions just confirm what you'd do anyway.

Use `AskUserQuestion` with 2-4 options per question. Structure questions across these categories:

1. **Depth**: How deep should the research go?
   - Survey/overview (breadth over depth)
   - Working knowledge (enough to make decisions)
   - Expert-level (comprehensive with primary sources)
   - State-of-the-art (cutting edge, including preprints/recent work)

2. **Focus**: Which angle matters most? (topic-specific options)

3. **Output**: What format serves the user best?
   - Executive briefing (2-3 pages, key takeaways)
   - Research report (5-10 pages, structured analysis)
   - Technical deep-dive (detailed with code/data/methodology)
   - Comparison matrix (structured comparison of alternatives)

4. **Recency**: How important is freshness?
   - Historical context matters (include foundational work)
   - Recent developments only (last 1-2 years)
   - Cutting edge (last 6 months, preprints, announcements)

5. **Actionability**: What will the user do with this?
   - Learning/understanding
   - Making a decision
   - Building something
   - Writing/presenting

Not all questions are needed every time. Pick the 3-5 most relevant ones based on the topic. See `examples/example-scoping-questions.md` for examples.

---

## Phase 2: Plan (Research Design)

After the user answers scoping questions, generate a research plan. Save it to `research-plan.md` in the current directory.

The plan has this structure:

```markdown
# Research Plan: [Topic]

## Scope
- Depth: [from QA]
- Focus: [from QA]
- Output format: [from QA]
- In-scope: [what we'll cover]
- Out-of-scope: [what we won't cover]

## Research Questions
1. [Primary question]
2. [Supporting question]
3. [Supporting question]
...

## Sections
### Section 1: [Title]
- Questions to answer: ...
- Likely sources: ...
- Search queries to try: ...

### Section 2: [Title]
...

## Source Strategy
- Web search queries: [list of planned searches]
- Documentation to check: [if technical]
- Key terms and synonyms: [to improve search coverage]
```

Before executing, briefly show the user the plan outline (section titles and key questions). This is the last checkpoint — after this, execution is autonomous.

---

## Phase 3: Execute (Autonomous Research Loop)

This is where the autoresearch philosophy kicks in: **once execution begins, proceed through ALL sections without stopping to ask**. The user may be away. Run the full loop.

### The Research Loop

```
FOR each section in the plan:
    1. Search: Run 2-4 web searches per section (use WebSearch, exa tools)
    2. Evaluate: For each source, assess relevance and credibility
    3. Extract: Pull key findings, data points, quotes
    4. Cross-reference: Check if findings align or conflict across sources
    5. Log: Record what was searched, found, kept, and discarded
```

### Search Strategy

Use multiple search approaches for coverage:

- **WebSearch** or **mcp__plugin_everything-claude-code_exa__web_search_exa**: For broad web search. Use natural language queries, not keyword soup. Describe the ideal page.
- **mcp__plugin_everything-claude-code_exa__get_code_context_exa**: For technical/code-related research questions.
- **mcp__plugin_everything-claude-code_exa__crawling_exa**: To read full content from promising URLs found in search results.
- **mcp__plugin_everything-claude-code_context7__resolve-library-id** and **query-docs**: For library/framework documentation lookups.
- **WebFetch**: To read specific URLs the user provided or that appear in search results.

For each section, try at least 2 different search queries phrased differently. If initial searches don't yield good results, reformulate — use synonyms, different framing, more specific or more general terms.

### Source Evaluation (Keep/Discard)

Apply the same keep/discard logic as autoresearch's experiment loop. For each source:

| Signal | Keep | Discard |
|--------|------|---------|
| Relevance | Directly addresses a research question | Tangentially related at best |
| Credibility | Known institution, peer-reviewed, primary source | Anonymous blog, no citations, promotional |
| Recency | Within the user's recency preference | Outdated for the topic |
| Depth | Provides data, evidence, or novel insight | Restates common knowledge |
| Uniqueness | Adds a perspective not yet covered | Duplicates existing findings |

See `references/source-evaluation.md` for the full evaluation framework.

### Research Log

Maintain a running log as you research. This is like autoresearch's `results.tsv` — it tracks what was tried and what happened. Save it alongside the final artifact as `research-log.md`:

```markdown
# Research Log

## Section: [name]
| Query | Source | Verdict | Key Finding |
|-------|--------|---------|-------------|
| "query text" | source.com/article | keep | Finding X |
| "other query" | blog.example | discard | Not relevant |
```

### Handling Dead Ends

If a section yields poor results after 3-4 searches:
1. Note the gap in the research log
2. Try adjacent queries or broader terms
3. If still nothing, acknowledge the gap in the final artifact rather than filling it with weak sources
4. Move on — don't burn excessive time on one section

---

## Phase 4: Synthesize (Research Artifact)

After all sections are researched, compile findings into the final artifact. Use the template in `scripts/research-template.md` as a starting structure, but adapt it to the topic and output format the user requested.

### Artifact Structure

```markdown
# [Research Title]

> [One-line summary of the core finding or answer]

**Research Date:** [date]
**Scope:** [depth level] | [focus area]
**Sources consulted:** [count]

---

## Executive Summary
[2-3 paragraphs: what was found, what it means, what to do about it]

## Table of Contents
[auto-generated from sections]

## [Section 1]
### Key Findings
- Finding with [citation]
- Finding with [citation]

### Analysis
[Interpretation, implications, connections to other sections]

## [Section 2]
...

## Cross-Cutting Themes
[Patterns that emerged across sections]

## Gaps and Limitations
[What couldn't be determined, conflicting evidence, areas needing more research]

## Recommendations
[If actionable research: concrete next steps]
[If learning research: suggested further reading]

## Sources
[Numbered list of all sources with URLs]
```

### Quality Criteria

The research artifact is the "val_bpb" of this skill — it's the metric. A good artifact:

- **Answers the research questions** posed in the plan
- **Cites specific sources** for claims (not vague "studies show")
- **Acknowledges uncertainty** where evidence is mixed or thin
- **Distinguishes fact from analysis** (what was found vs. what it means)
- **Is appropriately sized** for the requested output format
- **Cross-references** findings across sections to surface patterns

### Save the Artifact

Save the final research artifact to the current directory as `research-[topic-slug].md`. Also save `research-log.md` alongside it.

Tell the user: "Research complete. The artifact is at `research-[topic-slug].md` with a research log at `research-log.md`."

---

## Reference Files

Read these as needed during execution:

- `references/research-methodology.md` — Frameworks for structuring research across different domains. Read this when planning research on an unfamiliar domain type.
- `references/source-evaluation.md` — Detailed source credibility assessment criteria. Read this when evaluating sources from unfamiliar or potentially unreliable sources.
- `scripts/research-template.md` — The base template for research artifacts. Read this when starting the synthesis phase.
- `examples/example-scoping-questions.md` — Example QA flows for different topic types. Reference this when designing scoping questions for unusual topics.
