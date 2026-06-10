# /llm-wiki:query -- Search and answer questions

Answer questions using the knowledge base with unified search.

## Usage

```
/llm-wiki:query <question>
```

## Steps

1. **Query rewrite**: Optimize the user's question into search keywords
2. **Unified search**: Run `bash <skill>/scripts/wiki.sh search_wiki "<keywords>" --top 15 --json`
   - BM25 full-text search (jieba-tokenized)
   - Maps topic expansion (best-match topic -> all pages in that topic)
   - Graph 1-hop BFS traversal (seed from BM25 top-5)
   - RRF (Reciprocal Rank Fusion, k=60) to merge results
3. **Read relevant pages**: Read full content of top-N results; note low-confidence pages
4. **Synthesize answer**: Answer in the user's language, cite sources as `来源：[[PageName]]`
5. **Crystallize if valuable**: If answer synthesizes 3+ pages and forms new insight, auto-create `wiki/syntheses/` page
6. **Update last_accessed**: Update `last_accessed` on all cited pages
