# Initializer Agent — Full Guide

## Purpose

The initializer agent runs **exactly once** — in the very first context window.
Its sole job is to build the scaffolding that all future coding agents will use.
It should NOT implement any features itself.

---

## What to Create

### 1. `init.sh` — Environment Bootstrap Script

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== Starting environment ==="

# Install dependencies
if [ -f package.json ]; then
  npm install --silent
elif [ -f requirements.txt ]; then
  pip install -r requirements.txt -q
fi

# Start dev server in background
npm run dev &
DEV_PID=$!
echo "Dev server PID: $DEV_PID"

# Wait for server to be ready
MAX_WAIT=30
WAIT=0
while ! curl -s http://localhost:3000 > /dev/null 2>&1; do
  sleep 1
  WAIT=$((WAIT+1))
  if [ $WAIT -ge $MAX_WAIT ]; then
    echo "ERROR: Server failed to start within ${MAX_WAIT}s"
    exit 1
  fi
done

echo "=== Environment READY (server on http://localhost:3000) ==="
```

**Key requirements for init.sh:**
- Must be idempotent (safe to run multiple times)
- Must print a clear "READY" signal on success
- Must exit non-zero on failure
- Should take <30 seconds to complete

---

### 2. `features.json` — Structured Task Backlog

**Why JSON over Markdown:**
- Models are less likely to accidentally delete or reorder JSON entries
- Easy to programmatically query which features are incomplete
- Passes/fails status is machine-readable

**Feature entry schema:**
```json
{
  "id": "string (e.g., auth-001)",
  "category": "string (e.g., Authentication, UI, API)",
  "description": "One-sentence description of what the user can do",
  "test_steps": [
    "Step 1: Navigate to...",
    "Step 2: Click...",
    "Step 3: Verify..."
  ],
  "passes": false,
  "priority": 1
}
```

**Feature writing guidelines:**
- Write from the **user's perspective** ("User can X"), not implementation ("Add X function")
- Each feature should be testable in <5 minutes
- Include at least 2–3 test steps per feature
- Start with priority 1 (highest), increment for less critical features
- For a "clone of claude.ai" style prompt, expect 100–200 features minimum

**Example full features.json:**
```json
{
  "project": "Claude.ai Clone",
  "created": "2025-11-26",
  "features": [
    {
      "id": "auth-001",
      "category": "Authentication",
      "description": "User can register with email and password",
      "test_steps": [
        "Navigate to /register",
        "Fill in valid email and password",
        "Click Register button",
        "Verify redirect to /dashboard",
        "Verify welcome email message appears"
      ],
      "passes": false,
      "priority": 1
    },
    {
      "id": "auth-002",
      "category": "Authentication",
      "description": "User can log in with existing credentials",
      "test_steps": [
        "Navigate to /login",
        "Fill in registered email and password",
        "Click Login button",
        "Verify redirect to /dashboard"
      ],
      "passes": false,
      "priority": 1
    },
    {
      "id": "chat-001",
      "category": "Chat",
      "description": "User can start a new conversation",
      "test_steps": [
        "Click 'New Chat' button",
        "Verify empty chat interface appears",
        "Type a message in the input",
        "Press Enter or click Send",
        "Verify message appears in chat"
      ],
      "passes": false,
      "priority": 2
    }
  ]
}
```

---

### 3. `claude-progress.txt` — Session Handoff Log

Initial template to create:
```
# Project: [PROJECT_NAME]
# Created: [DATE]
# Status: IN PROGRESS

## Session Log

### Session 1 (Initializer) — [DATE]
- Set up project scaffold
- Created features.json with [N] features
- Created init.sh
- Initialized git repository
- Features completed: 0 / [N]
- Next session should: Start with auth-001 (highest priority)

## Notes
- Tech stack: [e.g., Next.js, FastAPI, PostgreSQL]
- Port: 3000 (frontend), 8000 (backend)
- Key files: [list any important files]
```

---

### 4. Initial Git Commit

```bash
git init
git add -A
git commit -m "Initial project setup by initializer agent

- Created features.json with [N] requirements
- Created init.sh for environment bootstrap
- Created claude-progress.txt for session tracking
- Ready for coding agent sessions"
```

---

## Prompting the Initializer

Key phrases to include in the initializer prompt:
- "Do NOT implement any features — your job is setup only"
- "Create a comprehensive feature list. For a complex app, aim for 100+ features"
- "Use JSON format for features.json, not Markdown"
- "Test that init.sh actually works before finishing"
- "Make the initial git commit before exiting"
