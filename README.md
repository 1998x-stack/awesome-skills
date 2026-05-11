# Awesome Skills

> 🎯 A curated collection of high-quality Agent Skills for AI coding assistants — battle-tested, production-ready, and organized by domain.

[![Skills](https://img.shields.io/badge/skills-19-brightgreen)]()
[![Files](https://img.shields.io/badge/files-400+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## What Are Skills?

Skills are modular, self-contained instruction sets that transform AI coding assistants into specialized experts. Each skill includes:

- **`SKILL.md`** — Core instructions and workflow
- **`references/`** — Detailed guides, patterns, and examples
- **`agents/`** — Agent configuration files
- **`scripts/`** — Automation and scaffolding tools
- **`assets/`** — Templates, styles, and components

---

## 📚 Skills Directory

### 🎨 Design & UI

| Skill | Lines | Description |
|-------|-------|-------------|
| [**claude-design**](claude-design/) | 330 | Expert HTML design — slide decks, prototypes, dashboards, animations in vanilla HTML/CSS or React+Babel |
| [**html-ppt**](html-ppt/) | 186 | Professional HTML slide deck generation with themes, layouts, and animations |
| [**html-design-manager**](html-design-manager/) | 169 | Design system management for HTML-based design workflows |
| [**graphify**](graphify/) | 1,214 | Visual graph and chart generation from data |
| [**gptimage2-prompt-builder**](gptimage2-prompt-builder/) | 87 | Professional prompt builder for GPT image generation |

### 🎮 Game Development

| Skill | Lines | Description |
|-------|-------|-------------|
| [**godot-engine**](godot-engine/) | 279 | Complete Godot engine development — GDScript, scene architecture, physics, shaders |
| [**game-design**](game-design/) | 160 | Comprehensive game design framework — GDD templates, loop design, economy systems |
| [**game-design-analyst**](game-design-analyst/) | 169 | Game design analysis using prosocial design principles and Jenova Chen's framework |

### 🤖 Agent & AI Engineering

| Skill | Lines | Description |
|-------|-------|-------------|
| [**autonomous-research**](autonomous-research/) | 240 | Autonomous research agent framework — methodology, source evaluation, scoping |
| [**prefab-search**](prefab-search/) | 210 | Intelligent search and categorization system with 13 category definitions |
| [**ralph-loop**](ralph-loop/) | 156 | Ralph loop pattern for iterative AI agent workflows |
| [**system-prompt-calibrator**](system-prompt-calibrator/) | 121 | Calibrate and optimize system prompts using altitude rubrics and patterns |
| [**model-pricing-visualizer**](model-pricing-visualizer/) | 68 | Generate pricing comparison charts for LLM models |

### 💡 Innovation & Strategy

| Skill | Lines | Description |
|-------|-------|-------------|
| [**bottom-up-innovation**](bottom-up-innovation/) | 208 | Identify innovation opportunities using opportunity lenses and scoring frameworks |
| [**musk-guidelines**](musk-guidelines/) | 141 | First-principles thinking and engineering guidelines inspired by Elon Musk |
| [**sunge-guidelines**](sunge-guidelines/) | 213 | Strategic thinking and execution guidelines |

### 🛠️ Development & Engineering

| Skill | Lines | Description |
|-------|-------|-------------|
| [**taptap-maker-issue-builder**](taptap-maker-issue-builder/) | 148 | Automated issue builder for TapTap Maker with routing maps |
| [**kadike-prompt**](kadike-prompt/) | 238 | Cinematic video prompt engineering — voiceover, Seedance, and brand guides |
| [**history-guidelines**](history-guidelines/) | 160 | Managing and leveraging conversation history in AI workflows |

---

## 🚀 Quick Start

### Browse Skills

```bash
# Clone the repository
git clone git@github.com:1998x-stack/awesome-skills.git
cd awesome-skills

# List all skills
ls */SKILL.md

# Explore a specific skill
cat godot-engine/SKILL.md
ls godot-engine/references/
```

### Use with AI Coding Assistant

Most skills follow this pattern:

1. **Read** the `SKILL.md` file to understand the workflow
2. **Check** `references/` for detailed guides and examples
3. **Apply** the skill to your project context
4. **Extend** with your own patterns and templates

---

## 📊 Statistics

```
Total Skills:     19
Total Files:      400+
Total Lines:      ~5,000+
Categories:       5 (Design, Game, Agent, Innovation, Engineering)
```

### By Category

```
🎨 Design & UI          5 skills   (2,000+ lines)
🎮 Game Development     3 skills   (600+ lines)
🤖 Agent & AI           5 skills   (800+ lines)
💡 Innovation           3 skills   (560+ lines)
🛠️ Engineering          3 skills   (550+ lines)
```

---

## 📁 Skill Structure

Each skill follows a consistent structure:

```
skill-name/
├── SKILL.md              ← Core instructions (required)
├── references/           ← Detailed guides and examples
│   ├── patterns.md
│   └── examples.md
├── agents/               ← Agent configurations (optional)
│   └── openai.yaml
├── scripts/              ← Automation tools (optional)
│   └── scaffold.py
└── assets/               ← Templates and resources (optional)
    └── base.css
```

---

## 🤝 Contributing

### Add a New Skill

1. Create a new directory under the root: `my-skill/`
2. Add `SKILL.md` with the skill definition
3. Add `references/`, `scripts/`, `assets/` as needed
4. Update this README with your skill

### SKILL.md Template

```markdown
---
name: my-skill
description: >
  Brief description of what this skill does and when to use it.
---

# My Skill

## Workflow
1. Step one
2. Step two
3. Step three
```

### Guidelines

- Keep `SKILL.md` focused and actionable
- Use `references/` for detailed explanations
- Include working examples in `references/examples.md`
- Add agent configs if the skill requires specific settings

---

## 🔄 Update

```bash
# Pull latest skills
git pull origin main

# Check what's new
git log --oneline -10
git diff --stat HEAD~5
```

---

## 📜 License

MIT

---

## 🙏 Acknowledgments

Skills collected from the community and open-source projects. Special thanks to:

- **Karpathy Skills** — Programming guidelines inspired by Andrej Karpathy
- **Supervisor Skills** — Agent orchestration framework
- **Community Contributors** — All skill authors and maintainers

---

<div align="center">

**⭐ If you find this collection useful, give it a star!**

[Skills](#-skills-directory) · [Structure](#-skill-structure) · [Contributing](#-contributing)

</div>
