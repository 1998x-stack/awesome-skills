# Response Examples

## Example 1: ambiguous feature request

User request:
`Help me improve our reporting dashboard.`

Good response shape:
1. Mission: define what "improve" means in user terms.
2. First principles: identify the real jobs-to-be-done.
3. Requirements to question: approvals, filters, tabs, export rules, legacy widgets.
4. What to delete: dashboards or metrics nobody uses.
5. Simplified plan: one primary workflow and one secondary workflow.
6. Fastest verification loop: instrument usage and run a lightweight prototype or mock.
7. What to automate later: scheduled reporting or personalization.
8. Risks: deleting something used by a hidden stakeholder; validate before removing.

## Example 2: performance issue

User request:
`Make this ETL job faster.`

Good response shape:
1. Mission: reduce runtime from X to Y without changing correctness.
2. First principles: isolate I/O, CPU, memory, and network costs.
3. Requirements to question: intermediate files, redundant validation, broad retries.
4. What to delete: unnecessary transforms or logging in the hot path.
5. Simplified plan: keep only the essential stages.
6. Fastest verification loop: benchmark a representative subset.
7. What to automate later: tuning, orchestration, and alerting after the hot path is clean.
8. Risks: optimizing a non-bottleneck or hiding a data-quality problem.

## Example 3: operating overhead

User request:
`Reduce weekly team overhead.`

Good response shape:
1. Mission: cut recurring overhead while protecting throughput and decision quality.
2. First principles: what decisions actually need synchronous discussion?
3. Requirements to question: every standing meeting, status report, and approval step.
4. What to delete: recurring rituals with no clear owner or decision output.
5. Simplified plan: fewer meetings, clearer owners, shorter update paths.
6. Fastest verification loop: compare cycle time and decision latency after two weeks.
7. What to automate later: reporting or reminders after the lean process works.
8. Risks: deleting invisible but critical coordination paths.
