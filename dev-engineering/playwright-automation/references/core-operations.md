# Playwright Core Operations Reference

## Table of Contents
1. [Browser & Context Management](#1-browser--context-management)
2. [Navigation](#2-navigation)
3. [Selectors & Locators](#3-selectors--locators)
4. [Screenshots & Visual Capture](#4-screenshots--visual-capture)
5. [Page Content Extraction](#5-page-content-extraction)
6. [Form Interactions](#6-form-interactions)
7. [Mouse & Keyboard](#7-mouse--keyboard)
8. [Network Interception](#8-network-interception)
9. [File Handling](#9-file-handling)
10. [JavaScript Execution](#10-javascript-execution)
11. [Frames & Popups](#11-frames--popups)
12. [Cookies & Storage](#12-cookies--storage)
13. [Waiting Strategies](#13-waiting-strategies)
14. [PDF Generation](#14-pdf-generation)
15. [Mobile Emulation](#15-mobile-emulation)
16. [Video & HAR Recording](#16-video--har-recording)

---

## 1. Browser & Context Management

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Browser types
    browser = p.chromium.launch(headless=True)   # Chrome/Edge
    browser = p.firefox.launch(headless=True)    # Firefox
    browser = p.webkit.launch(headless=True)     # Safari

    # Launch options
    browser = p.chromium.launch(
        headless=False,              # Show browser
        slow_mo=100,                 # Slow down for debugging
        devtools=True,               # Open devtools
        proxy={                      # HTTP proxy
            "server": "http://proxy:8080",
            "username": "user",
            "password": "pass"
        },
        args=[
            "--no-sandbox",          # Required in Docker
            "--disable-gpu",         # Headless stability
            "--disable-dev-shm-usage",
            "--window-size=1920,1080",
        ],
        executable_path="/usr/bin/chromium",  # Custom binary
        channel="chrome",            # Use installed Chrome: "chrome", "msedge"
        timeout=30000,               # Launch timeout ms
    )

    # Persistent context (saves login across runs)
    context = p.chromium.launch_persistent_context(
        user_data_dir="/tmp/playwright-profile",
        headless=False,
    )

    # Isolated context (fresh session per run)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        device_scale_factor=2,       # Retina/HiDPI
        is_mobile=False,
        has_touch=False,
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
        geolocation={"latitude": 31.2, "longitude": 121.5},
        permissions=["geolocation", "notifications"],
        color_scheme="dark",         # "light" | "dark" | "no-preference"
        http_credentials={"username": "admin", "password": "secret"},
        accept_downloads=True,
        ignore_https_errors=True,    # Bypass SSL errors
        extra_http_headers={"Authorization": "Bearer token123"},
        offline=False,               # Simulate offline
        java_script_enabled=True,
        bypass_csp=True,             # Bypass Content-Security-Policy
    )

    page = context.new_page()
    # ... do work ...
    context.close()
    browser.close()
```

---

## 2. Navigation

```python
# Basic navigation
response = page.goto("https://example.com")
print(response.status)            # HTTP status code
print(response.url)               # Final URL (after redirects)
print(response.ok)                # True if 200-299

# wait_until options:
# "commit"          - response received, body not yet received
# "domcontentloaded"- HTML parsed, no external resources
# "load"            - page fully loaded (including images)
# "networkidle"     - no network requests for 500ms (for SPAs)
page.goto(url, wait_until="networkidle", timeout=60000)

# Other navigation
page.go_back()
page.go_forward()
page.reload(wait_until="networkidle")

# Current state
print(page.url)
print(page.title())

# Wait for navigation after action
with page.expect_navigation(url="**/dashboard**"):
    page.click("#login-btn")

# Wait for navigation with pattern
page.wait_for_url("https://example.com/*/profile", timeout=5000)
```

---

## 3. Selectors & Locators

### Locator API (preferred — lazy, auto-waiting)
```python
# Role-based (most resilient)
page.get_by_role("button", name="Submit")
page.get_by_role("heading", name="Welcome", level=1)
page.get_by_role("link", name="Sign in")
page.get_by_role("checkbox", name="Remember me")
page.get_by_role("combobox")        # <select>
page.get_by_role("textbox")         # <input type=text> / <textarea>
page.get_by_role("img", name="Logo")
page.get_by_role("dialog")

# Text
page.get_by_text("Hello World")               # exact=False by default
page.get_by_text("Hello World", exact=True)
page.get_by_placeholder("Enter your email")
page.get_by_label("Password")
page.get_by_alt_text("Profile picture")
page.get_by_title("Close dialog")
page.get_by_test_id("submit-button")  # data-testid attribute

# CSS / XPath
page.locator("button.primary")
page.locator("#submit")
page.locator("[data-id='123']")
page.locator("//div[@class='content']")
page.locator("text=Click me")
page.locator(":has-text('Submit')")

# Combining
page.locator("form").get_by_role("button", name="Submit")   # scoped
page.locator("tr").filter(has_text="John").locator("td:last-child")
page.locator("li").nth(0)           # first item
page.locator("li").last            # last item
page.locator("li").first           # first item

# Multiple elements
items = page.locator(".item").all()
count = page.locator(".item").count()
for item in page.locator("tr").all():
    print(item.inner_text())
```

### Old-style $ selectors (still works)
```python
el = page.query_selector("button.primary")   # returns None if not found
el.click()

els = page.query_selector_all("a.link")
for el in els:
    print(el.get_attribute("href"))
```

---

## 4. Screenshots & Visual Capture

```python
# Full page screenshot
page.screenshot(
    path="screenshot.png",
    full_page=True,
    type="png",           # "png" | "jpeg"
    quality=90,           # JPEG only, 0-100
    omit_background=True, # transparent background (PNG only)
    animations="disabled",# freeze CSS animations
    timeout=30000,
)

# Viewport only (default)
page.screenshot(path="viewport.png", full_page=False)

# Clip region
page.screenshot(path="section.png", clip={
    "x": 100, "y": 200, "width": 800, "height": 600
})

# Element screenshot
page.locator("#hero-section").screenshot(path="hero.png")

# Screenshot as bytes (no file)
img_bytes = page.screenshot()   # returns bytes
import base64
img_b64 = base64.b64encode(img_bytes).decode()

# Screenshot comparison (pixel diff)
# Use pytest-playwright for this:
# assert_snapshot(page.screenshot(), name="homepage.png")
```

---

## 5. Page Content Extraction

```python
# HTML
full_html = page.content()                         # complete page HTML
inner_html = page.locator(".container").inner_html()  # element innerHTML

# Text
all_text = page.locator("body").inner_text()           # visible text, newlines preserved
text      = page.locator("h1").text_content()          # raw text content (incl hidden)
trimmed   = page.locator("span").inner_text().strip()

# Attributes
href  = page.locator("a.nav").get_attribute("href")
src   = page.locator("img").get_attribute("src")
value = page.locator("input").input_value()

# Evaluate JavaScript for complex extraction
title    = page.evaluate("document.title")
all_hrefs = page.evaluate("Array.from(document.querySelectorAll('a')).map(a => a.href)")
meta_desc = page.evaluate("document.querySelector('meta[name=description]')?.content")
json_data = page.evaluate("() => window.__INITIAL_STATE__")  # embedded JSON state

# Extract table data
table_data = page.evaluate("""() => {
    const rows = Array.from(document.querySelectorAll('table tr'));
    return rows.map(row =>
        Array.from(row.querySelectorAll('td, th')).map(cell => cell.innerText.trim())
    );
}""")

# All links
links = page.eval_on_selector_all("a[href]", "els => els.map(e => ({text: e.innerText, href: e.href}))")

# Wait for element and extract
page.wait_for_selector(".price")
price = page.locator(".price").inner_text()

# Extract from multiple matching elements
texts = page.locator(".item-name").all_inner_texts()   # list of strings
attrs = page.locator("img").evaluate_all("imgs => imgs.map(i => i.src)")
```

---

## 6. Form Interactions

```python
# Text inputs
page.locator("#email").fill("user@example.com")    # clears then fills
page.locator("#email").type("typed slowly")         # simulates keystrokes
page.locator("#email").clear()                      # clear only

# Pressing keys
page.locator("#search").press("Enter")
page.locator("#search").press("Control+a")
page.locator("#search").press("Backspace")

# Select / Dropdown
page.locator("select#country").select_option("US")           # by value
page.locator("select#country").select_option(label="China")  # by label
page.locator("select#country").select_option(index=2)        # by index
page.locator("select#multi").select_option(["a", "b"])       # multi-select

# Checkboxes / Radio
page.locator("#agree").check()
page.locator("#agree").uncheck()
page.locator("#agree").set_checked(True)
page.locator("input[value='male']").check()

# File upload
page.locator("input[type=file]").set_input_files("document.pdf")
page.locator("input[type=file]").set_input_files(["file1.jpg", "file2.jpg"])
page.locator("input[type=file]").set_input_files([])  # clear

# Rich text editors (contenteditable)
page.locator("[contenteditable]").click()
page.keyboard.type("Hello from Playwright!")

# Custom dropdowns (not <select>)
page.click(".dropdown-toggle")
page.wait_for_selector(".dropdown-menu", state="visible")
page.click(".dropdown-menu li[data-value='option2']")

# Form submission
page.get_by_role("button", name="Submit").click()
# OR
page.locator("form").evaluate("form => form.submit()")
```

---

## 7. Mouse & Keyboard

```python
# Click variants
page.click(selector)
page.click(selector, button="right")       # right-click
page.click(selector, button="middle")      # middle-click
page.dblclick(selector)
page.click(selector, click_count=3)        # triple-click (select all text)
page.click(selector, modifiers=["Shift"])  # shift+click
page.click(selector, modifiers=["Control"]) # ctrl+click
page.click(selector, force=True)           # bypass actionability checks
page.click(selector, position={"x": 10, "y": 10})  # click offset
page.click(selector, delay=100)            # hold delay ms

# Hover
page.hover(".tooltip-trigger")
page.hover(selector, position={"x": 50, "y": 50})

# Drag and drop
page.drag_and_drop("#source", "#target")
page.drag_and_drop("#source", "#target",
    source_position={"x": 10, "y": 10},
    target_position={"x": 50, "y": 50}
)

# Low-level mouse
page.mouse.move(100, 200)
page.mouse.down()
page.mouse.move(300, 400)
page.mouse.up()
page.mouse.click(x=100, y=200, button="right")
page.mouse.dblclick(x=100, y=200)
page.mouse.wheel(delta_x=0, delta_y=300)  # scroll

# Keyboard
page.keyboard.press("Tab")
page.keyboard.press("Escape")
page.keyboard.press("Control+c")
page.keyboard.press("Meta+a")       # Cmd+A on Mac
page.keyboard.press("F5")
page.keyboard.down("Shift")
page.keyboard.press("ArrowDown")
page.keyboard.up("Shift")
page.keyboard.type("Hello World", delay=50)   # with keystroke delay
page.keyboard.insert_text("Paste text directly")  # no events
```

---

## 8. Network Interception

```python
# Abort requests (block ads/trackers)
page.route("**/*.{png,jpg,gif,svg}", lambda route: route.abort())
page.route("**/google-analytics.com/**", lambda route: route.abort())

# Mock API responses
def mock_api(route):
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps({"users": [{"id": 1, "name": "Alice"}]}),
        headers={"X-Custom": "mocked"},
    )
page.route("**/api/users", mock_api)

# Modify requests
def modify_request(route):
    route.continue_(
        headers={**route.request.headers, "Authorization": "Bearer token"},
        url=route.request.url.replace("v1", "v2"),
    )
page.route("**/api/**", modify_request)

# Intercept and capture responses
with page.expect_response("**/api/data") as resp_info:
    page.click("#load-data")
response = resp_info.value
print(response.status)
data = response.json()

# Capture all requests/responses
page.on("request", lambda req: print(f">> {req.method} {req.url}"))
page.on("response", lambda resp: print(f"<< {resp.status} {resp.url}"))
page.on("requestfailed", lambda req: print(f"FAILED: {req.url}"))

# Wait for specific response
with page.expect_response(lambda r: r.url.endswith("/data") and r.status == 200) as resp_info:
    page.click("#refresh")
data = resp_info.value.json()

# HAR capture (all network traffic)
context = browser.new_context(record_har_path="network.har")
```

---

## 9. File Handling

```python
# File upload
page.locator("input[type=file]").set_input_files("report.pdf")

# File download
with page.expect_download() as dl_info:
    page.click("#download-btn")
download = dl_info.value
print(download.suggested_filename)
download.save_as(f"/downloads/{download.suggested_filename}")

# Download URL directly
with page.expect_download() as dl_info:
    page.goto("https://example.com/file.xlsx")
download = dl_info.value
download.save_as("output.xlsx")

# Check download failure
download = dl_info.value
print(download.failure())  # None if success, error string if failed

# Multiple file download
downloads = []
page.on("download", lambda d: downloads.append(d))
# ... trigger multiple downloads ...
for d in downloads:
    d.save_as(d.suggested_filename)
```

---

## 10. JavaScript Execution

```python
# Evaluate (returns serializable value)
result = page.evaluate("1 + 2")                        # 3
result = page.evaluate("window.location.href")         # URL string
result = page.evaluate("() => ({ a: 1, b: 2 })")      # dict
result = page.evaluate("document.querySelectorAll('a').length")

# Pass Python values into JS
result = page.evaluate("x => x * 2", 21)              # 42
result = page.evaluate("({a, b}) => a + b", {"a": 1, "b": 2})

# Evaluate on element
el = page.locator("h1")
text = el.evaluate("node => node.textContent")
el.evaluate("node => node.style.color = 'red'")

# evaluate_handle (returns JSHandle for non-serializable objects)
window_handle = page.evaluate_handle("window")
body_handle   = page.evaluate_handle("document.body")

# Add script to every page
page.add_script_tag(content="window.myVar = 42;")
page.add_script_tag(url="https://cdn.example.com/lib.js")
page.add_init_script("window.__TESTING__ = true")  # runs before page JS

# Expose Python function to JS
def my_python_func(arg):
    print(f"Called from JS with: {arg}")
    return "Python result"
page.expose_function("myFunc", my_python_func)
# In JS: const result = await myFunc("hello")
```

---

## 11. Frames & Popups

```python
# Iframes
frame = page.frame("frame-name")                      # by name attribute
frame = page.frame_locator("#frame-id").locator("button")  # frame locator
frame = page.frames[1]                                 # by index
frame = page.frame(url="**/iframe-src**")             # by URL

# Work with frame content
frame.fill("#input", "value")
frame.click("button")
text = frame.locator("h1").inner_text()

# Nested iframes
inner = page.frame_locator("#outer").frame_locator("#inner")
inner.locator("button").click()

# Popups / new tabs
with page.expect_popup() as popup_info:
    page.click("a[target=_blank]")
popup = popup_info.value
popup.wait_for_load_state()
print(popup.title())
popup.close()

# New page in same context
new_page = context.new_page()
new_page.goto("https://other-site.com")
context.pages   # list of all open pages

# Dialog handling
page.on("dialog", lambda dialog: dialog.accept())
page.on("dialog", lambda dialog: dialog.dismiss())
page.on("dialog", lambda dialog: (print(dialog.message), dialog.accept("input_text")))
```

---

## 12. Cookies & Storage

```python
# Cookies
cookies = context.cookies()                            # all cookies
cookies = context.cookies(["https://example.com"])    # for URL

context.add_cookies([{
    "name": "session",
    "value": "abc123",
    "domain": ".example.com",
    "path": "/",
    "httpOnly": True,
    "secure": True,
    "sameSite": "Lax",
}])

context.clear_cookies()

# Save and restore cookies (persist login)
import json
cookies = context.cookies()
Path("cookies.json").write_text(json.dumps(cookies))

# Restore
cookies = json.loads(Path("cookies.json").read_text())
context.add_cookies(cookies)

# Local/Session Storage
page.evaluate("localStorage.setItem('key', 'value')")
value = page.evaluate("localStorage.getItem('key')")
page.evaluate("localStorage.clear()")

# Storage state (cookies + localStorage in one)
storage = context.storage_state()            # dict
context.storage_state(path="state.json")    # save to file

# Launch with pre-loaded state
context = browser.new_context(storage_state="state.json")
```

---

## 13. Waiting Strategies

```python
# Selector states
page.wait_for_selector(".results", state="visible")   # default
page.wait_for_selector(".spinner", state="hidden")
page.wait_for_selector(".item", state="attached")     # in DOM
page.wait_for_selector(".item", state="detached")     # removed from DOM
page.wait_for_selector(".item", timeout=10000)        # ms

# Load states
page.wait_for_load_state("load")
page.wait_for_load_state("domcontentloaded")
page.wait_for_load_state("networkidle")

# URL change
page.wait_for_url("**/success**")
page.wait_for_url(re.compile(r"/order/\d+"))

# JS condition
page.wait_for_function("() => document.readyState === 'complete'")
page.wait_for_function("count => document.querySelectorAll('.item').length >= count", 5)

# Network request
with page.expect_request("**/api/submit") as req_info:
    page.click("#submit")
request = req_info.value

# Hard timeout (last resort)
page.wait_for_timeout(3000)

# Auto-waiting: locators auto-wait before action
page.locator(".btn").click()  # waits up to 30s for element to be visible+stable

# Set default timeouts
page.set_default_timeout(30000)           # all operations
page.set_default_navigation_timeout(60000) # navigation only
```

---

## 14. PDF Generation

```python
# Only works in Chromium headless
page.goto("https://example.com")
page.pdf(
    path="output.pdf",
    format="A4",            # "Letter", "Legal", "A4", etc.
    landscape=False,
    print_background=True,  # include background colors/images
    margin={
        "top": "20mm",
        "right": "15mm",
        "bottom": "20mm",
        "left": "15mm",
    },
    scale=1.0,              # 0.1 - 2
    width="210mm",          # overrides format
    height="297mm",
    page_ranges="1-5",      # "1-5, 8, 11-13"
    header_template="<span class='title'></span>",
    footer_template="<span class='pageNumber'></span> of <span class='totalPages'></span>",
    display_header_footer=True,
)
```

---

## 15. Mobile Emulation

```python
# Use built-in devices
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    iphone = p.devices["iPhone 13"]
    context = p.chromium.launch().new_context(**iphone)
    page = context.new_page()
    page.goto("https://example.com")
    page.screenshot(path="mobile.png")

# Available devices (partial list)
# "iPhone 13", "iPhone 13 Pro Max", "iPad Pro"
# "Pixel 5", "Galaxy S8", "Nexus 10"
# All: p.devices  (dict of all devices)

# Custom mobile
context = browser.new_context(
    viewport={"width": 390, "height": 844},
    device_scale_factor=3,
    is_mobile=True,
    has_touch=True,
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)...",
)

# Touch events
page.tap(".button")                       # tap (touch)
page.locator(".item").tap()
```

---

## 16. Video & HAR Recording

```python
# Record video of session
context = browser.new_context(
    record_video_dir="videos/",
    record_video_size={"width": 1280, "height": 720},
)
page = context.new_page()
# ... actions ...
context.close()  # video saved after close
video_path = page.video.path()   # get video path

# Record HAR (HTTP Archive)
context = browser.new_context(record_har_path="session.har")
page = context.new_page()
# ... actions ...
context.close()  # HAR saved after close

# Or save HAR manually
page.route_from_har("session.har")   # replay from HAR

# Tracing (detailed timeline for debugging)
context.tracing.start(screenshots=True, snapshots=True, sources=True)
# ... actions ...
context.tracing.stop(path="trace.zip")
# View: playwright show-trace trace.zip
```
