# Skill Visualizer — Design Spec

A single-page static website that visualizes all 1596+ SKILL.md and AGENTS.md files in this repository, deployed on GitHub Pages from the `assets/` directory.

## Architecture

```
build.js (Node.js, one-shot)
  ├─ Recursively scan 9 categories + 6 collections
  ├─ For each SKILL.md / AGENTS.md:
  │   ├─ Parse YAML frontmatter (gray-matter)
  │   ├─ Extract markdown body
  │   └─ Enumerate sibling references/, scripts/, examples/, agents/, assets/
  ├─ Build tree structure (category → skill → sub-files)
  └─ Output → assets/data.json

assets/
  ├─ index.html    ← Single page, loads data.json, marked.js via CDN
  └─ data.json     ← All data (frontmatter, body, file tree, paths)
```

- Build command: `node build.js`
- GitHub Pages: point to `assets/` directory
- No server required. All rendering is client-side.

## UI Layout

- **Top bar** (48px, fixed): search input + dark/light toggle
- **Left sidebar** (280px, collapsible): tree view — categories → skills, expandable
- **Right content** (scrollable):
  - Sticky YAML frontmatter card at top (name, description, any other frontmatter keys)
  - Rendered markdown body below (marked.js)
  - Attached files section at bottom — clickable links to references/, scripts/, examples/
- **Bottom bar**: breadcrumb trail (category / skill name)
- **File viewing**: clicking a reference/script file opens its content inline or in a modal. .md files rendered with marked.js, .yaml/.json with syntax highlighting, .py/.js with code blocks.

## Data Model

```json
{
  "tree": [
    {
      "name": "ai-tools",
      "type": "category",
      "children": [
        {
          "name": "autonomous-research",
          "path": "ai-tools/autonomous-research",
          "type": "skill",
          "frontmatter": { "name": "...", "description": "..." },
          "body": "# markdown content...",
          "files": [
            { "name": "references/", "type": "dir", "children": [
              { "name": "methodology.md", "type": "file", "path": "...", "ext": ".md", "content": "# file content..." }
            ]}
          ]
        }
      ]
    }
  ]
}
```

- `type`: `category` | `collection` | `skill` | `agent-doc` | `dir` | `file`
- `body`: raw markdown string for client-side rendering
- `content` (file nodes only): the file's text content, included so it can be rendered inline without additional fetches (required for static GitHub Pages)
- `files`: recursive directory tree for attachments/references

## Navigation

- Tree sidebar: click skill name → loads into content area via hash routing (`#/ai-tools/autonomous-research`)
- Search: fuzzy match against `frontmatter.name` + `frontmatter.description`, filters tree in real-time
- Breadcrumb shows current path, clickable to go back up

## Build Details

- Script language: Node.js (for gray-matter npm package)
- Recursive directory walk, skip `.git/`, `node_modules/`, `.DS_Store`
- AGENTS.md / CLAUDE.md files included as type `agent-doc`
- Skills with empty or missing frontmatter still included with `{}` frontmatter
- data.json written in compact form (no whitespace) to minimize size for 1596+ skills. Gzip by GitHub Pages will compress further.
- Sub-files (references, scripts, examples) have their content embedded as `content` field so they can be viewed inline without additional HTTP requests

## Client-Side Dependencies

- **marked.js** (CDN): Markdown rendering
- **highlight.js** (CDN): Syntax highlighting for code blocks in markdown, and for .yaml/.py/.js file content in modals
- **No framework** — vanilla HTML/CSS/JS

## Scope

- All 9 functional categories: guidelines-mindsets, design-creative, game-development, ai-tools, dev-engineering, document-generation, platform-ecosystems, life-automation, domain-expertise
- All 6 large collections: ECC, awesome-copilot, gstack, get-shit-done, servers, spec-kit
- All SKILL.md, AGENTS.md, and CLAUDE.md files (1596+ total)

## Non-Goals

- No live editing of skills
- No search across markdown body text (frontmatter only, to keep JSON size manageable)
- No diff/history view
- No mobile-first responsive design (desktop-first, minimum viable responsive)
