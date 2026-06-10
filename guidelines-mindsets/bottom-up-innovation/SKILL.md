---
name: bottom-up-innovation
description: analyze bottom-up innovation and opportunity discovery workflows for product, engineering, operations, and platform teams. use when the user describes a business, product, system, org, or delivery scenario and wants help finding valuable work, converting ideas into executable work cards, estimating value/cost/risk/manpower, designing dotted-line ownership, prioritizing a work pool, improving delivery success, or evaluating find-work, estimate-work, organize-work, and business-judgment capability. also use for opportunity maps, talent maps, six-week pilots, delivery gates, retrospectives, and bottom-up management mechanisms.
---

# bottom-up innovation

## Overview

Use this skill to help the user turn a vague scenario, product area, system, team problem, or operational friction into a bottom-up work system: find valuable work, estimate the work, assign it to suitable people, and raise delivery success.

Default to Chinese unless the user asks otherwise. Be direct, mechanism-first, and practical. Treat bottom-up not as free ideation, but as a repeatable system for opportunity discovery, problem definition, lightweight resource allocation, and quality delivery.

## Core model

Bottom-up innovation has four capability layers:

1. **交付能力**：能把别人定义好的活稳定做好。
2. **找活能力**：能主动发现业务系统、产品体验、工程质量、流程效率、工具链、ai 化空间里的有效机会。
3. **估活能力**：能判断一个活值不值得做、成本多大、风险在哪里、需要谁、验收标准是什么。
4. **组织交付能力**：能判断一整块系统有多少活，设计虚线机制，把活拆给合适的人，并保证高质量交付。

A useful shorthand: **合格的人等活；高级的人找活；更高级的人能判断哪里有一片活，并组织别人一起把它吃下来。**

## First move: classify the user's request

Determine which mode best fits. If multiple apply, combine them.

- **找活模式**：user gives a domain/system/team/scenario and asks what can be done.
- **估活模式**：user gives one or more ideas/work items and asks whether worth doing, how large, or who should do it.
- **交付模式**：user wants to improve delivery success, split work, define gates, or reduce failure risk.
- **虚线机制模式**：user wants to design dotted-line ownership, allocate interns/engineers, or scale a person beyond individual execution.
- **人才识别模式**：user wants to identify who has find-work, estimate-work, organize-work, or business-judgment capability.
- **试点机制模式**：user wants a bottom-up pilot, weekly rhythm, scorecard, or management mechanism.

Do not over-ask. If the scene is incomplete but workable, state assumptions and proceed. Ask up to three concise questions only when missing information would materially change the answer, usually: business goal, users/stakeholders, available people/time, current evidence, or risk constraints.

## Grounding rules

For work-related, internal, or latest-sensitive requests, use available internal connectors or uploaded files when possible before making recommendations. Look for docs, recordings, meeting notes, issue lists, support tickets, dashboards, PRs, or chats that show real pain, repeated friction, active priorities, and known constraints.

If internal search is unavailable or thin, say so briefly and continue from the user's provided context. Do not invent internal facts, metrics, owners, or priorities.

Always distinguish:

- **事实**：directly supported by user input or sources.
- **判断**：reasoned interpretation from the facts.
- **假设**：needed assumption that should be validated.

## Workflow

### 1. Build a thin context map

Extract or infer:

- domain/system: what product, tool, workflow, team, or business area is involved
- target outcome: growth, efficiency, quality, safety, content supply, creator/user experience, ai adoption, revenue, reliability
- current friction: repeated manual work, bugs, slow review, unclear ownership, data blind spots, coordination cost, user complaints
- evidence: screenshots, logs, metrics, support tickets, meetings, anecdotes, repeated requests
- constraints: people, time, permissions, risk, dependencies, launch windows, existing roadmap

Keep this lightweight. The goal is not a PRD; the goal is to find executable work.

### 2. Find work using opportunity lenses

Use multiple lenses instead of random brainstorming. Read `references/opportunity-lenses.md` when doing a deep opportunity search.

Default lenses:

- repeated bugs / quality instability
- user or internal stakeholder complaints
- manual toil / repeated operations
- data anomaly / unmeasured funnel
- ai automation / ai-assisted workflow
- toolchain bottleneck / developer productivity
- review, safety, audit, permission, or compliance drag
- content supply, creation threshold, or creator tooling
- growth / conversion / retention leak
- platform debt / future scalability blocker

