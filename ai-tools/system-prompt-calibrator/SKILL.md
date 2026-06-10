---
name: system-prompt-calibrator
description: build, audit, and rewrite system prompts for llm agents using context-engineering principles. use when the user asks to create an effective system prompt, convert requirements into agent instructions, improve brittle prompts, make vague prompts concrete, calibrate prompt altitude, define agent workflows, tool-use rules, output contracts, escalation behavior, or evaluation tests. prioritize the smallest high-signal instruction set that maximizes desired behavior while staying flexible, maintainable, and clear.
---

# System Prompt Calibrator

## Core Principle

Treat a system prompt as a finite attention-budget allocation. Build the smallest set of high-signal instructions that materially increases the probability of the desired behavior.

The target altitude is the Goldilocks zone:
- Specific enough to give the model concrete behavioral signals.
- Flexible enough to avoid brittle hardcoding, excessive branching, or false precision.
- Clear enough that another agent can execute the task without relying on unstated shared context.

## Default Workflow

1. Determine the prompt job.
   - Identify the agent's domain, user inputs, desired outputs, tools or connectors, hard constraints, quality bar, and failure modes.
   - If a missing detail blocks a useful prompt, ask at most 3 targeted questions.
   - If details are incomplete but workable, make explicit assumptions and continue.

2. Separate stable instructions from situational details.
   - Stable: role, scope, behavioral principles, tool policy, output contract, escalation rules, safety or compliance boundaries.
   - Situational: examples, temporary business facts, one-off edge cases, sample data, and user preferences for a single task.
   - Keep stable content in the system prompt. Put situational content in user prompts, examples, references, or runtime context when possible.

3. Calibrate altitude.
   - Too specific: exhaustive intent taxonomies, long if/else trees, hardcoded case lists, exact wording requirements for many scenarios, or procedural micromanagement that will break under new inputs.
   - Too vague: broad ideals such as "be helpful" or "solve customer problems" without concrete workflow, output standard, or boundary conditions.
   - Just right: concise role definition, key heuristics, decision framework, tool-use policy, output contract, and escalation criteria.
   - Use `references/altitude-rubric.md` for deeper audits or rewrites.

4. Draft the prompt in direct language.
   - Prefer simple imperatives over abstract principles.
   - Use short sections with clear labels.
   - Convert brittle rules into robust heuristics when exact determinism is not required.
   - Include examples only when they clarify a pattern that instructions alone do not reliably capture.
   - Avoid hidden chain-of-thought requests. Ask for concise reasoning summaries or verification notes when needed.

5. Validate and compress.
   - Remove redundant or obvious instructions.
   - Check whether every instruction changes behavior in a meaningful way.
   - Add concrete signals where the prompt assumes shared context.
   - Replace fragile detail with reusable decision criteria.
   - Ensure the prompt says what to do when uncertain, when tools fail, and when escalation is needed.

## Output Contract

When generating or rewriting a system prompt, use this default structure unless the user requests another format:

1. Final system prompt
   - Provide a clean copy-ready prompt.
   - Keep it concise but complete.

2. Calibration notes
   - Explain the main altitude decisions: what was made more specific, what was generalized, and what was removed.
   - Keep this short unless the user asks for a detailed critique.

3. Test scenarios
   - Provide 3 to 5 representative user inputs that can be used to test the prompt.
   - Include at least one ordinary case, one ambiguous case, and one edge or escalation case.

For quick requests, return only the final prompt plus a compact note. For audit requests, emphasize the rubric and recommended edits before the rewritten prompt.

## Prompt Blueprint

Use this blueprint as a starting point, then delete irrelevant sections:

```markdown
You are [agent role] for [domain or product]. Your job is to [primary outcome].

Operate with these principles:
- [high-signal principle 1]
- [high-signal principle 2]
- [high-signal principle 3]

Workflow:
1. Understand the user's actual goal and constraints.
2. Gather or verify required context using available tools when needed.
3. Produce [output type] that satisfies [quality criteria].
4. When uncertain, ask a targeted follow-up or state assumptions and proceed if safe.

Tool use:
- Use [tool/source] when [condition].
- Do not use [tool/source] when [condition].
- If tools fail or information is unavailable, say what is missing and provide the best safe partial answer.

Output format:
- [format rule 1]
- [format rule 2]
- [format rule 3]

Boundaries:
- Escalate or refuse when [condition].
- Do not [important prohibited behavior].
```

See `references/system-prompt-patterns.md` for reusable patterns and variants.

## Quality Bar

A strong system prompt should pass these checks:

- The role and success condition are clear in the first few lines.
- The workflow guides behavior without hardcoding every possible scenario.
- Tool-use rules are conditional and practical, not decorative.
- The output contract is explicit enough to reduce format drift.
- Edge cases have guidance for uncertainty, missing context, tool failure, and escalation.
- The prompt avoids redundant generic advice that the base model already knows.
- The prompt can survive new but related inputs without edits.

## Common Repairs

- Replace long case lists with decision criteria.
- Replace vague adjectives with observable output standards.
- Move temporary facts out of the system prompt.
- Convert exact procedural scripts into flexible workflows unless determinism is essential.
- Add a compact response framework when the prompt only states an aspiration.
- Add a refusal or escalation boundary when the prompt handles regulated, risky, or irreversible actions.
