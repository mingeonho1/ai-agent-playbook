---
name: weekly-economy-cards
description: Create verified weekly Korean economy, stock, and finance news cards for Instagram Stories. Use when producing three concise, source-backed 1080×1920 cards with a reproducible data-to-PNG workflow.
metadata:
  short-description: Verified weekly economy story cards
---

# Weekly Economy Cards

Create three Korean Instagram Story cards for a weekly period. Each card contains one news item, one primary number or comparison, and a short `그래서 우리한텐?` interpretation. The outcome is a downloadable package, not just a draft caption.

## Working method

1. Determine the coverage period. Start on the day after the previous card’s final date; do not overlap weeks.
2. Collect five to eight candidates from primary institutions. Keep three that have a clear number and distinct practical relevance.
3. Check every number against its primary URL before writing. Read [source-verification.md](references/source-verification.md) before creating `data.js`.
4. Keep facts in the headline and conditional interpretation in `그래서 우리한텐?`. Avoid investment advice and causal claims the source does not establish.
5. Use the built-in GPT Image workflow for the card visual, with the approved reference-derived hierarchy and next palette in the required cycle. For a number or date that must remain exact, use the supplied HTML/CSS template as a supporting layer rather than asking the image model to improvise it.
6. Inspect PNGs. Fix wording or regenerate if the reading order, data legibility, or balance fails. Archive PNGs, source notes, input data, provenance, and ZIP under the weekly run folder.

## Orchestration and token budget

When the Claude Code Fable profile is available, use its `deep-reasoner` role for editorial planning, source-conflict resolution, and visual tradeoffs. Use Claude Opus 5.1 with maximum effort for this role. Route implementation, rendering, and verification changes to the `executor` role using Claude Opus 5.0 at extra-high effort. Route mechanical file reads, commands, and size checks to Claude Sonnet 5 at medium effort.

Parallelize only independent work: for example, one agent can verify domestic statistics while another checks overseas releases and a third reviews the rendered PNGs. Give each agent a bounded deliverable and source list. Do not ask multiple agents to edit the same `data.js` or design file.

Use expensive reasoning once to choose the three-story angle and resolve evidence conflicts. Keep raw URLs and structured facts in files so builders receive only the selected facts, not repeated article dumps. Stop research when three verified, distinct items are ready; extra candidates do not improve the card.

## Non-negotiable card constraints

- Three cards per weekly edition; one news item per card.
- 1080×1920 PNG; title at most two lines; practical impact one or two short lines.
- Keep the base paper system fixed. Cycle the single accent palette: `green-coral → teal-orange → olive-terracotta`.
- Place the release source and date in the footer; put full URLs and verification notes in `sources.md`.
- Use the built-in GPT Image workflow for final card visuals. Keep the HTML/CSS renderer available as a supporting path for exact text or chart layers.

## Read when needed

- For primary-source facts and wording checks: [source-verification.md](references/source-verification.md)
- For visual hierarchy, typography, and palette choices: [design-system.md](references/design-system.md)
- For folder names, output artifacts, and notification content: [run-package.md](references/run-package.md)
