"""
playwright_toolkit.py
=====================
Production-ready Playwright toolkit for browser automation.
All core operations in one importable module.

Install:
    pip install playwright
    playwright install chromium

Usage:
    from playwright_toolkit import PlaywrightToolkit
    with PlaywrightToolkit(headless=True) as pw:
        pw.goto("https://example.com")
        pw.screenshot("shot.png")
        html = pw.fetch_page()
        pw.form_fill({"#email": "user@example.com", "#pass": "secret"})
"""

from __future__ import annotations
import json
import time
import base64
import random
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from contextlib import contextmanager
from dataclasses import dataclass, field

from playwright.sync_api import (
    sync_playwright,
    Page,
    BrowserContext,
    Browser,
    Playwright,
    TimeoutError as PlaywrightTimeout,
    Response,
    Download,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ─────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────

@dataclass
class PlaywrightConfig:
    headless: bool = True
    browser_type: str = "chromium"        # chromium | firefox | webkit
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout: int = 30_000                 # default action timeout (ms)
    navigation_timeout: int = 60_000      # navigation timeout (ms)
    slow_mo: int = 0                      # delay between actions (ms)
    user_agent: Optional[str] = None
    locale: str = "en-US"
    timezone: str = "America/New_York"
    accept_downloads: bool = True
    ignore_https_errors: bool = True
    proxy: Optional[Dict] = None          # {"server": "http://..."}
    storage_state: Optional[str] = None  # path to saved auth state
    extra_headers: Dict[str, str] = field(default_factory=dict)
    record_video: bool = False
    record_video_dir: str = "videos/"
    docker_mode: bool = False             # adds --no-sandbox etc.


# ─────────────────────────────────────────────────────────
# Main Toolkit Class
# ─────────────────────────────────────────────────────────

class PlaywrightToolkit:
    """
    Unified Playwright toolkit wrapping all common browser automation tasks.

    Example (context manager):
        with PlaywrightToolkit(headless=False) as pw:
            pw.goto("https://example.com")
            pw.screenshot("home.png", full_page=True)

    Example (manual):
        pw = PlaywrightToolkit(headless=True)
        pw.start()
        pw.goto("https://example.com")
        pw.stop()
    """

    def __init__(self, config: PlaywrightConfig = None, **kwargs):
        self.config = config or PlaywrightConfig(**kwargs)
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    # ── Lifecycle ────────────────────────────────────────

    def start(self) -> "PlaywrightToolkit":
        """Launch browser and create context/page."""
        self._playwright = sync_playwright().start()
        browser_launcher = getattr(self._playwright, self.config.browser_type)

        launch_args = []
        if self.config.docker_mode:
            launch_args = [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--disable-gpu",
            ]

        self._browser = browser_launcher.launch(
            headless=self.config.headless,
            slow_mo=self.config.slow_mo,
            args=launch_args,
            proxy=self.config.proxy,
        )

        ctx_kwargs = dict(
            viewport={"width": self.config.viewport_width, "height": self.config.viewport_height},
            locale=self.config.locale,
            timezone_id=self.config.timezone,
            accept_downloads=self.config.accept_downloads,
            ignore_https_errors=self.config.ignore_https_errors,
            extra_http_headers=self.config.extra_headers,
        )
        if self.config.user_agent:
            ctx_kwargs["user_agent"] = self.config.user_agent
        if self.config.storage_state:
            ctx_kwargs["storage_state"] = self.config.storage_state
        if self.config.record_video:
            ctx_kwargs["record_video_dir"] = self.config.record_video_dir
            ctx_kwargs["record_video_size"] = {
                "width": self.config.viewport_width,
                "height": self.config.viewport_height,
            }

        self._context = self._browser.new_context(**ctx_kwargs)
        self._context.set_default_timeout(self.config.timeout)
        self._context.set_default_navigation_timeout(self.config.navigation_timeout)
        self._page = self._context.new_page()
        logger.info(f"Browser started ({self.config.browser_type}, headless={self.config.headless})")
        return self

    def stop(self):
        """Close all browser resources."""
        try:
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception as e:
            logger.warning(f"Error during stop: {e}")
        logger.info("Browser stopped")

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.stop()

    @property
    def page(self) -> Page:
        if not self._page:
            raise RuntimeError("Toolkit not started. Call start() or use as context manager.")
        return self._page

    # ── Navigation ───────────────────────────────────────

    def goto(
        self,
        url: str,
        wait_until: str = "networkidle",
        timeout: int = None,
    ) -> Response:
        """Navigate to URL. wait_until: commit|domcontentloaded|load|networkidle"""
        logger.info(f"→ {url}")
        return self.page.goto(url, wait_until=wait_until, timeout=timeout or self.config.navigation_timeout)

    def reload(self, wait_until: str = "networkidle"):
        self.page.reload(wait_until=wait_until)

    def go_back(self):
        self.page.go_back()

    def go_forward(self):
        self.page.go_forward()

    @property
    def current_url(self) -> str:
        return self.page.url

    @property
    def title(self) -> str:
        return self.page.title()

    # ── Screenshot ──────────────────────────────────────

    def screenshot(
        self,
        path: str = "screenshot.png",
        full_page: bool = False,
        selector: str = None,
        clip: Dict = None,
        as_bytes: bool = False,
    ) -> Union[Path, bytes]:
        """
        Take screenshot. Options:
        - full_page: capture entire scrollable page
        - selector: screenshot just that element
        - clip: {"x", "y", "width", "height"} dict
        - as_bytes: return bytes instead of saving to file
        """
        kwargs = dict(
            full_page=full_page,
            animations="disabled",
        )
        if clip:
            kwargs["clip"] = clip
        if not as_bytes:
            kwargs["path"] = path

        if selector:
            result = self.page.locator(selector).screenshot(**kwargs)
        else:
            result = self.page.screenshot(**kwargs)

        if as_bytes:
            logger.info(f"Screenshot captured ({len(result)} bytes)")
            return result

        logger.info(f"Screenshot saved → {path}")
        return Path(path)

    def screenshot_b64(self, full_page: bool = False) -> str:
        """Return screenshot as base64-encoded string."""
        data = self.screenshot(as_bytes=True, full_page=full_page)
        return base64.b64encode(data).decode()

    # ── Fetch Page ──────────────────────────────────────

    def fetch_page(self, url: str = None) -> str:
        """Navigate to URL (if given) and return full HTML."""
        if url:
            self.goto(url)
        return self.page.content()

    def get_text(self, selector: str = "body") -> str:
        """Get visible text content of an element."""
        return self.page.locator(selector).inner_text()

    def get_html(self, selector: str = None) -> str:
        """Get innerHTML of element or full page HTML."""
        if selector:
            return self.page.locator(selector).inner_html()
        return self.page.content()

    def get_attribute(self, selector: str, attr: str) -> Optional[str]:
        return self.page.locator(selector).get_attribute(attr)

    def get_all_text(self, selector: str) -> List[str]:
        return self.page.locator(selector).all_inner_texts()

    def get_all_attrs(self, selector: str, attr: str) -> List[str]:
        return self.page.eval_on_selector_all(
            selector, f"els => els.map(e => e.getAttribute('{attr}') || '')"
        )

    def get_links(self) -> List[Dict[str, str]]:
        """Extract all links from current page."""
        return self.page.eval_on_selector_all(
            "a[href]",
            "els => els.map(e => ({text: e.innerText.trim(), href: e.href}))"
        )

    def evaluate(self, script: str, arg: Any = None) -> Any:
        """Run JavaScript and return result."""
        return self.page.evaluate(script, arg) if arg is not None else self.page.evaluate(script)

    # ── Form Fill ────────────────────────────────────────

    def form_fill(self, fields: Dict[str, str], submit_selector: str = None):
        """
        Fill a form with field map: {selector: value}.
        Handles: text inputs, selects, checkboxes, file uploads.

        Example:
            pw.form_fill({
                "#email": "user@example.com",
                "#password": "secret",
                "select#country": {"select": "US"},
                "#agree": {"check": True},
                "input[type=file]": {"file": "doc.pdf"},
            }, submit_selector="button[type=submit]")
        """
        for selector, value in fields.items():
            loc = self.page.locator(selector)

            if isinstance(value, dict):
                action = list(value.keys())[0]
                val = value[action]

                if action == "select":
                    loc.select_option(val)
                elif action == "check":
                    loc.check() if val else loc.uncheck()
                elif action == "file":
                    loc.set_input_files(val)
                elif action == "press":
                    loc.press(val)
            else:
                # Auto-detect input type
                input_type = self.page.eval_on_selector(
                    selector,
                    "el => el.tagName.toLowerCase() + ':' + (el.type || '')"
                ) if self.page.locator(selector).count() else "input:text"

                if "select" in input_type:
                    loc.select_option(str(value))
                elif "checkbox" in input_type or "radio" in input_type:
                    loc.check() if value else loc.uncheck()
                else:
                    loc.fill(str(value))

            logger.debug(f"Filled {selector}")

        if submit_selector:
            self.click(submit_selector)

    # ── Click & Interact ─────────────────────────────────

    def click(
        self,
        selector: str = None,
        text: str = None,
        role: str = None,
        name: str = None,
        force: bool = False,
        timeout: int = None,
    ):
        """
        Click an element. Specify via selector, text content, or ARIA role+name.
        Examples:
            pw.click("#submit")
            pw.click(text="Submit")
            pw.click(role="button", name="Submit")
        """
        if role and name:
            self.page.get_by_role(role, name=name).click(force=force, timeout=timeout)
        elif text:
            self.page.get_by_text(text).click(force=force, timeout=timeout)
        elif selector:
            self.page.click(selector, force=force, timeout=timeout)
        else:
            raise ValueError("Must specify selector, text, or role+name")

    def hover(self, selector: str):
        self.page.hover(selector)

    def type_text(self, selector: str, text: str, delay: int = 50, clear_first: bool = True):
        """Type text with realistic keystroke delays."""
        loc = self.page.locator(selector)
        if clear_first:
            loc.clear()
        loc.type(text, delay=delay)

    def press_key(self, key: str, selector: str = None):
        """Press keyboard key. If selector given, focuses element first."""
        if selector:
            self.page.locator(selector).press(key)
        else:
            self.page.keyboard.press(key)

    def scroll_to(self, selector: str = None, x: int = 0, y: int = 0):
        """Scroll to element or position."""
        if selector:
            self.page.locator(selector).scroll_into_view_if_needed()
        else:
            self.page.evaluate(f"window.scrollTo({x}, {y})")

    def scroll_down(self, amount: int = 500):
        """Scroll down by pixels."""
        self.page.mouse.wheel(0, amount)

    # ── Waiting ──────────────────────────────────────────

    def wait_for(
        self,
        selector: str = None,
        state: str = "visible",
        url_pattern: str = None,
        js_condition: str = None,
        timeout: int = None,
    ):
        """
        Wait for various conditions:
        - selector: wait for element state (visible|hidden|attached|detached)
        - url_pattern: wait for URL to match glob pattern
        - js_condition: wait for JS expression to be truthy
        """
        t = timeout or self.config.timeout
        if selector:
            self.page.wait_for_selector(selector, state=state, timeout=t)
        elif url_pattern:
            self.page.wait_for_url(url_pattern, timeout=t)
        elif js_condition:
            self.page.wait_for_function(js_condition, timeout=t)
        else:
            raise ValueError("Specify selector, url_pattern, or js_condition")

    def sleep(self, ms: int):
        """Hard sleep (avoid in production; prefer wait_for instead)."""
        self.page.wait_for_timeout(ms)

    # ── Network ──────────────────────────────────────────

    def intercept_route(self, pattern: str, handler: Callable):
        """Intercept requests matching pattern."""
        self.page.route(pattern, handler)

    def block_resources(self, types: List[str] = None, patterns: List[str] = None):
        """
        Block resource types or URL patterns for faster loading.
        types: ["image", "stylesheet", "font", "media", "script"]
        patterns: ["*.png", "**google-analytics**"]
        """
        if types:
            self.page.route("**/*", lambda r: (
                r.abort() if r.request.resource_type in types else r.continue_()
            ))
        if patterns:
            for pattern in patterns:
                self.page.route(pattern, lambda r: r.abort())

    def capture_response(self, url_pattern: str, action_fn: Callable) -> Any:
        """Execute action and capture the matching API response as JSON."""
        with self.page.expect_response(url_pattern) as resp_info:
            action_fn()
        return resp_info.value.json()

    def on_response(self, pattern: str, callback: Callable):
        """Register callback for responses matching URL pattern."""
        self.page.on("response", lambda r: callback(r) if pattern in r.url else None)

    # ── Downloads ────────────────────────────────────────

    def download_file(self, trigger_selector: str, save_path: str = None) -> Path:
        """Click element and save the triggered download."""
        with self.page.expect_download() as dl_info:
            self.page.click(trigger_selector)
        dl = dl_info.value
        out = Path(save_path or dl.suggested_filename)
        dl.save_as(str(out))
        logger.info(f"Downloaded → {out}")
        return out

    # ── Auth / Session ───────────────────────────────────

    def save_session(self, path: str = "session.json"):
        """Save cookies + localStorage to file."""
        self._context.storage_state(path=path)
        logger.info(f"Session saved → {path}")

    def load_session(self, path: str = "session.json"):
        """Reload context with saved session (creates new page)."""
        self._context.close()
        self._context = self._browser.new_context(storage_state=path)
        self._page = self._context.new_page()
        logger.info(f"Session loaded ← {path}")

    def add_cookies(self, cookies: List[Dict]):
        self._context.add_cookies(cookies)

    def get_cookies(self) -> List[Dict]:
        return self._context.cookies()

    def clear_cookies(self):
        self._context.clear_cookies()

    # ── PDF ──────────────────────────────────────────────

    def save_as_pdf(
        self,
        path: str = "output.pdf",
        format: str = "A4",
        print_background: bool = True,
        landscape: bool = False,
        margin_mm: int = 15,
    ) -> Path:
        """Save current page as PDF (Chromium only)."""
        m = f"{margin_mm}mm"
        self.page.pdf(
            path=path,
            format=format,
            print_background=print_background,
            landscape=landscape,
            margin={"top": m, "right": m, "bottom": m, "left": m},
        )
        logger.info(f"PDF saved → {path}")
        return Path(path)

    # ── Frames ───────────────────────────────────────────

    def frame(self, name: str = None, url: str = None):
        """Get iframe by name or URL pattern."""
        if name:
            return self.page.frame(name)
        if url:
            return self.page.frame(url=url)
        raise ValueError("Specify name or url")

    def frame_locator(self, selector: str):
        """Get FrameLocator for interacting with iframe contents."""
        return self.page.frame_locator(selector)

    # ── Dialogs ──────────────────────────────────────────

    def auto_accept_dialogs(self, accept: bool = True, input_text: str = None):
        """Automatically accept or dismiss dialogs."""
        def handler(dialog):
            if accept:
                dialog.accept(input_text) if input_text else dialog.accept()
            else:
                dialog.dismiss()
        self.page.on("dialog", handler)

    # ── Tracing ──────────────────────────────────────────

    def start_tracing(self):
        self._context.tracing.start(screenshots=True, snapshots=True, sources=True)

    def stop_tracing(self, path: str = "trace.zip"):
        self._context.tracing.stop(path=path)
        logger.info(f"Trace saved → {path} (view: playwright show-trace {path})")

    # ── Convenience ──────────────────────────────────────

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def is_enabled(self, selector: str) -> bool:
        return self.page.locator(selector).is_enabled()

    def count(self, selector: str) -> int:
        return self.page.locator(selector).count()

    def exists(self, selector: str) -> bool:
        return self.count(selector) > 0

    def extract_table(self, selector: str = "table") -> List[List[str]]:
        """Extract a table as a list of rows."""
        return self.page.evaluate(f"""() => {{
            const table = document.querySelector('{selector}');
            if (!table) return [];
            return Array.from(table.querySelectorAll('tr')).map(row =>
                Array.from(row.querySelectorAll('td, th')).map(cell => cell.innerText.trim())
            );
        }}""")

    def extract_json_from_page(self, variable_name: str = None) -> Any:
        """Extract embedded JSON from page (e.g. window.__INITIAL_STATE__)."""
        if variable_name:
            return self.page.evaluate(f"window.{variable_name}")
        # Try common patterns
        for var in ["__INITIAL_STATE__", "__NEXT_DATA__", "__NUXT__", "__APP_STATE__"]:
            try:
                result = self.page.evaluate(f"window.{var}")
                if result:
                    return result
            except:
                pass
        # Try JSON-LD
        return self.page.evaluate("""() => {
            const el = document.querySelector('script[type="application/ld+json"]');
            return el ? JSON.parse(el.textContent) : null;
        }""")


# ─────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────

def quick_screenshot(url: str, output: str = "screenshot.png", full_page: bool = True) -> Path:
    """One-liner: take screenshot of URL."""
    with PlaywrightToolkit(headless=True) as pw:
        pw.goto(url)
        return pw.screenshot(output, full_page=full_page)


def quick_html(url: str) -> str:
    """One-liner: fetch HTML of URL."""
    with PlaywrightToolkit(headless=True) as pw:
        pw.goto(url)
        return pw.page.content()


def quick_text(url: str) -> str:
    """One-liner: extract visible text from URL."""
    with PlaywrightToolkit(headless=True) as pw:
        pw.goto(url)
        return pw.get_text("body")


def quick_pdf(url: str, output: str = "output.pdf") -> Path:
    """One-liner: save URL as PDF."""
    with PlaywrightToolkit(headless=True) as pw:
        pw.goto(url)
        return pw.save_as_pdf(output)


def batch_screenshot(urls: List[str], output_dir: str = "screenshots") -> List[Path]:
    """Screenshot a list of URLs."""
    out = Path(output_dir)
    out.mkdir(exist_ok=True)
    paths = []

    with PlaywrightToolkit(headless=True) as pw:
        for i, url in enumerate(urls):
            try:
                pw.goto(url)
                p = pw.screenshot(str(out / f"{i:04d}.png"), full_page=True)
                paths.append(p)
                logger.info(f"[{i+1}/{len(urls)}] {url}")
            except Exception as e:
                logger.error(f"Failed {url}: {e}")

    return paths


@contextmanager
def playwright_page(headless: bool = True, **kwargs):
    """Context manager that yields a raw Playwright page."""
    with PlaywrightToolkit(headless=headless, **kwargs) as toolkit:
        yield toolkit.page


# ─────────────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Playwright Toolkit CLI")
    sub = parser.add_subparsers(dest="command")

    # screenshot command
    ss = sub.add_parser("screenshot", help="Take screenshot of URL")
    ss.add_argument("url")
    ss.add_argument("-o", "--output", default="screenshot.png")
    ss.add_argument("--full-page", action="store_true")
    ss.add_argument("--visible", action="store_true", help="Show browser")

    # html command
    ht = sub.add_parser("html", help="Fetch HTML of URL")
    ht.add_argument("url")
    ht.add_argument("-o", "--output", help="Save to file")

    # text command
    tx = sub.add_parser("text", help="Extract text from URL")
    tx.add_argument("url")

    # pdf command
    pdf = sub.add_parser("pdf", help="Save URL as PDF")
    pdf.add_argument("url")
    pdf.add_argument("-o", "--output", default="output.pdf")

    args = parser.parse_args()

    if args.command == "screenshot":
        p = quick_screenshot(args.url, args.output, args.full_page)
        print(f"Saved: {p}")

    elif args.command == "html":
        html = quick_html(args.url)
        if args.output:
            Path(args.output).write_text(html, encoding="utf-8")
            print(f"Saved: {args.output}")
        else:
            print(html)

    elif args.command == "text":
        print(quick_text(args.url))

    elif args.command == "pdf":
        p = quick_pdf(args.url, args.output)
        print(f"Saved: {p}")

    else:
        parser.print_help()
