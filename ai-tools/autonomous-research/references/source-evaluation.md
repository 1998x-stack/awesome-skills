# Source Evaluation Framework

How to assess whether a source is worth including in the research artifact. Use this framework when you encounter sources of uncertain quality or when researching topics where misinformation is common.

---

## The CRAAP Test (Adapted for AI Research)

Evaluate each source across five dimensions. A source doesn't need to score perfectly on all — the weights depend on the research type.

### Currency (Recency)

| Signal | Score |
|--------|-------|
| Published within the user's recency window | Strong |
| Published within 2x the recency window | Acceptable if foundational |
| Older but seminal/foundational | Acceptable with explicit dating |
| Outdated and superseded | Discard |

**For fast-moving fields** (AI, crypto, policy): weight currency heavily. A 2023 article about LLM capabilities may be outdated by 2025.

**For stable fields** (mathematics, established engineering): currency matters less. A 2015 textbook on distributed systems is still relevant.

### Relevance (Fit to Research Questions)

| Signal | Score |
|--------|-------|
| Directly answers a research question | Keep |
| Provides useful context or background | Keep if depth allows |
| Tangentially related, interesting but off-topic | Discard (note in log) |
| Completely unrelated (search noise) | Discard |

The key test: **if you removed this source, would the research artifact lose something important?** If no, discard.

### Authority (Source Credibility)

| Source Type | Default Trust | Notes |
|-------------|---------------|-------|
| Peer-reviewed journal | High | Check journal reputation, retraction status |
| Official documentation | High | For technical topics |
| Established news organization | Medium-High | Check for corrections |
| University/research institution | Medium-High | Check if it's the institution or a student blog |
| Named expert's personal blog | Medium | Verify expertise via publications/role |
| Company engineering blog | Medium | May have vendor bias, but often high-quality |
| Industry report (Gartner, etc.) | Medium | Methodology sometimes opaque |
| Wikipedia | Medium | Good for overview/links, not primary citation |
| Anonymous blog post | Low | Need corroboration |
| Social media post | Low | Only for attributed quotes or announcements |
| SEO content farm | Very Low | Usually discard |
| AI-generated content (unverified) | Very Low | Circular citations risk |

### Accuracy (Evidence Quality)

| Signal | Score |
|--------|-------|
| Claims backed by data, citations, or methodology | Strong |
| Claims backed by logical argument without data | Acceptable |
| Claims without evidence ("studies show" with no citation) | Weak — need corroboration |
| Claims contradicted by other credible sources | Flag the conflict |
| Obvious factual errors detected | Discard |

### Purpose (Objectivity)

| Signal | Score |
|--------|-------|
| Informational / educational intent | Neutral — trust |
| Analysis with disclosed methodology | Neutral — trust |
| Advocacy with transparent position | Use with disclosure |
| Marketing / promotional content | Use with heavy skepticism |
| Comparison published by a competitor | Note bias explicitly |

---

## Quick Decision Matrix

For each source, run through this checklist:

```
[ ] Does it answer one of my research questions? → No = Discard
[ ] Is it current enough for this research? → No = Discard (unless foundational)
[ ] Can I identify and verify the author/org? → No = Need corroboration
[ ] Are claims supported by evidence? → No = Need corroboration
[ ] Is there an obvious commercial interest? → Yes = Note bias
```

If a source passes the first two checks, it's worth reading. If it passes all five, it's a strong source. If it fails the first check, don't waste time on the rest.

---

## Cross-Referencing Rules

When multiple sources cover the same claim:

- **3+ independent sources agree** → High confidence. State as established finding.
- **2 sources agree, none disagree** → Moderate confidence. Cite both.
- **Sources disagree** → Present both sides. Note which has stronger evidence.
- **Only 1 source** → Lower confidence. Note this is a single-source finding.
- **Circular citations** (sources citing each other or a common ancestor) → Treat as single source. Trace back to the original.

---

## Red Flags

Discard or heavily discount sources that:

- Have no author attribution and no institutional backing
- Make extraordinary claims without extraordinary evidence
- Contain obvious factual errors in areas you can verify
- Are primarily selling a product or service
- Were published on content farms or SEO-optimized sites with thin content
- Appear to be AI-generated without human editorial oversight
- Have URLs that look auto-generated or spammy

---

## When In Doubt

If you're unsure about a source:

1. Look for the same claim in other sources
2. Check if the author has other credible publications
3. Look for the source being cited by others you trust
4. If still unsure, include it with a caveat: "According to [source], though this has not been independently verified..."

It's better to include a source with appropriate caveats than to silently exclude it — the user can then decide for themselves.
