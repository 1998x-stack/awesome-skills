---
name: playwright-automation
description: >
  Expert-level Playwright browser automation skill for Python. Use this skill whenever
  the user wants to automate web interactions, scrape websites, take screenshots, fill forms,
  test web applications, extract data, interact with SPAs/dynamic pages, handle authentication,
  manage cookies/sessions, intercept network requests, or perform ANY browser automation task.
  Also trigger for: "open a website", "click a button on a page", "log into a site automatically",
  "extract data from a webpage", "automate browser", "web scraping with Python", "browser testing",
  "fetch page content with JavaScript", "fill in a form automatically", "download files from a site".
  This skill provides production-ready Python code patterns with best practices baked in.
compatibility: "Python >=3.8 | pip install playwright && playwright install chromium"
---

# Playwright Automation Skill

## Quick Reference

| Task | Go To |
|------|-------|
| Core API & selectors | `references/core-operations.md` |
| Common patterns (auth, scraping, forms) | `references/patterns.md` |
| Ready-to-run Python toolkit | `scripts/playwright_toolkit.py` |
| Full usage examples | `scripts/examples.py` |

## Installation

```bash
pip install playwright
playwright install chromium   # or: playwright install  (all browsers)
```

## Architecture Decision: Sync vs Async

| Use Sync | Use Async |
|----------|-----------|
| Scripts, one-off tasks, CLI tools | Web servers (FastAPI/Flask), Jupyter, concurrent scraping |
| Simpler code, easier debugging | High-throughput scraping, parallel browser contexts |

```python
# SYNC (default for scripts)
from playwright.sync_api import sync_playwright

# ASYNC (for servers / parallel work)
from playwright.async_api import async_playwright
import asyncio
```

## Core Workflow Template

```python
from playwright.sync_api import sync_playwright, Page, BrowserContext
from pathlib import Path
import json

def run(playwright):
    # 1. Launch browser
    browser = playwright.chromium.launch(
        headless=True,           # False = visible browser
        slow_mo=50,              # ms delay between actions (debugging)
        args=["--no-sandbox"],   # needed in Docker/CI
    )

    # 2. Create context (isolated session with cookies/storage)
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (compatible; MyBot/1.0)",
        locale="en-US",
        timezone_id="America/New_York",
        record_video_dir="videos/",   # optional: record session
        record_har_path="network.har", # optional: capture all network
    )

    # 3. Open page
    page = context.new_page()

    # 4. Do work (see operations below)
    page.goto("https://example.com", wait_until="networkidle")

    # 5. Cleanup
    context.close()
    browser.close()

with sync_playwright() as p:
    run(p)
```

## The 5 Essential Operations

### 1. Screenshot
```python
# Full page
page.screenshot(path="full.png", full_page=True)
# Specific element
page.locator("h1").screenshot(path="header.png")
# With clip
page.screenshot(path="crop.png", clip={"x": 0, "y": 0, "width": 800, "height": 400})
```

### 2. Fetch Page / Extract Content
```python
page.goto("https://example.com")
html   = page.content()                          # full HTML
title  = page.title()
text   = page.locator("body").inner_text()
data   = page.evaluate("() => document.title")  # run JS
links  = page.eval_on_selector_all("a", "els => els.map(e => e.href)")
```

### 3. Form Fill
```python
page.locator("#username").fill("user@example.com")
page.locator("#password").fill("secret123")
page.locator("select#country").select_option("US")
page.locator("input[type=checkbox]").check()
page.locator("input[type=radio][value=yes]").check()
page.locator("input[type=file]").set_input_files("upload.pdf")
page.get_by_role("button", name="Submit").click()
page.wait_for_url("**/dashboard**")
```

### 4. Navigation & Waiting
```python
page.goto(url, wait_until="networkidle")  # domcontentloaded | load | networkidle
page.go_back()
page.reload()
page.wait_for_selector(".results", state="visible", timeout=10000)
page.wait_for_load_state("networkidle")
page.wait_for_function("() => window.dataReady === true")
page.wait_for_timeout(2000)  # hard sleep (avoid in production)
```

### 5. Click & Interact
```python
page.click(".submit-btn")                    # simple click
page.dblclick(".item")                       # double click
page.click(".menu", button="right")         # right click
page.hover(".tooltip-trigger")              # hover
page.drag_and_drop("#src", "#dest")         # drag
page.keyboard.press("Enter")
page.keyboard.type("Hello World")
page.mouse.move(100, 200)
page.mouse.click(100, 200)
```

## Smart Selectors (Priority Order)

```python
# 1. Role-based (most resilient to UI changes)
page.get_by_role("button", name="Submit")
page.get_by_role("textbox", name="Email")
page.get_by_role("link", name="Home")

# 2. Text content
page.get_by_text("Welcome back")
page.get_by_label("Password")
page.get_by_placeholder("Enter email")
page.get_by_alt_text("Company logo")

# 3. Test IDs (best for testing)
page.get_by_test_id("submit-btn")  # data-testid="submit-btn"

# 4. CSS / XPath (fallback)
page.locator("button.primary")
page.locator("//button[contains(text(), 'Submit')]")
```

## Error Handling Pattern

```python
from playwright.sync_api import TimeoutError as PlaywrightTimeout

try:
    page.goto("https://example.com", timeout=30000)
    page.wait_for_selector(".content", timeout=10000)
except PlaywrightTimeout as e:
    print(f"Timeout: {e}")
    page.screenshot(path="error_state.png")
except Exception as e:
    print(f"Error: {e}")
    raise
finally:
    context.close()
    browser.close()
```

## Read Reference Files For:
- **Complex selectors, API deep-dive, network interception, file downloads** → `references/core-operations.md`
- **Authentication flows, scraping patterns, SPA handling, anti-bot bypass** → `references/patterns.md`
- **Complete Python toolkit with all operations** → `scripts/playwright_toolkit.py`
- **Runnable end-to-end examples** → `scripts/examples.py`
