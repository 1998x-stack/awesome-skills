# /llm-wiki:journal -- Create journal entries

Create daily notes, reflections, or judgments with automatic wiki linking.

## Usage

```
/llm-wiki:journal daily                    # Today's daily note
/llm-wiki:journal reflection <topic>       # Deep reflection on a topic
/llm-wiki:journal judgment <topic>         # Record a decision/judgment
```

## Steps

### daily
1. Check if `journal/daily/YYYY-MM-DD.md` exists; if so, read it
2. If not, create from `<skill>/templates/daily.md` (or user override in `templates/daily.md`)
3. Search wiki for recently ingested topics -> suggest links in "Related" section

### reflection
1. Create `journal/reflections/<topic>.md` from template
2. Search wiki for related pages -> populate "Related" section with [[links]]

### judgment
1. Create `journal/judgments/<topic>.md` from template
2. Search wiki for related pages -> populate "Related Knowledge" section

## !insight Support

When writing journal content, the user can mark paragraphs with `!insight`:

```
Today I realized: the condition number describes the problem's intrinsic
sensitivity, while algorithm stability describes the solution process.
The two are orthogonal. !insight
```

This marks the content for automatic wiki page creation during the next `/llm-wiki:review`.
