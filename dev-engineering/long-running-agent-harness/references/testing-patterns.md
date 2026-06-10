# Testing Patterns for Long-Running Agents

## The Self-Verification Blindspot

Without proper tooling, agents evaluate feature completion by:
1. Reading the code they just wrote
2. Mentally simulating what it does
3. Concluding "this looks correct"

This is unreliable. The solution: force **objective, behavioral verification**
through browser automation or API testing.

---

## Browser Automation: Puppeteer MCP

The recommended approach for web applications is the Puppeteer MCP server,
which gives the agent direct browser control.

### What Puppeteer MCP Enables

```
Agent calls → puppeteer_navigate("http://localhost:3000/register")
Agent calls → puppeteer_fill("#email", "test@example.com")
Agent calls → puppeteer_click("#submit-btn")
Agent calls → puppeteer_screenshot() → [image of result page]
Agent sees  → visual confirmation of success/failure
```

### Setting Up Puppeteer MCP

Add to your MCP configuration:
```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

### E2E Test Template for Agents

Include this in your coding agent prompt:
```
After implementing any UI feature, test it with Puppeteer:
1. Navigate to the relevant page
2. Perform the user action described in features.json test_steps
3. Take a screenshot at the end
4. Verify the expected state is visible
5. Only mark passes: true after visual verification
```

---

## API Testing (for Backend Features)

For API-only features, use curl or HTTPie:

```bash
# Test registration endpoint
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secure123"}' \
  -v

# Expected: 201 Created with user object
```

Agent prompt addition:
```
For API features, test with curl commands. Check:
- Status code is correct (200, 201, etc.)
- Response body has expected fields
- Error cases return appropriate error codes (400, 401, etc.)
```

---

## The Smoke Test Pattern

Every session starts with a smoke test. Here's what a good smoke test covers:

### Minimal Smoke Test (any web app)
```
1. Navigate to http://localhost:3000
2. Verify page loads (no 500 error, no blank screen)
3. If auth exists: log in with test credentials
4. If auth succeeds: verify landing page shows correct content
5. If ANY step fails: STOP, fix before new feature work
```

### Smoke Test for Chat Applications
```
1. Navigate to app root
2. Log in (or confirm already logged in)
3. Start a new conversation
4. Type "Hello" and send
5. Verify: AI response appears within 10 seconds
6. Verify: No error messages in the UI
```

### Automated Smoke Test in init.sh
```bash
#!/bin/bash
# ... (server startup) ...

# Automated smoke test
echo "=== Running smoke test ==="
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$HTTP_STATUS" = "200" ]; then
  echo "✓ Root page returns 200"
else
  echo "✗ Root page returned $HTTP_STATUS (expected 200)"
  echo "=== Smoke test FAILED ==="
  exit 1
fi

echo "=== Smoke test PASSED — Environment READY ==="
```

---

## Testing Constraints for Agent Prompts

These constraints should be in every coding agent prompt:

```
TESTING REQUIREMENTS:
- Test every feature using browser automation after implementing it
- Take at least one screenshot during testing as evidence
- It is UNACCEPTABLE to mark a feature passes: true without running a test
- It is UNACCEPTABLE to delete or modify existing passing tests
- If a test framework (Jest, pytest, etc.) exists, run it after every change
- A feature is only complete when the user-perspective test passes, not just
  when the code looks correct to you
```

---

## Common Testing Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Marking complete after code review | Broken features accumulate | Require E2E test for every feature |
| Not testing edge cases | Bugs discovered sessions later | Add negative test cases to features.json |
| Running unit tests only | Integration issues missed | Add smoke test covering full user flow |
| Not capturing screenshots | No evidence of pass/fail | Require screenshot in Puppeteer tests |
| Skipping smoke test at start | Session builds on broken base | Make smoke test mandatory, non-skippable |
