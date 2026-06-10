#!/usr/bin/env python3
"""Qwen API-powered wiki page extraction.

Usage:
    python3 scripts/qwen_ingest.py --raw <raw_file>
    python3 scripts/qwen_ingest.py --raw <raw_file> --model qwen-plus
    python3 scripts/qwen_ingest.py --raw <raw_file> --context-pages pages.txt
    python3 scripts/qwen_ingest.py --raw <raw_file> --wiki <wiki_file>   (legacy single-page mode)

Reads a raw source file, calls Qwen to extract entities/concepts.
One raw file may produce multiple wiki pages.

Features:
    - Retry with exponential backoff (3 attempts)
    - Input truncation at 100K chars
    - Dedup against existing wiki pages (by title + aliases)
    - Context injection for accurate [[wikilinks]]
    - Pages with YAML errors are included (not skipped) with "errors" field

Output JSON (multi-page mode):
    {"status": "SUCCESS", "has_errors": false, "pages": [
        {"type": "entity", "wiki_name": "...", "markdown": "..."},
        {"type": "concept", "wiki_name": "...", "markdown": "...", "errors": ["..."]},
        {"type": "entity", "wiki_name": "...", "markdown": "...", "existing_path": "wiki/..."}
    ]}
    {"status": "ERROR", "error": "..."}

Legacy mode (--wiki): writes single file, returns flat status (backwards compatible).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path
from typing import Optional

from wiki_utils import VAULT_DIR, WIKI_DIR, parse_frontmatter

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

TODAY = date.today().strftime("%Y-%m-%d")

MAX_CONTENT_CHARS = 100_000
DEFAULT_MODEL = "qwen3.5-plus"
MAX_RETRIES = 3

SYSTEM_PROMPT = """你是一个知识库维护者。你的任务是从源材料中提取所有重要的实体和概念，为每个生成一个结构化的 wiki 页面。

## 关键要求：每个页面必须以 YAML frontmatter 开头

每个页面的第一行必须是 `---`，然后是 YAML 字段，然后是 `---`。没有 frontmatter 的页面会被跳过。这是硬性要求。

## 重要：一个源文件可以产出多个 wiki 页面

仔细阅读源材料，识别其中所有值得独立记录的实体（人物、组织、项目等）和概念（理论、方法、算法等）。每个独立知识点生成一个 wiki 页面。

## 多页面分隔符

使用 `---PAGE_BREAK---` 分隔多个页面。每个页面都是完整的 Markdown，包含 YAML frontmatter。

## 单个页面格式

不要用代码块包裹。每个页面格式如下：

```yaml
---
type: entity | concept
title: "页面标题"
status: active
confidence: 0.0-1.0
created: {today}
updated: {today}
last_accessed: {today}
source_count: 1
tags: []
aliases: []
relates_to:
  - target: "[[相关页面]]"
    type: uses | depends_on | contradicts | caused | extends | implements
    confidence: 0.0-1.0
supersedes: null
---
```

### 正文结构：

# 页面标题

## 概述
50-200 字的简明概述。

## 关键内容
300 字以上的详细内容，分小节组织。

## 来源
- [[raw/路径/文件名]]

## 相关
- [[相关页面1]]
- [[相关页面2]]

## 规则

