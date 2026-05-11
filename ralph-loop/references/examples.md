# Ralph Loop Examples

## Python bug fix

```bash
python scripts/run_ralph_loop.py \
  --task "fix the pagination off-by-one bug and make the targeted tests pass" \
  --workdir /repo \
  --max-iterations 6 \
  --command "pytest tests/api/test_pagination.py -q" \
  --command "ruff check src tests"
```

Use this when one failing test or a small cluster of tests identifies the bug.

## Node service repair

```bash
python scripts/run_ralph_loop.py \
  --task "repair the session timeout flow without breaking lint or unit tests" \
  --workdir /repo \
  --max-iterations 8 \
  --command "pnpm test -- --runInBand src/session/session.test.ts" \
  --command "pnpm lint"
```

Prefer the smallest high-signal test target first. Add the full suite later only if it materially changes the completion definition.

## Rust implementation loop

```bash
python scripts/run_ralph_loop.py \
  --task "implement refresh token rotation for the auth module" \
  --workdir /repo \
  --max-iterations 10 \
  --command "cargo test auth::refresh" \
  --command "cargo clippy -- -D warnings"
```

This is a good fit for feature work with a tight test target and a compile or lint gate.

## Marker-based completion

```bash
mkdir -p /repo/.ralph-loop
printf 'RALPH_LOOP_COMPLETE\n' > /repo/.ralph-loop/done.txt

python scripts/check_completion.py \
  --workdir /repo \
  --command "pytest tests/unit/test_sync.py -q" \
  --marker-file /repo/.ralph-loop/done.txt \
  --marker-string RALPH_LOOP_COMPLETE
```

Use this when the task needs both passing commands and an explicit handoff token.

## JSON output for automation

```bash
python scripts/check_completion.py \
  --workdir /repo \
  --command "go test ./..." \
  --json-out /tmp/ralph-check.json
cat /tmp/ralph-check.json
```

The JSON file is useful when another script or workflow needs deterministic pass or fail data.

## Suggested response shape inside the loop

```text
iteration: 3/8
status: continue
primary failure: pytest tests/api/test_pagination.py -q
changes made: corrected page boundary logic in paginator.py and aligned the cursor test fixture
next check: python scripts/run_ralph_loop.py --task "fix the pagination off-by-one bug and make the targeted tests pass" ...
```

Keep the update short. The verification output already carries the detail.
