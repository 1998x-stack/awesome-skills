# opportunity lenses

Use this reference when the user asks to find work from a product, system, team, tool, or operational scenario.

## Principle

Do not brainstorm from personal interest. Search for friction, repeated waste, hidden demand, unmeasured leakage, and system constraints. Convert each finding into a work card with evidence, impact, owner fit, and acceptance criteria.

## 1. Repeated bugs and quality instability

Signals:
- the same class of bug appears repeatedly
- engineers keep patching symptoms
- support/ops has a workaround list
- incident postmortems repeat the same root cause

Good work items:
- add missing validation or invariant checks
- create regression tests for recurring defects
- add observability around the unstable path
- simplify or retire fragile code paths
- write a migration or cleanup plan if the issue is structural

Avoid:
- fixing one visible bug while ignoring the recurring class
- creating dashboards no one will monitor

## 2. User or internal stakeholder complaints

Signals:
- repeated complaints from users, creators, ops, support, editors, BD, QA, or developers
- people say “每次都要手动处理” or “这个地方总是卡”
- unclear ownership causes slow response

Good work items:
- reduce the number of steps in a common workflow
- provide self-serve tooling for repeated requests
- add better error messages, status visibility, or next actions
- create routing/triage rules for ambiguous issues

Avoid:
- treating all complaints as equal
- accepting anecdote without checking frequency or severity

## 3. Manual toil and repeated operations

Signals:
- repeated copy-paste, reconciliation, status update, manual review, report generation
- work is done by high-skill people but does not require their judgment
- delays come from queueing, not hard decisions

Good work items:
- automate the repetitive part while keeping human judgment at the gate
- create batch tools, templates, or one-click actions
- add ai draft/review/summarization where the cost of manual preparation is high
- create self-service flows for requesters

Avoid:
- fully automating decisions that require accountability
- building complex tools for rare workflows

## 4. Data anomaly or unmeasured funnel

Signals:
- metric changes but no owner knows why
- funnel drops at a step with no instrumentation
- teams argue from anecdotes because logs/dashboards are missing
- success cannot be measured after launch

Good work items:
- add event logging or dashboard for a critical flow
- define a north-star and guardrail metric for a workflow
- create a diagnostic report for recurring questions
- run a small investigation to explain an anomaly

Avoid:
- adding metrics without a decision they inform
- overbuilding analytics before knowing the decision need

## 5. AI automation or AI-assisted workflow

Signals:
- humans repeatedly summarize, classify, rewrite, tag, review, generate, translate, or search
- expert judgment is needed, but preparation work is mechanical
- large context must be gathered before a decision

Good work items:
- ai-assisted triage or summarization with human approval
- ai-generated drafts with explicit review gates
- ai search over internal knowledge for repeated questions
- ai QA/checklist for common mistakes
- workflow where human defines direction and ai accelerates execution

Avoid:
- replacing accountable decisions with opaque ai output
- shipping ai features without quality gates and fallback path

## 6. Toolchain and developer productivity bottleneck

Signals:
- slow build/test/deploy/review loops
- onboarding is slow because knowledge is scattered
- devs frequently ask the same setup/debug questions
- local environment or CI failures consume repeated time

Good work items:
- reduce build/test time for the hottest loop
- document or automate environment setup
- create templates, generators, or scripts for repeated project patterns
- improve CI signal quality and failure triage

Avoid:
- broad platform rewrites without a narrow proof of value

## 7. Review, safety, audit, permissions, and governance drag

Signals:
- approval happens late and causes rework
- reviewers lack context and ask repeated questions
- permissions are unclear or too coarse
- teams bypass process because it is too slow

Good work items:
- move review criteria earlier into templates or tooling
- define risk tiers and different gates by tier
- add preflight checks before submission
- create audit trails for high-risk operations

Avoid:
- adding one more manual approval without reducing ambiguity

## 8. Content supply, creation threshold, and creator tooling

Signals:
- creators/users fail before publishing or submitting
- content quality depends on manual coaching
- asset preparation or review is slow
- there are many unfinished drafts or abandoned flows

Good work items:
- reduce creation steps
- provide templates, examples, validation, or ai co-creation
- add feedback loops before final submission
- surface why content failed and what to do next

Avoid:
- optimizing final publishing while ignoring upstream preparation

## 9. Growth, conversion, and retention leaks

Signals:
- users drop at a specific step
- activation depends on manual guidance
- a valuable feature has low discovery or weak first-use experience
- retention pain appears in support/community feedback

Good work items:
- improve onboarding or first successful action
- add prompts, defaults, examples, or guided flows
- reduce setup time before value is felt
- test targeted interventions with metrics

Avoid:
- generic growth hacks without a specific behavioral bottleneck

## 10. Platform debt and future scalability blockers

Signals:
- a subsystem blocks many future initiatives
- local changes require too much coordination
- core concepts are inconsistent across teams
- a manual process cannot scale with expected volume

Good work items:
- define a stable interface or domain model
- remove a recurring dependency bottleneck
- migrate a risky/central path in small steps
- create a platform capability that unblocks multiple product teams

Avoid:
- large cleanups with no near-term user or business proof

## Work item phrasing pattern

Use this sentence form:

“因为 [证据/摩擦]，导致 [影响面/损失]。建议做 [具体动作]，目标是 [可观察结果]。规模大约 [xs/s/m/l]，适合 [人选]，主要风险是 [风险]。”
