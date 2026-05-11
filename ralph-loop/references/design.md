# Ralph Loop Design Notes

## Purpose

Ralph Loop is an **outer loop**, not a reasoning style.

Its job is to stop an agent from claiming victory too early. The loop keeps the task stable and re-checks objective completion after each attempt.

In practical terms:
- the repo state changes over time
- the task statement stays stable
- the completion contract stays stable unless there is a justified correction
- each iteration uses the newest repo state and the latest failure signal

## What makes it different from ReAct or Plan-and-Execute

- **ReAct** controls the next step inside one trajectory.
- **Plan-and-Execute** controls explicit subtask planning inside one trajectory.
- **Ralph Loop** controls whether the whole task gets another attempt.

A good mental model is:

`Ralph Loop = stable objective + repeated verification + bounded retries`

## Why external checks matter

Model self-assessment is noisy. External checks are useful because they are:
- reproducible
- falsifiable
- easy to compare across iterations

Prefer these signals:
1. targeted tests
2. build or type checks
3. lint checks
4. marker files with required strings
5. git cleanliness when relevant

## Choosing the completion contract

### Best contracts

Use contracts with clear pass or fail behavior:
- `pytest tests/foo/test_bar.py -q`
- `npm test -- --runInBand src/foo.test.ts`
- `cargo test auth_refresh`
- `go test ./...`
- `ruff check src tests`
- `mypy src`

### Good supplemental contracts

Use these in addition to commands:
- marker file exists
- marker file contains a required token
- required artifact exists at a path

### Weak contracts

Avoid these as the only success signal:
- "the code looks correct"
- "the refactor seems complete"
- "the explanation is done"

## Recommended iteration behavior

On each loop:

1. Run verification.
2. Identify the first failing or missing contract element.
3. Make the smallest credible change that addresses it.
4. Re-run verification.
5. Record what changed and what remains broken.

This minimizes drift and keeps the loop grounded.

## Common failure modes

### 1. Prompt drift

The task expands over time and the agent starts solving a different problem.

Mitigation:
- keep one stable task statement in the session
- report scope changes explicitly before adopting them

### 2. Verification drift

The loop changes the completion commands midway to make success easier.

Mitigation:
- keep the original commands fixed unless they are invalid or broken
- explain any contract correction explicitly

### 3. Thrashing

The loop changes too many things between runs and loses the thread.

Mitigation:
- prefer one focused batch of edits per iteration
- start from the highest-signal failure

### 4. Silent blocker accumulation

The loop keeps trying even though an external dependency or missing spec prevents progress.

Mitigation:
- stop and report blockers when the evidence shows the task cannot complete locally
- do not spend the entire budget pretending the task is tractable if it is not

## When to use a marker file

Use a marker file when command success is necessary but not sufficient.

Examples:
- the user wants a final migration note written to a known file
- a generated artifact must exist and be explicitly acknowledged
- the task requires a human-readable "handoff complete" token

A common pattern is:
- verification commands must all pass
- `.ralph-loop/done.txt` must contain `RALPH_LOOP_COMPLETE`

## Honest limitation in this skill

This skill emulates the Ralph Loop pattern with the tools available to ChatGPT.
It does not install Claude Code plugins or stop hooks. The repeat loop is driven by explicit re-runs of the bundled scripts and by keeping the repo state on disk.
