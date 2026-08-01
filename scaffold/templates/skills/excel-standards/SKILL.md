---
name: excel-standards
description: Excel and financial-model best practices (CFI-based) — sheet structure, blue/black/green font conventions, formula discipline, balance-sheet checks and cash-flow tie-outs, scenario switches, sensitivities, charts, performance, and keyboard shortcuts. Use whenever building, editing, reviewing, or auditing an Excel model or spreadsheet — three-statement models, DCF/valuations, projections, budgets, LBOs, operating models, dashboards, or any .xlsx workbook — even if the user never says "best practices". Complements the `xlsx` skill: `xlsx` does the file mechanics (read/write/format cells), this governs how the model itself should be designed, checked, and delivered.
---

# Excel Best Practices (CFI-based)

Operating rules for designing, building, and auditing any Excel model. These exist so a model is **auditable by someone other than its author** — a reviewer should trace any number back to an input in seconds, and a single glance should reveal whether the model still balances. Prefer clarity a stranger can follow over cleverness only you can.

When the `xlsx` skill handles the actual file writing, these rules decide *what* to write; run both together.

## Structure
- Separate inputs, calculations, and outputs into distinct sheets or clearly labeled sections — so a change to an assumption is never buried inside a calculation.
- Flow the model top-to-bottom and left-to-right; time periods across columns, line items down rows.
- One tab per logical module (Assumptions, IS, BS, CF, Schedules, Valuation, Summary).
- One file per model; avoid cross-workbook links (they break silently when a file moves).
- Build a cover sheet with model purpose, version, author, date, and the color key.

## Formatting and color conventions
The font-color convention is the fastest audit tool in Excel — it tells a reviewer at a glance what is an assumption they can change versus what is derived. Keep it strict:
- Hard-coded inputs in **blue** font.
- Formulas and calculations in **black** font.
- Links to other worksheets in **green** font.
- External links in **red** font (and minimize them).
- Light-yellow shading for input cells.
- Consistent number formatting: commas, parentheses for negatives, no decimals for whole-dollar items.
- Show units (USD mm, %, x) in column headers, not inside cells.
- Freeze panes at the first data column and header row.

## Formulas
- One formula per row, copied identically across all periods — a row a reviewer can read once and trust across time.
- Never hard-code a number inside a formula; reference an input cell instead.
- Keep formulas short; break complex logic into helper rows rather than one unreadable mega-formula.
- Avoid volatile functions (OFFSET, INDIRECT, NOW, TODAY) unless truly required — they recalc constantly and slow the book.
- Prefer INDEX/MATCH or XLOOKUP over VLOOKUP.
- Use IFERROR to trap *expected* errors only — never to hide a real break you should be seeing.
- Anchor references with `$` deliberately; don't overuse absolute refs.
- Use SUMIFS/COUNTIFS instead of array formulas where possible.

## Integrity and controls
These are the difference between a model you trust and one you hope is right.
- Balance-sheet check (Assets = Liabilities + Equity) on every sheet header.
- Cash-flow tie-out: CF statement ending cash = BS cash.
- A single "Error check" cell on the cover sheet that flags any break anywhere.
- Avoid circular references. If interest-on-debt circularity is genuinely needed, control it with an iteration switch and document it.
- Never deliver a model in manual calc mode.

## Sensitivities and scenarios
- Drive scenarios from a single switch cell using CHOOSE or INDEX — one place to flip the whole model.
- Centralize all scenario inputs in one block; never scatter them across tabs.
- Build data tables for two-variable sensitivities; isolate them on a dedicated tab.
- Stress-test with bull, base, and bear cases; document each.

## Readability
- Clear, descriptive row labels; avoid abbreviations.
- Indent subtotals one column to the right; bold totals.
- Underline rows above subtotals, double-underline final totals.
- Group and outline supporting rows so the model collapses to a summary view.
- Consistent column widths across tabs.
- Hide gridlines on output and presentation tabs.

## Charts and dashboards
- Choose chart type by purpose: column for comparison, line for trend, waterfall for a bridge, scatter for correlation.
- Remove chart junk: no 3D, no shadows, minimal gridlines, no chart border.
- Label data directly on the chart instead of using legends when possible.
- One accent color plus grayscale; reserve red for negatives.
- Source every chart from a dedicated data range, not the raw model.

## Performance
- Avoid full-column references (`A:A`); use bounded ranges or Tables.
- Convert large data ranges to Excel Tables for structured references.
- Replace nested IFs with IFS, SWITCH, or lookup tables.
- Remove unused formatting and conditional formats from blank ranges.

## Workflow
- Version files with a date suffix and version number: `Model_2026-05-25_v03.xlsx` (YYYY-MM-DD, v##).
- Save a clean blank template before adding scenario overrides.
- Never delete columns mid-model; insert new ones at the end of the time series.
- Document every non-obvious assumption with a cell comment or a footnote row.

## Shortcuts to default to
Keyboard-only navigation and formatting is faster and more precise than the mouse:
- F2 edit, F4 toggle reference, F9 calc, Ctrl+arrow navigate, Ctrl+Shift+arrow select, Alt+= autosum.
- Alt+E,S,V paste special values; Alt+H,O,I autofit column.
- Ctrl+1 format cells; Ctrl+; date; Ctrl+Shift+L filter.

## When you build or edit a model
Run this sequence before calling a model done:
1. Confirm purpose, audience, and time horizon before building.
2. State assumptions explicitly and place them in a single inputs block.
3. Show the formula logic in plain English next to each calculation block.
4. Run the balance-sheet check and cash-flow tie-out before delivering.
5. Provide a one-tab executive summary with the 3-5 outputs that matter.
