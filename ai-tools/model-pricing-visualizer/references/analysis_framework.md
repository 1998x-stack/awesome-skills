# Pricing Analysis Framework

## Why this analysis works

The useful comparison is not a generic price ranking. It is a cost-model decomposition:

1. Unit domain: token, character, second, request, image, or another billing unit.
2. Real paid price: discounted input and output prices, not only list prices.
3. Workload shape: input-heavy, output-heavy, long-context, or media-duration-heavy.
4. Price slope: tier jumps caused by context length, resolution, duration, or quality tier.
5. Procurement risk: notes such as pending discount activation or special rollout timing.

## Canonical metrics

- discounted_input = explicit discounted input if available, else list_input * discount
- discounted_output = explicit discounted output if available, else list_output * discount
- output_input_ratio = discounted_output / discounted_input when both are billable
- long_context_input_premium = highest_tier_discounted_input / lowest_tier_discounted_input
- long_context_output_premium = highest_tier_discounted_output / lowest_tier_discounted_output

## Interpretation rules

- Cheapest output model is usually best for verbose generation, summarization, writing, and agent responses.
- Cheapest input model is useful for large prompt ingestion, retrieval augmentation, and classification over long context.
- Low output/input ratio indicates a model is less punitive for generation-heavy workloads.
- Large context premium means the application should avoid unnecessarily crossing the next context tier.
- A low list price with a weak discount can lose to a higher list price with a stronger discount.
- Notes can override raw price ranking when discounts are not yet active or terms are uncertain.

## Recommended visual hierarchy

1. Summary cards for decision anchors.
2. Ranked text model table by discounted output price.
3. Insight cards with natural-language interpretation.
4. Long-context premium comparison.
5. Separate speech/video blocks with their own billing units.
