# Research Methodology Guide

How to structure research across different domain types. Read this when you encounter a topic type you haven't researched before, or when you need guidance on which methodology fits.

---

## Table of Contents

1. [Domain-Specific Approaches](#domain-specific-approaches)
2. [Research Depth Levels](#research-depth-levels)
3. [Question Decomposition](#question-decomposition)
4. [Search Strategy Patterns](#search-strategy-patterns)
5. [Synthesis Patterns](#synthesis-patterns)

---

## Domain-Specific Approaches

### Technical / Engineering Research

**Goal**: Understand how something works, compare implementations, evaluate tradeoffs.

**Structure**:
1. Problem definition — what problem does this solve?
2. Landscape — what solutions exist?
3. Architecture / mechanism — how does each work?
4. Tradeoffs — performance, complexity, maintainability
5. Recommendations — which to use when

**Sources to prioritize**: Official documentation, engineering blogs from companies using it at scale (Netflix, Google, Stripe tech blogs), GitHub repos with high stars, benchmarks with methodology disclosed.

**Watch out for**: Vendor marketing disguised as technical comparison. If a "comparison" is published by one of the vendors, note the bias.

### Academic / Scientific Research

**Goal**: Understand the state of knowledge, identify consensus and open questions.

**Structure**:
1. Background — foundational concepts
2. Current state — what's known, what's the consensus
3. Active debates — where experts disagree
4. Recent advances — what's changed recently
5. Open questions — what's unknown

**Sources to prioritize**: Survey papers, highly-cited papers, papers from top-tier venues (NeurIPS, ICML, Nature, Science), preprint servers (arXiv) for recent work.

**Watch out for**: Single papers presented as consensus. One study ≠ established knowledge. Look for replication and meta-analyses.

### Market / Competitive Research

**Goal**: Understand the competitive landscape, market dynamics, opportunities.

**Structure**:
1. Market overview — size, growth, key segments
2. Key players — who's doing what
3. Competitive dynamics — differentiation, pricing, positioning
4. Trends — where the market is heading
5. Opportunities / threats — gaps, risks

**Sources to prioritize**: Industry reports (Gartner, McKinsey, CB Insights), company press releases and earnings calls, product comparison sites, user reviews, job postings (signal of company priorities).

**Watch out for**: Outdated market data. Markets move fast. A 2023 market map may be very different from 2025.

### Policy / Regulatory Research

**Goal**: Understand the regulatory landscape, compliance requirements, policy debates.

**Structure**:
1. Current regulation — what's in effect
2. Proposed changes — what's being debated
3. Enforcement — how regulations are applied
4. Compliance implications — what organizations need to do
5. Stakeholder positions — who wants what

**Sources to prioritize**: Government websites, legal databases, policy think tanks, regulatory agency publications, law firm analysis memos.

**Watch out for**: Advocacy disguised as analysis. Check who funds the think tank.

### Historical / Conceptual Research

**Goal**: Understand how something evolved, why it is the way it is.

**Structure**:
1. Origins — how and why it started
2. Key developments — turning points
3. Current state — where things stand
4. Lessons — what patterns emerge
5. Future implications — where trends point

**Sources to prioritize**: Books and long-form articles, original primary sources, oral histories, established encyclopedias.

---

## Research Depth Levels

### Survey / Overview
- 5-10 sources
- Focus on breadth: cover all major aspects
- Cite authoritative overviews rather than primary sources
- Aim for 2-3 page output
- Time budget: 15-20 min of searching

### Working Knowledge
- 10-20 sources
- Balance breadth and depth
- Include both overviews and some primary sources
- Aim for 5-7 page output
- Time budget: 30-40 min of searching

### Expert-Level
- 20-40 sources
- Prioritize primary sources over summaries
- Include methodology discussions, limitations, edge cases
- Aim for 8-15 page output
- Time budget: 45-60 min of searching

### State-of-the-Art
- 30-50+ sources
- Focus on the most recent work (last 6-12 months)
- Include preprints, conference talks, blog posts from researchers
- Track active debates and unresolved questions
- Aim for 10-20 page output
- Time budget: 60-90 min of searching

---

## Question Decomposition

Break a broad topic into researchable sub-questions using the **5W1H framework**:

| Dimension | Question Type | Example |
|-----------|--------------|---------|
| What | Definition, scope | "What is retrieval-augmented generation?" |
| Why | Motivation, importance | "Why is RAG preferred over fine-tuning for knowledge-intensive tasks?" |
| Who | Key players, stakeholders | "Who are the leading companies building RAG systems?" |
| When | Timeline, recency | "When did RAG emerge as a dominant paradigm?" |
| Where | Application domains | "Where is RAG most effectively applied?" |
| How | Mechanism, implementation | "How does RAG integrate retrieval with generation?" |

Not all dimensions matter for every topic. Pick the 3-5 most relevant.

### Decomposition Heuristic

1. Start with the broadest version of the question
2. Identify the 2-3 most important sub-questions
3. For each sub-question, identify what specific evidence would answer it
4. Map evidence types to search strategies

---

## Search Strategy Patterns

### Snowball Search
Start with one known good source, then follow its references and citations. Good for academic research where citation networks are strong.

### Convergent Search
Search from multiple different angles and see where results converge. If three independent searches all point to the same conclusion, confidence is high. Good for controversial or ambiguous topics.

### Adversarial Search
Deliberately search for counterarguments and opposing views. For every "X is good" finding, search for "X problems" or "X criticism". Good for evaluation/comparison research.

### Temporal Search
Search the same topic across different time periods to understand evolution. Add year qualifiers to queries. Good for historical and trend analysis.

### Expert Search
Find who the recognized experts are, then search for their specific writings. Use "site:" operators for known expert blogs or institutions. Good for cutting-edge topics where the knowledge is concentrated among a few people.

---

## Synthesis Patterns

### Convergence Synthesis
Multiple sources agree → state the consensus with citations.

### Tension Synthesis
Sources disagree → present both sides, note the nature of the disagreement (methodological? definitional? ideological?), and assess which has stronger evidence.

### Gap Synthesis
Question not adequately answered by any source → explicitly note the gap, hypothesize why it exists (too new? too niche? actively debated?), and suggest where answers might be found.

### Layered Synthesis
Build from simple to complex: start with the basic answer, then add nuance, caveats, and edge cases in layers. Match the layer depth to the requested research depth.