Generate concrete work items, not vague ideas. Each candidate should be stated as a problem with evidence and expected impact.

### 3. Convert ideas into work cards

For each promising item, create a card with:

- **问题**：what friction exists
- **证据**：how we know it exists
- **影响面**：who/how many workflows/what metric is affected
- **目标**：what better state looks like
- **初步方案**：one practical path, not a full design unless needed
- **规模**：xs/s/m/l/xl or person-days/weeks
- **适合人群**：intern, engineer, senior engineer, product/ops, cross-functional
- **风险依赖**：technical, product, data, permission, review, cross-team
- **验收标准**：done means what, with metric or observable behavior
- **后续杠杆**：whether this unlocks more work or only fixes a local issue

### 4. Estimate value, cost, risk, and owner fit

Use `references/scoring-and-estimation.md` when estimating or prioritizing many items.

Prefer ranges over fake precision. When uncertain, show what would validate the estimate.

Score each work item across:

- **价值**：impact on business/user/internal efficiency
- **确定性**：quality of evidence and likelihood of impact
- **成本**：time, complexity, coordination
- **风险**：rollback difficulty, quality/safety exposure, dependency risk
- **杠杆**：whether it unlocks repeated future work
- **人选适配**：whether it is suitable for intern, engineer, senior, or cross-functional owner

Then classify:

- **快赢**：high value, low cost, high certainty
- **杠杆活**：may cost more but unlocks a class of future work
- **学习活**：uncertain but cheap enough to test
- **危险活**：uncertain, high coordination/risk, needs senior review or should wait
- **噪音活**：low evidence, low value, or mostly personal preference

### 5. Improve delivery success

Do not stop at prioritization. For selected work, define:

- owner and backup
- task split and sequence
- decision gates
- quality gates
- review checkpoints
- data/metric validation
- rollback or mitigation plan
- handoff/documentation requirement
- weekly cadence and escalation path

For dotted-line ownership, specify what authority the owner has and what boundaries apply.

A dotted-line owner should usually have authority to:

- maintain the opportunity pool for a problem domain
- propose what enters the weekly execution pool
- split work and recommend staffing
- define acceptance criteria and review quality

But should not:

- hijack others' mainline roadmap without agreement
- create unbounded work under the name of innovation
- bypass necessary technical/product/safety review
- turn coordination into status-chasing without clear value

### 6. Produce opportunity and talent maps when relevant

Opportunity map:

- where the most valuable clusters of work are
- which clusters are suitable for interns/engineers/seniors/cross-functional teams
- which are local fixes vs system-level opportunities
- where a formal owner may be needed

Talent map:

- stable delivery people
- high-quality find-work people
- accurate estimate-work people
- dotted-line organizer candidates
- business-judgment candidates
- noisy idea generators with weak evidence or low delivery follow-through

Be careful with people judgments. Use observed behavior and evidence, not personality labels. Phrase uncertain assessments as hypotheses to validate.

## Output style

Default answer structure:

1. **结论**：one concise judgment.
2. **机会地图 / 工作池**：concrete work items, grouped by domain or priority.
3. **估活与分配**：value/cost/risk/person fit.
4. **交付设计**：how to make selected work succeed.
5. **需要验证的假设**：only the important unknowns.

Use tables for multiple work items. Use short paragraphs for executive judgment. Avoid motivational language and generic innovation slogans.

For a quick answer, return 5-10 high-quality work cards and the top 3 recommended actions.

For a deep analysis, include a prioritized backlog, dotted-line staffing plan, delivery gates, scorecard, and a 2-6 week pilot plan.

See `references/output-templates.md` for reusable formats.

## Quality bar

A good response should:

- turn vague opportunities into executable work
- separate evidence from judgment and assumptions
- identify the smallest useful next step
- explain why some ideas should not be done now
- estimate owner fit and coordination cost, not just engineering effort
- include acceptance criteria and delivery gates
- make talent signals observable through work results

Avoid:

- treating bottom-up as open-ended brainstorming
- rewarding idea count over idea quality
- producing only a roadmap without delivery mechanism
- over-allocating people before proving value
- calling someone a manager just because they find many tasks
- using fake precision when evidence is weak
