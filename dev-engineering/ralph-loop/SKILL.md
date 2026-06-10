---
name: ralph-loop
description: emulate a ralph loop style outer iteration for local coding and repo tasks with persistent state, git awareness, and objective completion checks. use when chatgpt should keep working on the same engineering task across repeated validation cycles instead of stopping after one attempt, especially for bug fixing, test-driven implementation, lint or type failures, api scaffolding, refactors, or other repository work with clear commands or completion markers.
---

# Ralph Loop

Use this skill to run a Ralph Loop style **outer iteration** around a local engineering task.

This skill does **not** install Claude Code stop hooks. Instead, emulate the same behavior with the tools available here:
- keep the task statement stable across iterations
- preserve repo state on disk
- use external checks instead of trusting narrative completion claims
- continue until the completion contract passes or the iteration budget is exhausted

## Core rule

Do not treat "done" as a prose judgment.

Treat the completion contract as the source of truth. A task is complete only when the selected checks pass, such as:
- one or more test, build, lint, or type commands
- a marker file containing a required completion string
- optionally, a clean git working tree if the task requires it

## Decide the loop shape before editing code

Before the first code change, lock these items:

1. **Task statement**
   - Write one stable task sentence.
   - Reuse it across every iteration.
   - Do not silently broaden scope midway through the loop.

2. **Workdir**
   - Use the target repo or folder as the stable working directory.

3. **Completion contract**
   - Prefer concrete commands such as `pytest`, `npm test`, `pnpm lint`, `ruff check`, `cargo test`, or `go test`.
   - Add a marker file when the task also requires a specific human-readable handoff, for example `.ralph-loop/done.txt` containing `RALPH_LOOP_COMPLETE`.
   - Use at least one objective check. Never run a loop with no external completion condition.

4. **Iteration budget**
   - Set a maximum iteration count.
   - Keep the loop finite.

## Workflow

### 1. Initialize the session

Run the bundled runner to create or continue a session and evaluate the current state.

```bash
python scripts/run_ralph_loop.py \
  --task "fix the auth refresh regression and make the targeted tests pass" \
  --workdir /path/to/repo \
  --max-iterations 8 \
  --command "pytest tests/auth/test_refresh.py -q" \
  --command "ruff check src tests" \
  --marker-file /path/to/repo/.ralph-loop/done.txt \
  --marker-string RALPH_LOOP_COMPLETE
```

Use the runner output to anchor the next iteration. It will:
- persist session state under `.ralph-loop/`
- run the completion checks
- summarize command failures and git state
- tell you whether to continue, stop as complete, or stop because the budget is exhausted

### 2. Read the failure signal before making edits

On each incomplete iteration:
- identify the first failing command or missing marker
- inspect the relevant code and tests
- make one focused batch of edits aimed at that failure
- avoid broad speculative rewrites unless the evidence supports them

If the repo is unfamiliar, inspect files first and consult [references/design.md](references/design.md).

### 3. Re-run the same loop

After edits, re-run the same `run_ralph_loop.py` command with the same task and the same completion contract.

Preserve the task statement. The point of the loop is repeated execution against the same target, not prompt drift.

### 4. Stop only for one of these reasons

Stop when exactly one of these happens:
- the completion contract passes
- the maximum iteration count is reached
- a hard blocker prevents further progress and you can explain it concretely

When the budget is exhausted without success, report the strongest blocker, the most recent failure signal, and the smallest next step.

## Use the scripts deliberately

### `scripts/run_ralph_loop.py`

Use this as the default entrypoint for the loop.

It is best when you need:
- persistent session state
- iteration counting
- a concise handoff summary after each loop
- git snapshot context

### `scripts/check_completion.py`

Use this directly when you only need deterministic verification.

It is best when you need:
- a pass or fail answer for one repo state
- machine-readable JSON output
- a marker-file check without session bookkeeping

Example:

```bash
python scripts/check_completion.py \
  --workdir /path/to/repo \
  --command "pytest tests/unit/test_api.py -q" \
  --marker-file /path/to/repo/.ralph-loop/done.txt \
  --marker-string RALPH_LOOP_COMPLETE \
  --json-out /tmp/ralph-check.json
```

## Default operating pattern

Use this pattern unless the task clearly needs something else:

1. Define one stable task statement.
2. Define one to three verification commands.
3. Add a marker file only if a final explicit handoff is useful.
4. Run `run_ralph_loop.py`.
5. Fix the most important current failure.
6. Re-run `run_ralph_loop.py`.
7. Repeat until complete or out of budget.

## Output pattern for loop updates

When reporting progress inside the loop, use this structure:

```text
iteration: <current>/<max>
status: continue | complete | blocked | budget-exhausted
primary failure: <first failing command or missing contract element>
changes made: <brief factual summary>
next check: <exact command or contract to re-run>
```

Keep loop updates terse and evidence-based.

## References

Read these when relevant:
- [references/design.md](references/design.md) for the conceptual model, tradeoffs, and failure modes
- [references/examples.md](references/examples.md) for concrete loop setups in Python, Node, Rust, and marker-based workflows
