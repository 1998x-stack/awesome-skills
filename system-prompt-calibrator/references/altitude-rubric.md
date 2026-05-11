# Altitude Rubric for System Prompts

Use this rubric to calibrate whether a prompt is too specific, too vague, or just right.

## The Goldilocks Rule

A good system prompt sits between brittle control and empty aspiration. It should give the model enough concrete signal to act consistently, while preserving judgment for inputs that were not enumerated in advance.

## Too Specific

Symptoms:
- Large intent taxonomies that require exact classification before action.
- Nested if/then procedures for many small cases.
- Exhaustive edge-case lists that try to simulate business logic in prose.
- Repeated instructions that constrain wording rather than behavior.
- Tool calls mandated in rigid order when the situation may not require them.
- Prompt grows whenever a new bug or edge case appears.

Risks:
- Fragile behavior on novel inputs.
- Maintenance cost rises over time.
- The model follows stale rules instead of solving the actual task.
- Important context is crowded out by low-signal details.

Repair moves:
- Collapse case lists into decision criteria.
- Express invariant policy, not every branch.
- Move deterministic logic into code, tools, or external policies if exactness matters.
- Keep only examples that teach a reusable pattern.

## Too Vague

Symptoms:
- Describes values but not behavior.
- Uses broad goals such as "be helpful", "be professional", or "solve the issue" without workflow or output standard.
- Assumes the model knows product context, policies, user expectations, or available tools.
- Omits what to do when information is missing or uncertain.
- Omits format requirements for the final answer.

Risks:
- Inconsistent outputs.
- Hallucinated context or policy.
- Excessive follow-up questions or premature answers.
- No reliable evaluation criteria.

Repair moves:
- Add role, scope, and concrete success criteria.
- Add a compact workflow.
- Define tool-use triggers.
- Define output structure.
- Define uncertainty and escalation behavior.

## Just Right

Signals:
- The first paragraph establishes role, domain, and primary outcome.
- The prompt encodes a small number of durable behavioral heuristics.
- The workflow is sequential but not overfit.
- Tool instructions say when and why to use tools.
- Output expectations are specific enough to reduce drift.
- Boundaries are explicit for uncertainty, missing data, safety, compliance, or escalation.
- The prompt can handle adjacent scenarios without needing new rules.

## Calibration Questions

Ask these during review:

1. What behavior would change if this sentence were removed?
2. Is this instruction stable across most future requests?
3. Is this detail better placed in runtime context, a reference document, a tool, or code?
4. Does the prompt tell the agent how to decide, not just what to value?
5. Does the prompt define what to do when the situation is ambiguous?
6. Would the prompt still work for a realistic edge case not named here?
7. Is the output standard observable by a reviewer?

## Example Pattern

Too specific:
```markdown
For every request, classify the intent as one of: incident_resolution, general_inquiry, order_resubmission, account_maintenance, requires_escalation. If intent is incident_resolution, ask exactly 3 follow-up questions before using tools. If intent is general_inquiry, do not ask follow-up questions. If the user mentions an order id, tag the request as order_resubmission if five listed conditions are met...
```

Why it fails:
- It encodes brittle taxonomy and procedural details in the prompt.
- New cases require prompt edits.
- The agent may obey classification rules instead of solving the user problem.

Too vague:
```markdown
You are a bakery assistant. Solve customer issues in a way consistent with the brand. Escalate when needed.
```

Why it fails:
- It does not define the job, tools, workflow, output standard, or escalation criteria.
- It assumes shared context about the brand and policies.

Just right:
```markdown
You are a customer support agent for a bakery. Help customers with orders and basic questions. Use available order, catalog, and policy tools to verify facts before giving status, inventory, refund, or policy answers.

Workflow:
1. Identify the customer's real issue, not only the surface complaint.
2. Gather only the context needed to resolve it.
3. Provide the clearest next step or resolution, including realistic timelines.
4. Confirm the customer understands what will happen next.

Escalate to a human for legal issues, health or allergy emergencies, financial adjustments beyond standard policy, or cases where available tools cannot establish the facts.
```

Why it works:
- It gives role, scope, workflow, tool triggers, and boundaries.
- It avoids brittle taxonomies.
- It leaves room for judgment on novel but related cases.
