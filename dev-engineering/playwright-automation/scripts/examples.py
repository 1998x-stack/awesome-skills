"""
examples.py
===========
Runnable end-to-end examples using playwright_toolkit.py.
Each example is a self-contained function demonstrating one pattern.

Run all:   python examples.py
Run one:   python examples.py --example login
"""

from __future__ import annotations
import json
import asyncio
from pathlib import Path
from playwright_toolkit import (
    PlaywrightToolkit, PlaywrightConfig,
    quick_screenshot, quick_html, quick_text, quick_pdf,
    batch_screenshot, playwright_page,
)
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


# ═══════════════════════════════════════════════
# EXAMPLE 1 — Basic Screenshot & HTML Fetch
# ═══════════════════════════════════════════════

def example_basic():
    """Take screenshots and extract content from a webpage."""
    print("\n=== Example 1: Basic Screenshot & Fetch ===")

    # One-liners
    quick_screenshot("https://playwright.dev", "playwright_home.png", full_page=True)
    text = quick_text("https://playwright.dev")
    print(f"Extracted {len(text)} chars of text")

    # Full control
    with PlaywrightToolkit(headless=True) as pw:
        pw.goto("https://example.com")

        # Multiple screenshots
        pw.screenshot("full_page.png", full_page=True)
        pw.screenshot("viewport.png", full_page=False)
        pw.screenshot("header.png", selector="h1")

        # Content extraction
        html   = pw.get_html()
        title  = pw.title
        h1     = pw.get_text("h1")
        links  = pw.get_links()

        print(f"Title: {title}")
        print(f"H1: {h1}")
        print(f"Links: {len(links)}")
        print(f"HTML length: {len(html)}")

        # Table extraction
        table = pw.extract_table("table")
        if table:
            print(f"Table rows: {len(table)}")


# ═══════════════════════════════════════════════
# EXAMPLE 2 — Form Fill & Submit
# ═══════════════════════════════════════════════

def example_form_fill():
    """Fill and submit a web form."""
    print("\n=== Example 2: Form Fill & Submit ===")

    with PlaywrightToolkit(headless=False, slow_mo=100) as pw:
        # Using a public form demo
        pw.goto("https://the-internet.herokuapp.com/login")
        pw.screenshot("before_login.png")

        # Method 1: Using form_fill()
        pw.form_fill({
            "#username": "tomsmith",
            "#password": "SuperSecretPassword!",
        })
        pw.click(role="button", name="Login")

        # Wait for success
        pw.wait_for(selector=".flash.success", timeout=5000)
        pw.screenshot("after_login.png")
        print(f"Login successful! URL: {pw.current_url}")

        # Method 2: Direct locator API
        pw.goto("https://the-internet.herokuapp.com/login")
        pw.page.get_by_label("Username").fill("tomsmith")
        pw.page.get_by_label("Password").fill("SuperSecretPassword!")
        pw.page.get_by_role("button", name="Login").click()
        pw.page.wait_for_url("**/secure")
        print(f"Logged in via locators: {pw.current_url}")


# ═══════════════════════════════════════════════
# EXAMPLE 3 — Web Scraping (Hacker News)
# ═══════════════════════════════════════════════

