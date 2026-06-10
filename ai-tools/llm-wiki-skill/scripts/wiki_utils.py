#!/usr/bin/env python3
"""Shared utilities for wiki scripts.

Canonical implementations of parse_frontmatter, tokenize, stop words, and
path constants. All wiki scripts should import from here instead of
reimplementing these functions.
"""
from __future__ import annotations

import html
import re
import os
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

SKILL_DIR = Path(__file__).resolve().parent.parent  # <skill>/


def discover_wiki_root() -> Path:
    """Find the user's wiki root directory.

    1. LLM_WIKI_ROOT env var (highest priority)
    2. Walk up from CWD looking for .wiki-root marker
    3. Raise if not found
    """
    if env_root := os.environ.get("LLM_WIKI_ROOT"):
        root = Path(env_root)
        if root.is_dir():
            return root
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".wiki-root").exists():
            return parent
    raise RuntimeError(
        "Wiki root not found. Set LLM_WIKI_ROOT or run /llm-wiki:init"
    )


VAULT_DIR = discover_wiki_root()
WIKI_DIR = VAULT_DIR / "wiki"
INDEX_DIR = VAULT_DIR / "index" / "BM25"
MAPS_DIR = VAULT_DIR / "maps"
GRAPH_PATH = VAULT_DIR / "graph.json"
INDEX_FILE = VAULT_DIR / "index.md"

WIKI_SUBDIRS = ["concepts", "entities", "syntheses"]

KEYWORDS_PATH = WIKI_DIR / "keywords.txt"

# ---------------------------------------------------------------------------
# Wikilink regex
# ---------------------------------------------------------------------------

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")

# ---------------------------------------------------------------------------
# Stop words (Chinese + English)
# ---------------------------------------------------------------------------

STOP_WORDS = frozenset([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
    "什么", "可以", "这个", "那个", "如果", "因为", "所以", "但是", "而且",
    "或者", "以及", "还是", "已经", "可能", "应该", "需要", "通过", "进行",
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "and", "or", "but", "if", "for", "of", "in", "on", "at", "to", "from",
    "by", "with", "as", "it", "its", "this", "that", "these", "those",
    "not", "no", "nor", "so", "than", "too", "very",
])

# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


def parse_frontmatter(text: str) -> tuple[Optional[dict], str]:
    """Extract YAML frontmatter and body from markdown text.

    Returns (frontmatter_dict, body_str) or (None, text) if invalid.
    This is the canonical implementation — all scripts should use this.
    """
    if not text.startswith("---"):
        return None, text
    end = text.find("---", 3)
    if end == -1:
        return None, text
    fm_raw = text[3:end].strip()
    body = text[end + 3:].strip()
    if yaml is None:
        # Fallback: simple key-value parse when yaml not installed
        fm = {}
        for line in fm_raw.split("\n"):
            if ":" in line and not line.startswith(" ") and not line.startswith("-"):
                key, val = line.split(":", 1)
                fm[key.strip()] = val.strip()
        return fm, body
    try:
        fm = yaml.safe_load(fm_raw)
        if not isinstance(fm, dict):
            return None, text
        return fm, body
    except yaml.YAMLError:
        return None, text


def strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter, return body only."""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].strip()
    return text


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------


def extract_title(text: str) -> str:
    """Extract title from frontmatter 'title:' field or first '# ' heading."""
    fm, body = parse_frontmatter(text)
    if fm and fm.get("title"):
        return str(fm["title"]).strip().strip('"').strip("'")
    for line in body.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_type(text: str) -> str:
    """Extract type from frontmatter."""
    fm, _ = parse_frontmatter(text)
    if fm and fm.get("type"):
        return str(fm["type"])
    return "unknown"


# ---------------------------------------------------------------------------
# Tokenization (lazy jieba import)
# ---------------------------------------------------------------------------

_jieba = None
_jieba_dict_loaded = False


def _get_jieba():
    global _jieba, _jieba_dict_loaded
    if _jieba is None:
        import jieba
        _jieba = jieba
    if not _jieba_dict_loaded:
        _jieba_dict_loaded = True
        if KEYWORDS_PATH.exists():
            _jieba.load_userdict(str(KEYWORDS_PATH))
    return _jieba


def tokenize(text: str) -> list[str]:
    """Tokenize text with jieba, strip frontmatter/markdown, remove stop words."""
    text = strip_frontmatter(text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"[#*`>|_\-=]", " ", text)
    jieba = _get_jieba()
    tokens = list(jieba.cut_for_search(text))
    return [
        t.strip().lower()
        for t in tokens
        if t.strip() and t.strip().lower() not in STOP_WORDS and len(t.strip()) > 1
    ]


# ---------------------------------------------------------------------------
# Page resolution
# ---------------------------------------------------------------------------


def resolve_page_name(name: str) -> Optional[str]:
    """Find wiki/{subdir}/{name}.md. Return relative path from VAULT_DIR or None."""
    for subdir in WIKI_SUBDIRS:
        candidate = WIKI_DIR / subdir / f"{name}.md"
        if candidate.exists():
            return str(candidate.relative_to(VAULT_DIR))
    return None


def strip_wikilink(s: str) -> str:
    """'[[Foo]]' -> 'Foo', also handles '[[Foo|Bar]]' and bare names."""
    m = re.match(r"^\[\[([^\]|]+)(?:\|[^\]]*)?\]\]$", s)
    return m.group(1) if m else s


# ---------------------------------------------------------------------------
# HTML safety
# ---------------------------------------------------------------------------


def escape_html(text: str) -> str:
    """Escape text for safe insertion into HTML."""
    return html.escape(text, quote=True)
