---
name: model-pricing-visualizer
description: analyze ai model pricing tables and generate comparison reports or infographic-style images. use when a user provides model cost data with list prices, discounted prices, discounts, token tiers, character pricing, video-second pricing, or notes, and asks to compare models, rank costs, identify output/input cost ratios, long-context premiums, discount impact, pricing risks, or produce a visual pricing analysis.
---

# Model Pricing Visualizer

## Overview

Use this skill to turn an AI model pricing table into a decision-oriented cost analysis and, when requested, a comparison image. The core principle is to compare prices only within the same billing unit, then surface the operational implications: discounted output cost, input cost, output/input ratio, context-tier premium, and note-based pricing risk.

## Workflow

1. Parse the table into structured rows.
   - Treat section header rows as category/unit context, such as text token pricing, speech character pricing, or video seconds pricing.
   - Preserve the original model name, tier, list input price, list output price, discount, discounted input price, discounted output price, and notes.
   - Treat values such as `not charged`, `free`, `na`, and `\u4e0d\u8ba1\u8d39` as non-billable rather than zero-cost arithmetic inputs.

2. Normalize pricing fields.
   - Prefer explicit discounted prices when provided.
   - If discounted fields are missing but list price and discount are present, compute discounted price as `list_price * discount`.
   - Do not compute output/input ratios when either side is non-billable or missing.

3. Separate incomparable billing units.
   - Text models are usually priced per million tokens.
   - Speech models may be priced per ten thousand characters.
   - Video models may be priced per generated second.
   - Never directly rank text, speech, and video together by raw unit price. Compare each domain internally and explain the unit boundary clearly.

4. Build the analysis in this priority order.
   - Text discounted output price: usually the main cost driver for generation-heavy apps.
   - Text discounted input price: important for retrieval, long prompts, and agent context loading.
   - Output/input ratio: identifies models where generation is disproportionately expensive.
   - Long-context premium: compare the highest tier versus the lowest tier for the same model.
   - Discount depth: explain whether cheaper actual price comes from lower list price, larger discount, or both.
   - Notes and risk flags: call out delayed discounts, pending launch status, special remarks, or contract caveats.

5. Generate the visual narrative.
   - Header: title, unit caveat, and data basis.
   - Summary cards: cheapest text input, cheapest text output, cheapest third-party output if identifiable, most expensive text output, speech headline, video headline.
   - Ranked text table: sort text rows by discounted output price ascending; include category, discounted input, discounted output, output/input ratio, and proportional bars.
   - Key conclusions: cost tiers, long-context premium, output cost pressure, and note/risk flags.
   - Long-context premium table: for models with multiple tiers, show highest-tier / lowest-tier input and output multiples.
   - Non-text comparison: show speech and video separately because their billing units differ.

6. Use the bundled script when a PNG is requested.
   - Save the user-provided pricing table to a UTF-8 text file.
   - Run: `python scripts/generate_pricing_image.py --input pricing_table.txt --output model_pricing_comparison.png`
   - If the table has unusual column names, patch the parser or convert the table to the expected columns before running the script.
   - If the user wants a different visual style, modify labels, section order, card selection, or dimensions in the script rather than changing the analysis logic.

## Default report structure

When answering in chat, use this structure unless the user asks for a different format:

1. Start with the most actionable conclusion, not a data dump.
2. Explain the unit caveat: text, speech, and video cannot be directly ranked together.
3. Provide the top 3-5 pricing findings.
4. Provide usage recommendations such as low-cost generation, long-context usage, third-party fallback, or premium model scenarios.
5. List caveats and note-based risks.
6. Link the generated image or artifact if one was created.

## Quality bar

- Prefer discounted prices over list prices for ranking, because discounted prices drive actual budget impact.
- Always mention if the analysis is based only on the user-provided table.
- Use concrete numbers in conclusions.
- Avoid pretending to know model quality from price alone. If quality, latency, or benchmark tradeoffs matter, say that separate evaluation data is needed.
