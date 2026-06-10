# Architectural Constraints for Agent-First Codebases

Read this when the user needs to define dependency rules, set up structural testing,
enforce boundary parsing, or configure linters for agent-generated code.

---

## The Dependency Layer Model

The most powerful single constraint you can apply. Define a strict dependency
direction and enforce it via structural tests. Agents respect the rule uniformly
because CI enforces it on every PR — no exceptions, no "just this once."

### Defining Your Layers

Layers are domain-specific. A typical web app:

```
shared-types → config → db-repos → domain-services → api-handlers → frontend-ui

Rule: each layer may only import from layers to its LEFT (lower layers).
      No upward references. No cross-layer skips without going through the middle.
```

E-commerce example:
```
types → config → repositories → fulfillment/payments/users services → orchestration → web
```

Write this in `docs/architecture/layers.md`. Make it explicit enough that an agent
reading it can classify any module without asking.

### Enforcing with dependency-cruiser (JavaScript/TypeScript)

```javascript
// .dependency-cruiser.js
module.exports = {
  forbidden: [
    {
      name: 'no-upward-layer-dep',
      severity: 'error',
      comment: 'Dependencies may only flow from higher to lower layers',
      from: { path: '^src/layers/types/' },
      to: { path: '^src/layers/(config|repos|services|handlers|ui)/' }
    },
    {
      name: 'no-circular',
      severity: 'error',
      from: {},
      to: { circular: true }
    }
  ]
};
```

Run in CI: `npx depcruise --config .dependency-cruiser.js src`

### Enforcing with import-linter (Python)

```ini
# setup.cfg
[importlinter]
root_package = myapp

[importlinter:contract:layered]
name = Layered architecture
type = layers
layers =
    myapp.ui
    myapp.api
    myapp.services
    myapp.repositories
    myapp.config
    myapp.types
```

Run in CI: `lint-imports`

---

## Boundary Data Parsing

**The rule**: all data crossing a module or domain boundary must be validated against
an explicit schema. This prevents type drift from propagating and forces contracts
to be stated explicitly rather than implied.

Enforce the *behavior* — not the specific library. Agents will choose Zod, Pydantic,
Marshmallow, etc. based on the project stack.

### TypeScript / Zod (agent's typical choice)

```typescript
// Every boundary function looks like this:
import { z } from 'zod';

export const PaymentSchema = z.object({
  id: z.string().uuid(),
  amount: z.number().int().positive(),
  currency: z.enum(['USD', 'EUR', 'GBP']),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  createdAt: z.date(),
});

export type Payment = z.infer<typeof PaymentSchema>;

// Parse at the boundary — never trust incoming data
export function parsePayment(raw: unknown): Payment {
  return PaymentSchema.parse(raw);  // throws ZodError on invalid input
}
```

### Python / Pydantic (agent's typical choice)

```python
from pydantic import BaseModel, UUID4, PositiveInt
from enum import Enum
from datetime import datetime

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Payment(BaseModel):
    id: UUID4
    amount: PositiveInt
    currency: Currency
    status: PaymentStatus
    created_at: datetime

# At the boundary:
def parse_payment(raw: dict) -> Payment:
    return Payment.model_validate(raw)  # raises ValidationError on failure
```

### Custom Lint Rule to Enforce Boundary Parsing Exists

Rather than reviewing every PR manually, write a lint rule that detects public-facing
module APIs missing validation:

```javascript
// ESLint rule: exported functions accepting `unknown` or `any` must call parse/validate
// This is a simplified illustration — adapt to your conventions
module.exports = {
  rules: {
    'boundary-parse-required': {
      create(context) {
        return {
          ExportNamedDeclaration(node) {
            // Detect exported functions with unknown/any params lacking parse calls
            // Implementation details depend on your boundary convention
          }
        };
      }
    }
  }
};
```

---

## Security Constraints

Agent-generated code can introduce subtle security issues at high throughput.
Encode these as CI gates, not review checklists:

```yaml
# CI pipeline gates (GitHub Actions example)
- name: Security scan
  run: npx snyk test --severity-threshold=high

- name: Static analysis
  run: npx sonarqube-scanner

- name: Dependency audit
  run: npm audit --audit-level=high

- name: Structural layer check
  run: npx depcruise --config .dependency-cruiser.js src
```

For database migrations specifically, require explicit human async approval.
These are high-risk, hard-to-reverse, and should never auto-merge.

---

## What Good Constraint Coverage Looks Like

| Constraint | Enforcement | Failure Mode Without It |
|-----------|-------------|------------------------|
| Dependency direction | dependency-cruiser / import-linter CI | Circular deps, spaghetti, impossible refactors |
| Boundary parsing | Custom lint rule or PR checklist | Type drift propagates silently across modules |
| No circular deps | Structural test CI | Build failures, unpredictable module load order |
| Doc cross-refs valid | Markdown link checker CI | Agents navigate to 404s, ignore broken docs |
| Security scan | Snyk/SonarQube CI | Vulnerabilities accumulate undetected |
| Test coverage floor | Coverage CI gate | Quality regressions go unnoticed |

Add constraints incrementally — start with dependency direction and boundary parsing,
as these have the highest leverage per constraint-added.
