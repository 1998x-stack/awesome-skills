# /llm-wiki:ingest -- Extract knowledge from source materials

Read a source file from raw/ and compile it into structured wiki pages.

## Usage

```
/llm-wiki:ingest <path>          # Process a specific file (relative to raw/)
/llm-wiki:ingest all              # Process all unprocessed files
/llm-wiki:ingest !insight <text>  # Direct insight entry
```

## Format Auto-Routing

1. **!insight mode**: Direct text -> create/update wiki page immediately
2. **Non-markdown** (.pdf/.docx/.pptx/.xlsx/.html/.epub/.csv):
   a. Convert to .md first using markitdown
   b. Then process as markdown
3. **Markdown in raw/qa/**: Q&A clustering mode
   - Parse Q&A pairs from JSONL/markdown
   - Cluster by topic
   - Extract cross-conversation insights
   - Output to `wiki/syntheses/`
4. **Markdown in raw/ (other)**: Entity/concept extraction
   - Identify entities (people, companies, projects, tools) and concepts (theories, methods, algorithms)
   - Create pages in `wiki/entities/` and `wiki/concepts/`
   - Establish relationships via `relates_to`
   - Update `index.md` and `log.md`

## Quality Requirements

Each new page must have:
- Complete frontmatter (all required fields)
- Overview 50-200 chars
- At least 1 source citation
- At least 1 relates_to relationship
- At least 3 [[wikilinks]] in body
