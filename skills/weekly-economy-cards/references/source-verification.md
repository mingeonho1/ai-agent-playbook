# Source verification contract

For each card, record the institution, original URL, publication date, indicator period, value, unit, comparison baseline, seasonal-adjustment status, and provisional/final status when the source provides it.

Before rendering, compare these fields against both `data.js` and `sources.md`.

| Check | Example failure |
| --- | --- |
| Period | August observation presented as September data |
| Unit | Percent confused with percentage points |
| Comparison | Month-over-month caption used for a year-over-year value |
| Adjustment | Seasonally adjusted and unadjusted series mixed |
| Timing | Decision date confused with policy effective date |
| Scope | Total employment presented as youth employment |

The `그래서 우리한텐?` block is an interpretation. Use conditional language such as `부담이 될 수 있어요` and state an important dependency when useful. Never upgrade a plausible pathway into a guaranteed outcome.

