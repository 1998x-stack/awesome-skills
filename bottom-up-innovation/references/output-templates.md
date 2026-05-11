# output templates

Use these templates to make bottom-up analysis consistent. Adapt when needed.

## Quick opportunity scan

### 结论
[one paragraph: the core judgment and where the biggest opportunity likely is]

### 本周最值得抓的活
| priority | work item | evidence | impact | size | owner fit | acceptance criteria |
| --- | --- | --- | --- | --- | --- | --- |
| p0 | [work] | [evidence] | [impact] | [xs/s/m/l] | [person type] | [done state] |

### 不建议现在做的活
| item | why not now | what evidence would change the decision |
| --- | --- | --- |

### 下一步
[3 concrete actions]

## Work card

### [work item title]

- 问题：
- 证据：
- 影响面：
- 目标：
- 初步方案：
- 规模：
- 适合人群：
- 风险依赖：
- 验收标准：
- 后续杠杆：

## Estimation table

| item | value | certainty | cost | risk | leverage | owner fit | decision |
| --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| [item] | [1-5] | [1-5] | [xs/s/m/l] | [1-5] | [1-5] | [owner] | do / spike / park / reject |

Add short reasons under the table for any controversial score.

## Dotted-line ownership plan

### 结论
[who should hold dotted-line ownership and why]

### 问题域
- 范围内：
- 范围外：
- 成功指标：

### 权责
- 可以决定：
- 必须同步：
- 不能越界：

### 人力配置
| role | count | responsibilities | review needs |
| --- | ---: | --- | --- |

### 周节奏
- 周一：更新机会池和本周执行池
- 周中：风险/依赖检查
- 周五：交付验收和复盘

### 通过标准
- 找活命中率：
- 估活准确率：
- 他人交付成功率：
- 质量/返工：
- 业务结果：

## Six-week pilot

### 目标
[what the pilot should prove]

### Week 1: build the work pool
- collect candidate work items
- require evidence and impact fields
- tag by domain and owner fit

### Week 2: estimate and select
- score value/certainty/cost/risk/leverage
- select execution pool
- identify 2-3 dotted-line owner candidates

### Weeks 3-4: execute through dotted-line owners
- assign small teams
- define gates and acceptance criteria
- keep scope narrow enough to ship

### Week 5: verify outcomes
- measure shipped work, quality, time saved, user/business impact
- separate demo success from actual operating impact

### Week 6: talent and mechanism review
- identify delivery, find-work, estimate-work, dotted-line, and business-judgment signals
- decide whether to expand, adjust, or stop the mechanism

## Talent map

Use evidence-based phrasing. Do not label people based on personality.

| person/group | observed signal | likely capability | confidence | next test |
| --- | --- | --- | --- | --- |
| [name/team] | [behavior/result] | delivery / find-work / estimate-work / dotted-line / business judgment | low/medium/high | [small assignment to validate] |

Capability definitions:

- stable delivery: finishes clearly defined work with good quality
- find-work: repeatedly discovers valuable problems with evidence
- estimate-work: predicts value/cost/risk/owner fit accurately
- dotted-line: coordinates others to ship without formal authority
- business judgment: sees which opportunity clusters matter strategically
- noise risk: many suggestions but weak evidence, weak prioritization, or low follow-through

## Delivery gate checklist

Before execution:
- problem and evidence are clear
- owner and reviewer are named
- acceptance criteria are observable
- dependencies and risks are explicit
- rollback or mitigation exists if needed

During execution:
- scope changes are reviewed
- blocker escalation path is known
- quality gate is not skipped for speed

Before completion:
- result is shipped or deliberately killed
- metric/observable effect is checked
- docs/tooling/handoff are complete if needed
- follow-up work is separated from current done state