1. **语言**：中文为主，英文专有名词保留原文
2. **链接**：使用 [[双链]] 引用其他知识页面
3. **type**：人物、组织、项目、工具等用 entity；理论、方法、算法、概念等用 concept
4. **confidence**：根据来源可靠性和信息完整度打分，0.0-1.0
5. **tags**：从以下标签中选择（最多 8 个）：数学、数值分析、概率论、矩阵理论、AI、工具、方法论、研究
6. **aliases**：包含英文名、缩写、常见别名
7. **relates_to**：最多 10 个关系，每个关系包含 target、type、confidence
8. **概述**：必须 50-200 字，高度概括
9. **关键内容**：必须 300 字以上，详细展开
10. **来源**：必须引用原始文件路径
11. **相关**：列出所有 relates_to 中提到的页面""".replace("{today}", TODAY)

# --- Frontmatter required fields ---
REQUIRED_FM_FIELDS = [
    "type",
    "title",
    "status",
    "confidence",
    "created",
    "updated",
    "source_count",
    "tags",
    "aliases",
    "relates_to",
]

CRITICAL_FM_FIELDS = ["type", "title", "confidence"]


def strip_thinking_tags(text: str) -> str:
    """Remove <think>...</think> blocks from Qwen3 responses."""
    return re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL).strip()


def strip_code_block(text: str) -> str:
    """Remove ```markdown ... ``` wrappers and <think> tags from API response."""
    text = strip_thinking_tags(text)
    text = text.strip()
    pattern = r"^```(?:markdown|md|yaml)?\s*\n(.*?)```\s*$"
    m = re.match(pattern, text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text


def lint_page(content: str) -> tuple[list[str], list[str]]:
    """Lint a wiki page. Returns (critical_errors, warnings)."""
    critical = []
    warnings = []

    fm, body = parse_frontmatter(content)

    # Check frontmatter exists
    if fm is None:
        critical.append("YAML frontmatter missing or unparseable")
        return critical, warnings

    # Check required fields
    for field in CRITICAL_FM_FIELDS:
        if field not in fm or fm[field] is None:
            critical.append(f"Critical frontmatter field missing: {field}")

    for field in REQUIRED_FM_FIELDS:
        if field not in fm or fm[field] is None:
            if field not in CRITICAL_FM_FIELDS:
                warnings.append(f"Frontmatter field missing: {field}")

    # Check type value
    if fm.get("type") and fm["type"] not in (
        "entity",
        "concept",
        "synthesis",
        "qa-insight",
        "source-summary",
    ):
        warnings.append(f"Unexpected type value: {fm['type']}")

    # Check confidence range
    conf = fm.get("confidence")
    if conf is not None:
        try:
            c = float(conf)
            if c < 0.0 or c > 1.0:
                warnings.append(f"Confidence out of range: {c}")
        except (TypeError, ValueError):
            warnings.append(f"Confidence not a number: {conf}")

    # Check overview length
    overview_match = re.search(r"## 概述\s*\n(.*?)(?=\n## |\Z)", body, re.DOTALL)
    if overview_match:
        overview_text = overview_match.group(1).strip()
        char_count = len(overview_text)
        if char_count < 20:
            critical.append(f"Overview too short: {char_count} chars (min 50)")
        elif char_count < 50:
            warnings.append(f"Overview short: {char_count} chars (recommended 50-200)")
        elif char_count > 200:
            warnings.append(f"Overview long: {char_count} chars (recommended 50-200)")
    else:
        critical.append("Missing ## 概述 section")

    # Check wikilinks presence
    wikilinks = re.findall(r"\[\[.+?\]\]", body)
    if not wikilinks:
        warnings.append("No [[wikilinks]] found in body")

    # Check for empty key sections
    for section_name in ["概述", "关键内容", "来源", "相关"]:
        section_match = re.search(
            rf"## {section_name}\s*\n(.*?)(?=\n## |\Z)", body, re.DOTALL
        )
        if section_match:
            section_body = section_match.group(1).strip()
            if len(section_body) < 5:
                if section_name in ("概述", "关键内容"):
                    critical.append(f"Section ## {section_name} is empty or too short")
                else:
                    warnings.append(f"Section ## {section_name} is empty or too short")
        else:
            if section_name in ("概述", "关键内容"):
                critical.append(f"Missing ## {section_name} section")
            else:
                warnings.append(f"Missing ## {section_name} section")

    return critical, warnings


def scan_existing_pages() -> dict[str, str]:
    """Scan wiki/ for existing pages. Returns {normalized_name: relative_path}.

    Matches by filename stem and by aliases in frontmatter.
    """
    wiki_dir = WIKI_DIR
    existing = {}
    for fp in wiki_dir.rglob("*.md"):
        if fp.name == ".gitkeep":
            continue
        stem = fp.stem
        rel = str(fp.relative_to(VAULT_DIR))
        existing[stem] = rel
        # Also index aliases from frontmatter
        try:
            text = fp.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            if fm and isinstance(fm.get("aliases"), list):
                for alias in fm["aliases"]:
                    if alias and isinstance(alias, str):
                        existing[alias.strip()] = rel
        except (OSError, UnicodeDecodeError):
            pass
    return existing


def call_qwen(raw_content: str, raw_path: str, model: str = DEFAULT_MODEL) -> str:
    """Call Qwen3-Plus API to extract wiki page from raw content."""
    if OpenAI is None:
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "error": "openai package not installed. Run: pip install openai",
                }
            )
        )
        sys.exit(1)

    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "error": "DASHSCOPE_API_KEY environment variable not set",
                }
            )
        )
        sys.exit(1)

    client = OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=api_key,
    )

    user_message = f"源文件路径：{raw_path}\n\n---\n\n{raw_content}"

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                extra_body={"enable_thinking": False},
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                print(f"Retry {attempt + 1}/{MAX_RETRIES} in {wait}s: {e}", file=sys.stderr)
                time.sleep(wait)
            else:
                print(json.dumps({"status": "ERROR", "error": f"API failed after {MAX_RETRIES} attempts: {e}"}))
                sys.exit(1)


def split_pages(text: str) -> list[str]:
    """Split multi-page response by ---PAGE_BREAK--- delimiter."""
    parts = re.split(r"\n*---PAGE_BREAK---\n*", text)
    return [strip_code_block(p.strip()) for p in parts if p.strip()]


def extract_page_info(content: str) -> dict:
    """Extract type and title from a wiki page's frontmatter."""
    fm, _ = parse_frontmatter(content)
    if fm is None:
        return {"type": "unknown", "wiki_name": "untitled"}
    page_type = fm.get("type", "concept")
    title = fm.get("title", "untitled")
    return {"type": page_type, "wiki_name": title}


