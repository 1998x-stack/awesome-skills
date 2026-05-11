# scoring and estimation

Use this reference when estimating work, prioritizing a work pool, or deciding staffing/ownership.

## Size scale

Use rough ranges unless the user provides better data.

| size | typical effort | description | suitable owner |
| --- | --- | --- | --- |
| xs | 0.5-1 day | small fix, copy/tooling tweak, one narrow script, minor dashboard | intern or engineer with review |
| s | 1-3 days | contained feature, clear bug class, simple automation, narrow instrumentation | intern+engineer or engineer |
| m | 1-2 weeks | cross-module work, meaningful workflow change, multiple stakeholders | engineer or senior owner |
| l | 2-6 weeks | system-level change, multiple dependencies, product/design/data involvement | senior or dotted-line owner |
| xl | 6+ weeks | platform/strategy-level project, high uncertainty or org coordination | formal owner/project setup |

If work has high uncertainty, split into a discovery spike first.

## Value score

Score 1-5:

1. cosmetic or personal preference
2. local convenience for a few people
3. clear efficiency/quality/user improvement in one workflow
4. meaningful business/user/internal leverage across a team or system
5. strategic unlock, large user/business impact, or reusable platform capability

## Certainty score

Score 1-5:

1. opinion only, little evidence
2. anecdotal but plausible
3. repeated evidence from users/ops/logs/support or clear expert judgment
4. metrics or multiple independent signals support it
5. strong causal evidence or already validated prototype/experiment

## Cost score

Score 1-5 where higher means more expensive:

1. xs, no meaningful dependency
2. s, one owner, low risk
3. m, some coordination or review
4. l, cross-team dependency or migration risk
5. xl, high uncertainty, high coordination, high rollback cost

## Risk score

Score 1-5:

1. easy rollback, no user/safety impact
2. contained risk, normal review enough
3. possible quality or workflow disruption
4. cross-team, data, permission, review, or reliability risk
5. high user/business/safety exposure; needs formal gating

## Leverage score

Score 1-5:

1. one-off local fix
2. small repeated benefit
3. removes repeated toil or bug class
4. unlocks a queue of future work or many downstream users
5. creates a new reusable capability, platform, or organizational operating rhythm

## Priority formula

Do not overfit to numbers, but this heuristic is useful:

priority = (value + certainty + leverage) / (cost + risk)

Then override with judgment when:

- a low-score item is mandatory for safety/compliance
- an item is a dependency for several high-value items
- an item is cheap enough to learn quickly
- an item creates irreversible risk

## Classification

| class | pattern | action |
| --- | --- | --- |
| quick win | high value/certainty, low cost/risk | do now; assign to intern/engineer with clear review |
| leverage work | high value/leverage, medium cost | give senior/dotted-line owner; break into milestones |
| learning work | uncertain value but cheap | run spike/prototype; define learning question |
| dangerous work | high value but high risk/cost/uncertainty | require senior review, staged rollout, or defer |
| noise | low evidence, low value, unclear owner | park or reject; ask for evidence |

## Owner fit

Use these defaults:

- **intern**: clear boundaries, low risk, good acceptance criteria, reviewable output
- **engineer**: contained execution with known technical path
- **senior engineer**: ambiguous problem, architecture choice, high-risk path, mentoring needed
- **product/ops**: workflow definition, stakeholder alignment, business rules, acceptance criteria
- **dotted-line owner**: recurring opportunity pool, multi-person coordination, cross-domain delivery
- **formal owner / real-line manager**: sustained domain ownership, people/resource decisions, roadmap authority

## Estimation output pattern

For each item:

- value: 1-5 with reason
- certainty: 1-5 with reason
- cost: xs/s/m/l/xl and person estimate
- risk: 1-5 with main risk
- leverage: 1-5 with reason
- owner fit: who should own and who should review
- delivery gate: what must be true before shipping
- acceptance criteria: observable done state
