# Playwright Patterns Reference

## Table of Contents
1. [Authentication Patterns](#1-authentication-patterns)
2. [Web Scraping Patterns](#2-web-scraping-patterns)
3. [SPA & Dynamic Content](#3-spa--dynamic-content)
4. [Anti-Bot & Stealth](#4-anti-bot--stealth)
5. [Pagination & Infinite Scroll](#5-pagination--infinite-scroll)
6. [Multi-Tab Workflows](#6-multi-tab-workflows)
7. [Retry & Resilience](#7-retry--resilience)
8. [Parallel Scraping (Async)](#8-parallel-scraping-async)
9. [CI/CD & Docker](#9-cicd--docker)
10. [Data Pipeline Pattern](#10-data-pipeline-pattern)

---

## 1. Authentication Patterns

### Cookie/Session Persistence (Most Efficient)
```python
from playwright.sync_api import sync_playwright
from pathlib import Path
import json

STATE_FILE = Path("auth_state.json")

def login(page, username, password):
    """Perform login and return cookies."""
    page.goto("https://app.example.com/login")
    page.get_by_label("Email").fill(username)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_url("**/dashboard**", timeout=15000)
    return page.context.storage_state()

def get_authenticated_context(playwright, username, password, browser_type="chromium"):
    browser = getattr(playwright, browser_type).launch(headless=True)

    if STATE_FILE.exists():
        # Reuse saved session
        context = browser.new_context(storage_state=str(STATE_FILE))
        page = context.new_page()
        page.goto("https://app.example.com/dashboard")
        # Validate still logged in
        if "/login" not in page.url:
            return context, page

    # Fresh login
    context = browser.new_context()
    page = context.new_page()
    state = login(page, username, password)
    context.storage_state(path=str(STATE_FILE))
    return context, page

# Usage
with sync_playwright() as p:
    context, page = get_authenticated_context(p, "user@example.com", "password123")
    page.goto("https://app.example.com/reports")
    # ... do work ...
    context.close()
```

### OAuth / SSO Flow
```python
def handle_oauth(page, provider="google"):
    """Handle OAuth popup window."""
    page.goto("https://app.example.com")
    page.click(f"button[data-provider='{provider}']")

    # OAuth opens popup
    with page.expect_popup() as popup_info:
        page.click(".oauth-btn")
    oauth_page = popup_info.value
    oauth_page.wait_for_load_state()

    # Fill OAuth credentials
    oauth_page.fill("#identifierId", "user@gmail.com")
    oauth_page.click("#identifierNext")
    oauth_page.wait_for_selector("#password")
    oauth_page.fill("input[type=password]", "password")
    oauth_page.click("#passwordNext")

    # Wait for redirect back to app
    page.wait_for_url("**/dashboard**", timeout=30000)
```

### Basic Auth
```python
context = browser.new_context(
    http_credentials={"username": "admin", "password": "secret"}
)
# OR via URL
page.goto("https://admin:secret@internal.example.com")
# OR via header
page.set_extra_http_headers({"Authorization": "Basic " + base64.b64encode(b"admin:secret").decode()})
```

### JWT / Bearer Token
```python
# Set before navigation
context = browser.new_context(
    extra_http_headers={"Authorization": f"Bearer {jwt_token}"}
)

# Or intercept requests to inject
def inject_auth(route):
    route.continue_(headers={**route.request.headers, "Authorization": f"Bearer {jwt_token}"})
page.route("**/api/**", inject_auth)
```

---

## 2. Web Scraping Patterns

### Structured Data Extraction
```python
from dataclasses import dataclass
from typing import List
import json

@dataclass
class Product:
    name: str
    price: str
    url: str
    image: str
    rating: float | None

def scrape_products(page, url: str) -> List[Product]:
    page.goto(url, wait_until="networkidle")
    page.wait_for_selector(".product-grid", timeout=10000)

    products = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('.product-card')).map(card => ({
            name:   card.querySelector('.product-name')?.innerText?.trim() || '',
            price:  card.querySelector('.price')?.innerText?.trim() || '',
            url:    card.querySelector('a')?.href || '',
            image:  card.querySelector('img')?.src || '',
            rating: parseFloat(card.querySelector('.rating')?.dataset?.score) || null,
        }));
    }""")

    return [Product(**p) for p in products]
```

### API Interception Scraping (Fastest method)
```python
import json

scraped_data = []

def capture_api_response(response):
    if "/api/products" in response.url and response.status == 200:
        try:
            data = response.json()
            scraped_data.extend(data.get("items", []))
        except:
            pass

page.on("response", capture_api_response)
page.goto("https://shop.example.com/category/electronics")
page.wait_for_load_state("networkidle")
print(f"Captured {len(scraped_data)} items via API")
```

### Screenshot-Based Scraping (for complex layouts)
```python
def capture_section_screenshots(page, url: str, selector: str, output_dir: Path):
    """Screenshot each matching element."""
    output_dir.mkdir(parents=True, exist_ok=True)
    page.goto(url)
    page.wait_for_selector(selector)

    elements = page.locator(selector).all()
    for i, el in enumerate(elements):
        el.scroll_into_view_if_needed()
        el.screenshot(path=output_dir / f"item_{i:04d}.png")

    return len(elements)
```

---

## 3. SPA & Dynamic Content

```python
# React/Vue/Angular apps often need networkidle
page.goto(url, wait_until="networkidle")

# Wait for store/state to populate
page.wait_for_function("""() => {
    const store = window.__REDUX_STORE__ || window.__VUEX_STORE__;
    return store && Object.keys(store.getState?.() || store.state || {}).length > 0;
}""", timeout=10000)

# Wait for React to render
page.wait_for_function("""() => {
    const root = document.getElementById('root');
    return root && root.children.length > 0 && !root.querySelector('.loading');
}""")

# Scroll to trigger lazy loading
def scroll_and_wait(page, times=5):
    """Scroll to trigger lazy-loaded content."""
    for _ in range(times):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1500)
        page.wait_for_load_state("networkidle")

# Wait for XHR/fetch to complete
def wait_for_api_call(page, url_pattern: str, action_fn):
    """Execute action and wait for specific API call."""
    with page.expect_response(url_pattern) as resp_info:
        action_fn()
    return resp_info.value.json()

# Example
data = wait_for_api_call(
    page,
    "**/api/search*",
    lambda: page.fill("#search", "playwright")
)

# Handle client-side routing
def navigate_spa(page, route: str):
    """Navigate SPA without full reload."""
    page.evaluate(f"window.history.pushState({{}}, '', '{route}')")
    page.wait_for_load_state("networkidle")
```

---

## 4. Anti-Bot & Stealth

```python
# playwright-stealth package (install separately)
# pip install playwright-stealth
from playwright_stealth import stealth_sync

context = browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    locale="en-US",
    timezone_id="America/New_York",
)
page = context.new_page()
stealth_sync(page)   # patches navigator, webgl, etc.

# Manual stealth patches
page.add_init_script("""
    // Override webdriver detection
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    // Override plugins
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    // Override languages
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    // Fake chrome object
    window.chrome = { runtime: {} };
""")

# Human-like behavior
import random, time

def human_type(locator, text, min_delay=30, max_delay=120):
    """Type with random delays between keystrokes."""
    locator.click()
    for char in text:
        locator.press(char)
        time.sleep(random.randint(min_delay, max_delay) / 1000)

def random_scroll(page, amount: int = None):
    """Scroll a random amount."""
    amount = amount or random.randint(200, 600)
    page.mouse.wheel(0, amount)
    page.wait_for_timeout(random.randint(300, 800))

def human_move_click(page, selector: str):
    """Move mouse naturally before clicking."""
    box = page.locator(selector).bounding_box()
    # Move to a nearby random point first
    page.mouse.move(box["x"] + random.randint(0, 30),
                    box["y"] + random.randint(0, 30))
    page.wait_for_timeout(random.randint(50, 200))
    page.mouse.move(box["x"] + box["width"] / 2,
                    box["y"] + box["height"] / 2)
    page.mouse.click(box["x"] + box["width"] / 2,
                     box["y"] + box["height"] / 2)

# Proxy rotation
def create_browser_with_proxy(playwright, proxy_url: str):
    return playwright.chromium.launch(
        proxy={"server": proxy_url}
    )

# Random viewport sizes
VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
    {"width": 1280, "height": 720},
]
context = browser.new_context(viewport=random.choice(VIEWPORTS))
```

---

## 5. Pagination & Infinite Scroll

```python
def scrape_paginated(page, base_url: str, extract_fn, max_pages=50):
    """Scrape paginated results."""
    all_data = []
    current_page = 1

    while current_page <= max_pages:
        url = f"{base_url}?page={current_page}"
        page.goto(url, wait_until="networkidle")

        # Check for "no results"
        if page.locator(".no-results").count() > 0:
            break

        data = extract_fn(page)
        if not data:
            break

        all_data.extend(data)
        print(f"Page {current_page}: {len(data)} items")

        # Check for next page button
        next_btn = page.locator("a.next, button[aria-label='Next']")
        if next_btn.count() == 0 or not next_btn.is_enabled():
            break

        current_page += 1

    return all_data

def scrape_infinite_scroll(page, url: str, extract_fn, max_iterations=20):
    """Scrape infinite scroll pages."""
    page.goto(url, wait_until="networkidle")
    all_data = []
    last_count = 0

    for _ in range(max_iterations):
        data = extract_fn(page)
        all_data = data  # or extend if appending

        # Scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Wait for new content
        try:
            page.wait_for_function(
                f"document.querySelectorAll('.item').length > {last_count}",
                timeout=5000
            )
            last_count = page.locator(".item").count()
        except:
            break  # No new content loaded

    return all_data

def click_next_page(page, extract_fn):
    """Scrape with "Load More" / "Next" button clicks."""
    all_data = []

    while True:
        page.wait_for_load_state("networkidle")
        all_data.extend(extract_fn(page))

        load_more = page.locator("button:has-text('Load more'), .load-more")
        if load_more.count() == 0:
            break

        load_more.click()
        page.wait_for_load_state("networkidle")

    return all_data
```

---

## 6. Multi-Tab Workflows

```python
def multi_tab_scraper(context, urls: list) -> list:
    """Open multiple tabs and scrape in sequence."""
    pages = [context.new_page() for _ in urls]
    results = []

    for page, url in zip(pages, urls):
        page.goto(url, wait_until="domcontentloaded")

    for page, url in zip(pages, urls):
        page.wait_for_load_state("networkidle")
        results.append({
            "url": url,
            "title": page.title(),
            "content": page.locator("main").inner_text(),
        })
        page.close()

    return results

# Handle new tab opened by click
def handle_link_in_new_tab(page, context, link_selector: str):
    """Click a link that opens new tab, scrape, return to original."""
    with context.expect_page() as new_page_info:
        page.click(link_selector)
    new_page = new_page_info.value
    new_page.wait_for_load_state("networkidle")

    data = new_page.evaluate("document.title")
    new_page.close()
    return data
```

---

## 7. Retry & Resilience

```python
import time
from functools import wraps
from playwright.sync_api import TimeoutError as PlaywrightTimeout

def retry(max_attempts=3, delay=2, exceptions=(PlaywrightTimeout, Exception)):
    """Decorator for retrying flaky operations."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    print(f"Attempt {attempt+1}/{max_attempts} failed: {e}")
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))  # exponential backoff
            raise last_exc
        return wrapper
    return decorator

@retry(max_attempts=3)
def scrape_page(page, url):
    page.goto(url, timeout=30000)
    page.wait_for_selector(".content", timeout=10000)
    return page.locator(".content").inner_text()

# Resilient navigation helper
def safe_goto(page, url, retries=3, **kwargs):
    for i in range(retries):
        try:
            response = page.goto(url, timeout=30000, **kwargs)
            if response and response.ok:
                return response
        except PlaywrightTimeout:
            if i == retries - 1:
                raise
            page.reload()
    return None

# Screenshot on failure
def with_screenshot_on_error(page, operation_fn, screenshot_path="error.png"):
    try:
        return operation_fn()
    except Exception as e:
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Error screenshot saved to {screenshot_path}")
        raise
```

---

## 8. Parallel Scraping (Async)

```python
import asyncio
from playwright.async_api import async_playwright
from typing import List

async def scrape_url(context, url: str) -> dict:
    """Scrape a single URL in an async context."""
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_load_state("networkidle", timeout=10000)
        return {
            "url": url,
            "title": await page.title(),
            "html": await page.content(),
            "text": await page.locator("body").inner_text(),
        }
    except Exception as e:
        return {"url": url, "error": str(e)}
    finally:
        await page.close()

async def scrape_all(urls: List[str], concurrency: int = 5) -> List[dict]:
    """Scrape multiple URLs in parallel."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Semaphore to limit concurrency
        sem = asyncio.Semaphore(concurrency)

        async def bounded_scrape(url):
            async with sem:
                return await scrape_url(context, url)

        results = await asyncio.gather(
            *[bounded_scrape(url) for url in urls],
            return_exceptions=True
        )

        await context.close()
        await browser.close()
        return list(results)

# Run it
if __name__ == "__main__":
    urls = [f"https://example.com/page/{i}" for i in range(1, 51)]
    results = asyncio.run(scrape_all(urls, concurrency=10))
    print(f"Scraped {len(results)} pages")
```

---

## 9. CI/CD & Docker

### Dockerfile
```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "scraper.py"]
```

### requirements.txt
```
playwright>=1.40.0
playwright-stealth>=1.0.6
```

### GitHub Actions
```yaml
name: Playwright Scraper
on: [push, schedule: [{cron: "0 8 * * *"}]]

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11"}
      - run: pip install playwright && playwright install chromium --with-deps
      - run: python scraper.py
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: screenshots
          path: "*.png"
```

### Headless server flags
```python
browser = playwright.chromium.launch(
    headless=True,
    args=[
        "--no-sandbox",               # Required for non-root Docker
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",    # /dev/shm too small in Docker
        "--disable-accelerated-2d-canvas",
        "--no-first-run",
        "--no-zygote",
        "--disable-gpu",
    ]
)
```

---

## 10. Data Pipeline Pattern

```python
"""
Complete scraping pipeline: crawl → extract → transform → save
"""
import csv
import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class ScrapedItem:
    url: str
    title: str
    data: dict
    scraped_at: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.utcnow().isoformat()

class PlaywrightPipeline:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.items: List[ScrapedItem] = []

    def extract(self, page: Page, url: str) -> ScrapedItem:
        """Override this method for your specific site."""
        page.goto(url, wait_until="networkidle")
        return ScrapedItem(
            url=url,
            title=page.title(),
            data={"text": page.locator("body").inner_text()[:500]},
        )

    def run(self, urls: List[str]):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            for i, url in enumerate(urls, 1):
                print(f"[{i}/{len(urls)}] {url}")
                try:
                    item = self.extract(page, url)
                    self.items.append(item)
                except Exception as e:
                    print(f"  ERROR: {e}")

            context.close()
            browser.close()

        self.save()
        return self.items

    def save(self):
        # JSON
        json_path = self.output_dir / "results.json"
        json_path.write_text(json.dumps([asdict(i) for i in self.items], indent=2, ensure_ascii=False))

        # CSV
        if self.items:
            csv_path = self.output_dir / "results.csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=asdict(self.items[0]).keys())
                writer.writeheader()
                writer.writerows([asdict(i) for i in self.items])

        print(f"Saved {len(self.items)} items to {self.output_dir}/")

# Usage
class MyPipeline(PlaywrightPipeline):
    def extract(self, page, url):
        page.goto(url, wait_until="networkidle")
        return ScrapedItem(
            url=url,
            title=page.title(),
            data={
                "price": page.locator(".price").inner_text() if page.locator(".price").count() else None,
                "description": page.locator(".description").inner_text() if page.locator(".description").count() else None,
            }
        )

if __name__ == "__main__":
    pipeline = MyPipeline()
    results = pipeline.run(["https://example.com/product/1", "https://example.com/product/2"])
```
