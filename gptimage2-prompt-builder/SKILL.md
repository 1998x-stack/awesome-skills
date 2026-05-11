---
name: gptimage2-prompt-builder
description: generate, refine, critique, and translate chinese text-to-image prompts for gpt image 2 / chatgpt image generation. use when the user asks for gpt image 2 prompts, official-style image prompts, chinese prompt engineering for text-to-image, high-fidelity visual prompt expansion, prompt analysis, style keyword extraction, or converting a rough idea into a detailed image-generation prompt with composition, medium, typography, layout, materials, scene, text-rendering, and aspect-ratio control.
---

# GPT Image 2 Prompt Builder

## Core principle

Turn a vague visual idea into a production-grade Chinese image prompt by specifying **what is being made**, **how it is visually constructed**, **what exact readable text appears**, **which medium/style system governs the image**, and **which constraints must not be lost**.

GPT Image 2 prompts work best when they read like an art-director brief, not a keyword dump. Be concrete, complete, and compositional.

## Workflow

1. Identify the output format: poster, magazine spread, photo, comic page, infographic, brand board, product grid, character sheet, print asset, UI screenshot, etc.
2. Select a dominant visual system from `references/style-taxonomy.md`.
3. Fill the canonical prompt skeleton in `references/prompt-template.md`.
4. Add text-rendering instructions when the image contains titles, labels, annotations, handwriting, UI, speech bubbles, or multilingual text.
5. Add fidelity constraints: aspect ratio, camera/lens, material, lighting, layout grid, typography, historical era, print marks, continuity, legibility, and no missing details.
6. Return one polished Chinese prompt. When useful, also return a short “关键词拆解” section.

## Official-style prompt anatomy

Always try to include these layers, in this order:

1. **作品类型 + 主题**: e.g. “现代主义风格主题海报，标题为……”
2. **画面主体**: people, objects, place, UI, products, characters, symbols.
3. **视觉系统**: modernist, bauhaus, editorial, 35mm realism, manga, art deco, surrealist, nostalgic computer lab, etc.
4. **构图/版式**: bold typography, magazine body copy, panels, grid, spread, scrapbook, infographic modules.
5. **材质/媒介**: film grain, rough paper, burlap, print halftone, pencil handwriting, CRT screen, glossy fashion lighting.
6. **文字内容**: exact title, labels, captions, speech text, multilingual samples; demand readable, correctly spelled text.
7. **场景细节**: background, props, environment, cultural cues, activities, maps, charts, UI windows.
8. **摄影/绘画控制**: lens, macro, flash, natural light, cinematic framing, low saturation, black and white, color palette.
9. **质量与约束**: high fidelity, complete details, commercial-ready, unified style, consistent characters, accurate annotations, specified aspect ratio.

## Text rendering rules

When the image includes text:

- Quote every required title or phrase exactly with Chinese quotation marks or English quotes.
- Say whether the text is a headline, subtitle, body copy, handwritten note, label, UI text, map label, chart label, speech bubble, or print mark.
- Request “清晰可读、拼写准确、排版合理、无乱码、无伪文字”.
- For multilingual outputs, name the scripts/languages and their layout role.
- For handwriting, specify paper type, tool, pressure, alignment, classroom/note-taking context.
- For comics, require readable speech bubbles and consistent character identity across panels.

## Style selection shortcuts

Use these compact mappings when expanding prompts:

- **海报/品牌/趋势** → bold typography, modernist grid, geometric color blocks, editorial hierarchy, cream/red/blue/black/yellow palette.
- **信息图/科普/学术** → magazine-grade layout, labeled diagrams, maps, statistics, step-by-step visual logic, clean annotations.
- **摄影写实** → camera/lens, lighting, location, candid realism, material texture, atmospheric storytelling.
- **漫画/分镜/角色设定** → panel structure, motion lines, readable dialogue, consistent character design, emotion arc, genre-specific rendering.
- **文旅/生活方式/品牌物料** → commercial-ready art direction, local culture cues, photography plus typography, unified brand system.
- **复古/做旧/胶片** → halftone, torn paper, film grain, timestamp, aged texture, analog print feel.
- **超现实/艺术肖像** → symbolic transformation, dreamlike set, coherent color tone, psychological narrative.

## Output format

When asked to create a prompt, use:

```markdown
## GPT Image 2 中文 Prompt
[one complete polished prompt]

## 关键词拆解
- 类型/媒介：...
- 主体/场景：...
- 风格/时代：...
- 版式/构图：...
- 文字/标注：...
- 光影/材质：...
- 质量约束：...
```

When the user asks only for a prompt, omit long explanation unless requested.

## Negative constraints

Do not produce generic strings such as “高清、精美、好看” without concrete visual constraints. Avoid conflicting style stacks. Do not omit required text. Do not invent copyrighted characters or living-person likenesses unless the user explicitly requests a safe allowed transformation. Do not overfit to “official” wording if the user needs a different brand, market, or medium.

## References

- For the full taxonomy of styles, prompt atoms, and the 47-item pattern analysis, read `references/style-taxonomy.md`.
- For reusable templates and examples, read `references/prompt-template.md`.
