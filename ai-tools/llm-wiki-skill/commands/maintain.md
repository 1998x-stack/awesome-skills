# /llm-wiki:maintain -- Full knowledge base health check and repair

Run the complete maintenance pipeline: check -> lint -> reindex -> build.

## Usage

```
/llm-wiki:maintain
```

## Steps

### 1. Check -- Read-only diagnostics
Run: `bash <skill>/scripts/wiki.sh lint_wiki --json`

9 checks performed:
- F1: Missing required frontmatter fields (error)
- F2: Unparseable YAML frontmatter (error)
- F3: Overview > 200 chars (warning)
- F4: Empty sections (warning)
- B1: Broken [[links]] (warning)
- B2: Page not in BM25 docmap (warning)
- I1: Page not in index.md (warning)
- I2: Stale index entries (warning)
- O1: Orphan pages -- no inbound links (warning)

Exit code 2 if errors exist. Record findings.

### 2. Lint -- Auto-repair
For each fixable issue from Step 1:
- Missing frontmatter fields -> fill defaults (confidence based on source_count)
- Broken [[links]] -> correct if similar page exists, otherwise flag
- Page not in index.md -> auto-add
- Orphan pages -> try to find related pages and add links

Run: `bash <skill>/scripts/wiki.sh snapshot_index --slim`

### 3. Reindex
Run: `bash <skill>/scripts/wiki.sh snapshot_index --slim`
Run: `bash <skill>/scripts/wiki.sh build_maps --json`

Cold-start guard: if wiki pages < 20, skip topic clustering and maps generation.

### 4. Build
Run: `bash <skill>/scripts/wiki.sh build_keywords`
Run: `bash <skill>/scripts/wiki.sh build_graph`

(These are also maintained by hooks -- this is a full rebuild for insurance.)

## Output

```
Maintenance Complete

[1/4] Check -- 0 errors, 3 warnings
[2/4] Lint -- 2 fixed, 1 pending
[3/4] Reindex -- OK (N pages, M topics) | SKIPPED (< 20 pages)
[4/4] Build -- keywords (N entries), graph (N nodes, M edges)
```

## Post-Maintenance

Append to log.md:
```
## [YYYY-MM-DD] maintain
- Check: N errors, M warnings
- Lint: K fixed
- Reindex: OK / SKIPPED
- Build: OK
```