def example_scraping():
    """Scrape Hacker News front page."""
    print("\n=== Example 3: Web Scraping ===")

    with PlaywrightToolkit(headless=True) as pw:
        pw.goto("https://news.ycombinator.com")

        # Extract all stories
        stories = pw.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.athing')).map(row => {
                const titleEl = row.querySelector('.titleline > a');
                const scoreRow = row.nextElementSibling;
                const score = scoreRow?.querySelector('.score')?.innerText || '0 points';
                const meta = scoreRow?.querySelector('.subline')?.innerText || '';
                return {
                    id: row.id,
                    title: titleEl?.innerText?.trim() || '',
                    url: titleEl?.href || '',
                    score: parseInt(score) || 0,
                    meta: meta,
                };
            });
        }""")

        print(f"Scraped {len(stories)} stories")
        for story in stories[:5]:
            print(f"  [{story['score']:3d}] {story['title'][:60]}")

        # Save to JSON
        Path("hn_stories.json").write_text(json.dumps(stories, indent=2))
        print("Saved to hn_stories.json")


# ═══════════════════════════════════════════════
# EXAMPLE 4 — Network Interception & Mocking
# ═══════════════════════════════════════════════

def example_network():
    """Intercept and mock network requests."""
    print("\n=== Example 4: Network Interception ===")

    with PlaywrightToolkit(headless=True) as pw:
        # Block images/stylesheets for faster loading
        pw.block_resources(types=["image", "stylesheet", "font"])

        # Mock an API endpoint
        mock_data = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}

        pw.page.route("**/api/users", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_data),
        ))

        # Capture API requests
        captured = []
        pw.page.on("response", lambda r: captured.append({
            "url": r.url, "status": r.status
        }) if "ycombinator" in r.url else None)

        pw.goto("https://news.ycombinator.com")
        print(f"Captured {len(captured)} YC responses")

        # Wait for specific response
        # with pw.page.expect_response("**/some-api**") as resp:
        #     pw.click("#load-data")
        # data = resp.value.json()


# ═══════════════════════════════════════════════
# EXAMPLE 5 — PDF Generation
# ═══════════════════════════════════════════════

def example_pdf():
    """Generate PDF from a webpage."""
    print("\n=== Example 5: PDF Generation ===")

    with PlaywrightToolkit(headless=True) as pw:
        pw.goto("https://playwright.dev/python/docs/intro")
        pw.save_as_pdf(
            "playwright_docs.pdf",
            format="A4",
            print_background=True,
            margin_mm=20,
        )
        print("PDF saved: playwright_docs.pdf")


# ═══════════════════════════════════════════════
# EXAMPLE 6 — Session Persistence (Login Once)
# ═══════════════════════════════════════════════

def example_session_persistence():
    """Login once, save session, reuse in future runs."""
    print("\n=== Example 6: Session Persistence ===")

    STATE_FILE = "session_state.json"

    def is_logged_in(pw: PlaywrightToolkit) -> bool:
        """Check if current session is authenticated."""
        pw.goto("https://the-internet.herokuapp.com/secure")
        return "Secure Area" in pw.get_text("h2")

    with PlaywrightToolkit(headless=True) as pw:
        if Path(STATE_FILE).exists():
            print("Loading saved session...")
            pw.load_session(STATE_FILE)
            if is_logged_in(pw):
                print("✓ Session still valid!")
                return

        # Fresh login
        print("Performing fresh login...")
        pw.goto("https://the-internet.herokuapp.com/login")
        pw.form_fill({"#username": "tomsmith", "#password": "SuperSecretPassword!"})
        pw.click(role="button", name="Login")
        pw.wait_for(url_pattern="**/secure")
        pw.save_session(STATE_FILE)
        print(f"✓ Logged in and saved session to {STATE_FILE}")


# ═══════════════════════════════════════════════
# EXAMPLE 7 — Infinite Scroll Scraping
# ═══════════════════════════════════════════════

def example_infinite_scroll():
    """Scrape a page that loads more content on scroll."""
    print("\n=== Example 7: Infinite Scroll ===")

    with PlaywrightToolkit(headless=True) as pw:
        pw.goto("https://quotes.toscrape.com/scroll")
        pw.wait_for(selector=".quote")

        all_quotes = []
        last_count = 0

        for iteration in range(10):  # max 10 scrolls
            quotes = pw.page.evaluate("""() =>
                Array.from(document.querySelectorAll('.quote')).map(q => ({
                    text: q.querySelector('.text')?.innerText || '',
                    author: q.querySelector('.author')?.innerText || '',
                }))
            """)

            all_quotes = quotes  # replace with full list
            print(f"Scroll {iteration+1}: {len(quotes)} quotes loaded")

            if len(quotes) == last_count:
                print("No new content — done!")
                break
            last_count = len(quotes)

            # Scroll and wait
            pw.scroll_down(amount=1000)
            pw.sleep(1500)

        print(f"Total quotes scraped: {len(all_quotes)}")
        Path("quotes.json").write_text(json.dumps(all_quotes, indent=2))


# ═══════════════════════════════════════════════
# EXAMPLE 8 — File Download
# ═══════════════════════════════════════════════

def example_download():
    """Download a file triggered by clicking a button."""
    print("\n=== Example 8: File Download ===")

    with PlaywrightToolkit(headless=True) as pw:
        pw.goto("https://the-internet.herokuapp.com/download")
        links = pw.page.locator("a").all()

        if links:
            # Download first file
            with pw.page.expect_download() as dl_info:
                links[0].click()
            dl = dl_info.value
            out = Path("downloads") / dl.suggested_filename
            out.parent.mkdir(exist_ok=True)
            dl.save_as(str(out))
            print(f"Downloaded: {out} ({out.stat().st_size} bytes)")


# ═══════════════════════════════════════════════
# EXAMPLE 9 — Async Parallel Scraping
# ═══════════════════════════════════════════════

async def _async_scrape(url: str) -> dict:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return {"url": url, "title": await page.title(), "ok": True}
        except Exception as e:
            return {"url": url, "error": str(e), "ok": False}
        finally:
            await browser.close()

async def _async_batch(urls, concurrency=5):
    from playwright.async_api import async_playwright
    sem = asyncio.Semaphore(concurrency)

    async def bounded(url):
        async with sem:
            return await _async_scrape(url)

    return await asyncio.gather(*[bounded(u) for u in urls], return_exceptions=False)

def example_async_parallel():
    """Scrape multiple URLs in parallel using async."""
    print("\n=== Example 9: Async Parallel Scraping ===")

    urls = [
        "https://example.com",
        "https://playwright.dev",
        "https://python.org",
        "https://github.com",
        "https://pypi.org",
    ]

    results = asyncio.run(_async_batch(urls, concurrency=3))
    for r in results:
        status = "✓" if r.get("ok") else "✗"
        print(f"  {status} {r.get('title', r.get('error', '?'))[:50]}")


# ═══════════════════════════════════════════════
# EXAMPLE 10 — Tracing & Debugging
# ═══════════════════════════════════════════════

def example_tracing():
    """Record a trace for debugging (view with playwright show-trace)."""
    print("\n=== Example 10: Tracing ===")

    with PlaywrightToolkit(headless=True) as pw:
        pw.start_tracing()

        pw.goto("https://example.com")
        pw.screenshot("traced_screenshot.png")
        text = pw.get_text("h1")
        print(f"H1: {text}")

        pw.stop_tracing("trace.zip")
        print("View trace: playwright show-trace trace.zip")


# ═══════════════════════════════════════════════
# Runner
# ═══════════════════════════════════════════════

EXAMPLES = {
    "basic": example_basic,
    "form": example_form_fill,
    "scraping": example_scraping,
    "network": example_network,
    "pdf": example_pdf,
    "session": example_session_persistence,
    "scroll": example_infinite_scroll,
    "download": example_download,
    "async": example_async_parallel,
    "trace": example_tracing,
}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Playwright Examples Runner")
    parser.add_argument(
        "--example", "-e",
        choices=list(EXAMPLES.keys()) + ["all"],
        default="basic",
        help="Which example to run"
    )
    args = parser.parse_args()

    if args.example == "all":
        for name, fn in EXAMPLES.items():
            try:
                fn()
            except Exception as e:
                print(f"[{name}] FAILED: {e}")
    else:
        EXAMPLES[args.example]()