def main():
    parser = argparse.ArgumentParser(
        description="Qwen API-powered wiki page extraction"
    )
    parser.add_argument("--raw", required=True, help="Path to raw source file")
    parser.add_argument("--wiki", default=None, help="Path to output wiki file (legacy single-page mode)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Qwen model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--context-pages", default=None, help="File containing existing page names for dedup/linking")
    args = parser.parse_args()

    raw_path = Path(args.raw)
    legacy_mode = args.wiki is not None

    # Validate raw file exists
    if not raw_path.exists():
        print(json.dumps({"status": "ERROR", "error": f"Raw file not found: {raw_path}"}))
        sys.exit(1)

    # Read raw content
    raw_content = raw_path.read_text(encoding="utf-8")
    if not raw_content.strip():
        print(json.dumps({"status": "ERROR", "error": f"Raw file is empty: {raw_path}"}))
        sys.exit(1)

    # Truncate if too large
    truncated = False
    original_len = len(raw_content)
    if original_len > MAX_CONTENT_CHARS:
        raw_content = raw_content[:MAX_CONTENT_CHARS]
        truncated = True
        print(f"Content truncated: {original_len} → {MAX_CONTENT_CHARS} chars", file=sys.stderr)

    # Inject existing page context into prompt if provided
    if args.context_pages:
        ctx_path = Path(args.context_pages)
        if ctx_path.exists():
            ctx_text = ctx_path.read_text(encoding="utf-8").strip()
            if ctx_text:
                raw_content += f"\n\n---\n\n## 已有知识库页面（请使用精确的 [[页面名]] 链接，如果提取的实体与已有页面相同请使用相同标题）\n\n{ctx_text}"

    # Call Qwen API
    response_text = call_qwen(raw_content, str(raw_path), model=args.model)

    # Strip thinking tags from full response before splitting
    response_text = strip_thinking_tags(response_text)

    # Split into pages
    pages_raw = split_pages(response_text)
    if not pages_raw:
        # Fallback: treat entire response as single page
        pages_raw = [strip_code_block(response_text)]

    # --- Legacy mode: single file write (backwards compatible) ---
    if legacy_mode:
        wiki_path = Path(args.wiki)
        content = pages_raw[0]
        critical_errors, warnings = lint_page(content)

        if critical_errors:
            print(json.dumps({
                "status": "ERROR",
                "error": "Lint critical errors — page not written",
                "critical": critical_errors,
                "warnings": warnings,
                "raw_response_preview": content[:500],
            }, ensure_ascii=False))
            sys.exit(1)

        wiki_path.parent.mkdir(parents=True, exist_ok=True)
        wiki_path.write_text(content, encoding="utf-8")

        if warnings:
            print(json.dumps({"status": "LINT_WARNING", "wiki_path": str(wiki_path), "warnings": warnings}, ensure_ascii=False))
        else:
            print(json.dumps({"status": "SUCCESS", "wiki_path": str(wiki_path)}, ensure_ascii=False))
        return

    # --- Multi-page mode: return JSON with all pages ---
    # Scan existing pages for dedup
    existing_pages = scan_existing_pages()

    result_pages = []
    has_errors = False

    for content in pages_raw:
        info = extract_page_info(content)
        critical_errors, warnings = lint_page(content)

        page_entry = {
            "type": info["type"],
            "wiki_name": info["wiki_name"],
            "markdown": content,
        }

        if critical_errors:
            page_entry["errors"] = critical_errors
            has_errors = True
        if warnings:
            page_entry["warnings"] = warnings

        # Dedup: check if page already exists
        wiki_name = info["wiki_name"]
        if wiki_name in existing_pages:
            page_entry["existing_path"] = existing_pages[wiki_name]

        result_pages.append(page_entry)

    if not result_pages:
        print(json.dumps({
            "status": "ERROR",
            "error": "No pages extracted from response",
        }, ensure_ascii=False))
        sys.exit(1)

    output = {
        "status": "SUCCESS",
        "pages": result_pages,
        "has_errors": has_errors,
    }
    if truncated:
        output["truncated_from"] = original_len
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
