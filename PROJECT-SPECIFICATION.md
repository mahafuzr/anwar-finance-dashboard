---
name: build-anwar-finance-dashboard
description: Build or revise the Anwar Group multi-SBU finance web app with the same menus, sections, filters, charts, source drilldowns, Excel upload templates, financial analysis and insights as the dashboard updated on 15 October 2026. Use for reproducing this dashboard, extending its analysis or adding grounded AI insights while preserving its experience.
---

# Build the Anwar Group finance dashboard

## Baseline and workflow

Reproduce the latest dashboard, including expanded SBU analysis. Use bundled `assets/dashboard/` as the exact implementation baseline. It contains all HTML, CSS, JavaScript, existing source datasets and eight blank Excel templates. Copy the complete directory into the new app's static output directory. Preserve its relative paths. Do not replace it with a generic finance dashboard.

Baseline date: 15 October 2026. Source commit: `33cee7a168e1236ddccf8cceed3ea259031fa9cf`.
Current dashboard: https://agl-finance-ai-insights.mahafuzr.chatgpt.site/
Original structural reference: https://agl-finance-sep26.anwar-9865.chatgpt.site/

Use the original reference only for experience and structure, never as a financial data source. The bundled latest implementation takes precedence over older reference behavior and superseded requests. Keep existing access private unless the user requests otherwise.

1. Inspect `index.html`, `reference.css` and the relevant final module in the bundled directory before editing.
2. Copy all baseline assets for exact reproduction. Preserve final overrides; older functions in `app.js` are not the final specification.
3. Use only the existing authorized source data or newly supplied files. For a different organization, replace Anwar data with its authorized records or compatible empty datasets. Never present Anwar numbers as another organization's figures.
4. If migrating frameworks, preserve calculation, DOM interaction and source-evidence parity through shared SBU/period context and null-safe financial functions.
5. Implement, verify and deliver the requested app through the supported hosting workflow. Do not modify the original live dashboard merely to demonstrate this skill.

This Markdown is the complete functional contract; the bundled assets preserve exact labels, visual details, formulas and interactions. If only SKILL.md is transferred without its assets, request the latest source export before claiming exact reproduction.

## Source modules and load order

Retain this order because modules intentionally override earlier functions:

| File | Responsibility |
|---|---|
| `app.js` | Shared render, records, formatting, evidence modal, XLSX foundations |
| `multi.js` | SBU portfolio, activation, normalization, batch imports |
| `drivers.js` | Comparison analytics and reconciled profit bridge |
| `financial.js` | Balance-sheet, cash-flow, equity and reconciliation readers |
| `products.js` | Product definitions and source evidence |
| `pricing.js` | Net Sales Price parsing and rates |
| `economics.js` | Final product economics view |
| `review-menus.js` | Departments, targets, costs, break-even, planning, statements |
| `cash-analysis.js` | Final cash and working-capital view |
| `performance-review.js` | Final performance overview and board review |
| `chart-focus.js` | Shared tooltip, point and bar focus |
| `period-filters.js` | Year, month, rolling ranges and date normalization |
| `interactions.js` | Active SBU, series toggles, sorting and searching |
| `sbu-analysis.js` | Expanded SBU comparison |
| `upload.js` | Final upload page, template downloads, menu removals, initial load |

Keep `data.json`, `financial.json`, `additional-sbus.json`, `equity-statements.json` and `pricing.json` as existing source snapshots. Preserve names, labels, dates, worksheet and cell addresses. Read exact algorithms from the final module, not a similarly named superseded function.

## Visual contract

Preserve both `reference.css` and the inline CSS in `index.html`, including their cascade. Use a 235px fixed dark sidebar, pale gray page, white cards/panels, system sans-serif typography and responsive SVG visuals. Preserve ANWAR GROUP / MANAGEMENT FINANCE branding, page heading, active company caption, Refresh, active SBU strip, filter toolbar, content and footer.

| Token | Value |
|---|---|
| Background / paper | `#f3f5f8` / `#ffffff` |
| Ink / muted / border | `#182a38` / `#657582` / `#dfe6ec` |
| Sidebar / teal | `#102635` / `#087f8c` |
| Favorable / adverse / warning | `#137b56` / `#ba4050` / `#b47c20` |
| Desktop layout | Four KPI columns; two analysis columns; main max width 1800px |
| Typography | 30px page heading; 18px panel headings; 13px tables |
| Components | 12px panel radius; teal card top border; 16px card gap; 20px panel-grid gap |

Keep numerical columns right aligned, labels left aligned, rounded controls, compact uppercase labels, dashed empty states, source links and modal dialogs. Preserve mobile horizontal navigation and baseline responsive breakpoints. Preserve print rules that remove navigation/actions/tooltips while retaining readable financial content.

Do not invent extra submenu or tab navigation. The current hierarchy consists of top-level hash menus, in-page selectors, expandable panels, linked review panels, chart legends and source dialogs. Reproduce each of these as implemented.

## Shared context and interaction contract

- Provide Business unit selector and active SBU buttons with active styling and `aria-pressed`. Keep current navigation identifiable with `aria-current`.
- Switching SBU updates all views, products, source evidence, planning context and upload destination. Clear stale product/planning selections and persist active SBU. SBU comparison links open that company's overview.
- Provide Year: All years and individual available years; Month: All months and individual months; Specific period: all periods and rolling last 1, 3, 6, 12 and 24 months. Anchor rolling ranges to latest supplied month, not today's date. Preserve precedence and disabled states from `period-filters.js`.
- Normalize real year-month identities across year boundaries. Freeze identical selected months for all SBU comparisons and restore active context after calculating them.
- Provide BDT, BDT lakh and BDT million display units. Keep MT, BDT/kg, BDT/MT, ratios, percentages and percentage-point changes correctly labelled.
- Refresh reloads browser-saved data and recalculates; it does not reread local Excel files automatically.
- Preserve exports, source modals, hash/back/forward navigation, keyboard interaction, sortable tables and search on eligible tables with at least eight rows. Sort numerically where appropriate, with unavailable values last.
- Show full series/period/value/unit tooltips on hover and keyboard focus. Visibly highlight nearest data points with halo and guide, and bars with outlines. Keep overlays pointer-transparent so source clicks work. Missing points must not select a neighboring observation.
- Preserve legend toggles, accessible tables, viewport-safe tooltips and chart gaps. Never draw missing data as zero.

## Complete menu contract

### 1. Performance overview — `#overview`

Keep comparison selection and net sales, NPAT, net margin and sales MT cards. Show previous-month sales momentum, comparison achievement, contribution, fixed/operating burden, material intensity and all-in cost/MT. Include sales/profit trends and sales-to-profit waterfall. Retain source links and caveat that company value/tonne reflects mix and secondary revenue.

### 2. Board review — `#board`

Keep dynamic headline, comparison, Explain profit and Print review. Preserve eight KPI cards and linked questions about sustainable profit, business cash and recovery. Include adverse profit drivers, discussion questions with suggested leads, quarterly performance with partial-quarter labels, capital-employed/ROCE analysis, product spread signals, liquidity, funding, reconciliation differences and evidence needed next. Suggested leads are discussion roles, not assigned tasks.

### 3. AI insights — `#insights`

Preserve existing deterministic `insights()` commentary and recompute with selected SBU/period/data. Describe its rule-based nature accurately. Link conclusions to evidence. Do not require an API key for baseline functionality. Apply the optional AI contract below only when requested.

### 4. Profit drivers — `#drivers`

Keep Budget, historical Actual year and single-month Previous month comparison choices. Include comparison/actual profit, change and margin-change cards; Comparison insights; profit bridge waterfall; Headwinds; Improvements; Comparison analytics; Per-tonne comparison; Profit bridge detail; expandable Calculation and reconciliation.

Use volume effect = (actual MT − comparison MT) × comparison contribution / comparison MT. Use sales-value/mix = actual sales after VAT − comparison sales after VAT × actual MT / comparison MT. Variable expense effects are negative actual cost less comparison cost scaled to actual volume. Fixed/operating cost effects use signed absolute differences. Derive net other income/expense from EBIT minus operating profit. Show the unexplained reported profit-change residual explicitly.

Require positive comparable tonnes and complete required P&Ls. Otherwise show missing inputs and available comparison tables. Variance percentage uses absolute comparison value; zero/missing denominator stays blank. Do not call mix a pure price effect or cost changes proven efficiency. Driver clicks reveal calculation and exact source cells.

### 5. Product economics — `#products`

Keep gross-sales comparison, concentration, secondary share, product count and negative-spread cards. Include product table with net revenue, sales MT, revenue share, selling value/kg, cost/kg, spread/kg and comparison achievement. Keep Product detail, chart-year/global-period linkage and duration selectors for all/selected/last three/last six months.

Include selling-value/cost chart, production/sales chart, review questions, monthly detail, source dialogs and expandable pricing-source comparison/reconciliation. Match products only through existing explicit label normalization; retain differently named products separately. Prefer income revenue after matched product VAT divided by sales kg; otherwise use supplied price rate. Cost/kg is supplied, not an invented allocation. Multi-month rates require complete volume-weighted matched observations. Never sum rates. Spread is indicative, not product NPAT. Production minus sales is a flow gap, not closing stock. Pricing-only rows may overlap and must not be blindly consolidated.

### 6. Break-even & targets — `#breakeven`

Keep desired margin input and What-If link. Include net break-even revenue/tonnes, margin of safety and target-margin revenue cards; estimated/desired profit chart; sales/cost gap table; capacity context; assumptions.

Preserve `breakModel()`: revenue after VAT before commission; contribution/revenue; fixed burden = contribution − NPAT; current company value/tonne for volume conversion; target net margin after commission. Hold source mix, variable ratios, fixed costs, finance, other income and tax constant. Keep denominator checks and blank volume-only break-even for nonpositive contribution.

### 7. Profit & cash quality — `#cashquality`

Keep OCF, cash after capex, unavailable working-capital cash effect and net debt cards. Include Why cash differs from profit, profit/OCF trend, Cash funding and uses and Cash-quality review. Preserve six funding/uses lines: operating, investing, financing, intercompany net within financing, net movement and closing cash.

Use direct-method CFS. Unsupported indirect bridge components remain blank. OCF minus NPAT is an unallocated difference, not an inferred working-capital cause. Cash after PPE/CWIP payments is not distributable cash.

### 8. Departments — `#departments`

Keep comparison, total/per-tonne basis and financial-group selector. Include sales achievement, production, department spend and margin cards; comparison table; selected-group spending and intensity trends; matched-year scorecard.

Preserve materials, factory, maintenance, logistics, sales/marketing including commission, administration, depreciation/rent and finance groups using exact `departmentGroups` mappings. Administration = opex minus sales/distribution. Count subtotals once. These are financial expense groups, not proven departmental ownership; lower spend is not proof of efficiency.

### 9. Target vs achievement — `#achievement`

Keep achievement cards and target table for net sales, sales MT, production and NPAT. Include department budget use, actual/budget amounts, cost/sales and cost/MT. Retain horizontal percentage bars; cap visual fill at 100% while showing exact over-budget percentage in red. Zero/missing budgets yield blank ratios.

### 10. Cost analysis — `#cost`

Keep comparison/basis, sales after VAT, all-in cost, NPAT and tonnes cards; department spending chart; cost composition; sales-to-profit waterfall; group selector; monthly expense-head chart; ledger details and source clicks. Include tax in all-in costs with other income/expense separate. Never add supporting ledger rows again to parent totals. Waterfall ends at reported NPAT with explicit residual if necessary.

### 11. Cash & working capital — `#cash`

Use final `cash-analysis.js`. Preserve cash/flow/liquidity cards; monthly OCF/CFS/BS cash trends; funding/uses; cash reconciliation; working-capital balances; liquidity ratios; opening-to-closing balance movements; debt/funding; management observations; expandable full CFS.

Calculate NWC = CA − CL, current ratio = CA/CL and investment-excluded ratio = (CA − investments)/CL. Label cash-plus-receivables coverage explicitly. Debt includes bank loans and current/noncurrent leases; net debt deducts cash only. Do not assume investments liquid. Do not infer DSO, DPO or cash-conversion cycle without suitable underlying schedules. Balance movements are not cash effects.

### 12. What-If planning — `#scenario`

Keep planning month, actual starting pattern, Reset and CSV export. Include linked volume/value per tonne/revenue; expandable starting values/ratios; department percentage/fixed-lakh levers; other income/expense; fixed/sales/positive-PBT tax modes; desired margin; scenario P&L; recorded-month comparison and year-end outlook.

Preserve `makePlan`, `planResult` and `planningOutput`. Store assumptions by SBU/year/month, separate from source Actual/Budget. When both other fields are unavailable, retain source net other amount. Retain reconciliation adjustment so baseline reproduces source NPAT. Future months stay blank until explicitly planned; incomplete years are not full-year forecasts.

### 13. Statement detail — `#statements`

Keep comparison and curated income statement Actual/Comparison/Variance table. Preserve exact `statementView()` row order: volumes, gross sales, VAT, commission, net sales, variable/fixed costs, operating expenses, EBIT, finance detail, PBT, tax and NPAT. Source clicks show original cells. Explain subtotals without double counting.

### 14. SBU comparison — `#group`

Keep expanded analysis over identical months. Include coverage, highest available margin, loss count and positive-OCF count cards; clickable sales/NPAT bars; profitability/budget table; efficiency/cost table; cash/liquidity table; capital/funding/working-capital table; multi-SBU monthly sales/profit charts; management priorities and completeness table.

Cover sales/budget/achievement/variance, NPAT/budget/variance, margin, sales/production MT, volume achievement, capacity use, contribution/gross/operating margins, materials/sales, all-in cost/MT, OCF, cash after capex, OCF/sales, cash, NWC, both current ratios, inventory, receivables, investments, debt/net debt, interest cover and period ROCE.

Exclude missing metrics from rankings. Signals include largest sales, best available margin, losses, sales shortfalls, negative NWC and OCF below positive profit. Name/bar clicks open that SBU's overview. These are comparisons, not consolidated group accounts: eliminations are unavailable. Explain sector/mix limitations on cross-company per-tonne comparisons.

### 15. Financial reconciliation — `#reconcile`

Preserve available BS equation, BS/CFS cash, cash rollforward, cash classification, SCE/BS equity and SCE/income-profit checks with evidence. Expose differences without changing figures. Missing checks are unavailable, not passed. Retain equity data despite removal of its standalone menu. Flag identical supplied equity data across SBUs for review rather than invent replacements.

### 16. Data Upload — `#upload`

Keep upload exclusively here. Provide existing destination SBU, Detect SBUs and Add new SBU with name/code. Segment choices: Multiple/detect, Income statement, Expense break-up, Balance sheet, Cash-flow statement, Changes in equity, Net Sales Price and combined financial statements. Allow multiple XLSX files simultaneously.

Keep detected-sheet review dialog, Import all files, Cancel and validation errors. Validate SBU identifiers and selected segment before an atomic batch import. Replace only imported SBU/segment datasets, retaining unrelated books/SBUs. Explain full-segment replacement and including all periods to retain. Preserve browser storage and refresh behavior.

Provide blank IS, Break Up, BS, CFS, SCE and AGL/AIL/ACL pricing XLSX downloads. Keep financial cells and identifiers blank, source headers/labels intact. IS/Break Up use Budget/Actual pairs; BS/CFS monthly values; SCE dated opening/movements/closing and equity components; pricing product/measure/monthly Excel dates without Budget/Actual split. Preserve SCE/SEC/CSE recognition and cached formula-value handling.

Do not restore the removed SBU-count/browser-saved/refreshed summary banner. Do not restore Sources & reporting notes, Balance sheet or Changes in equity standalone menus. Retain underlying books and analysis. Hide global financial toolbar on upload; do not put file pickers elsewhere.

## Data and formula rules

Use portfolio SBU IDs with name/code and books `income`, `detail`, `balance`, `cashflow`, `equity`, `pricing`. Preserve file, worksheet, row/cell, label, year/month and Actual/Budget provenance. Null is not zero. Strict totals require every selected monthly input; never silently report partial totals. Ratios use aggregated numerator/denominator, not average monthly percentages.

Canonical income rows: 5 capacity; 12 production; 19 sales MT; 27 gross; 28 VAT; 29 after VAT; 30 commission; 31 net sales; 32 variable COGS; 33 materials; 34 labour; 35 electricity; 36 gas; 37 diesel; 38 maintenance; 39 other variable factory; 40 transport; 41 contribution; 42 fixed; 43 salary; 44 other fixed; 45 depreciation/rent; 46 gross profit; 47 opex; 48 admin; 49 asset loss; 50 sales/distribution; 51 operating profit; 52 other income; 56 other expense; 60 EBIT; 61 finance including WPPF; 62 interest; 63 WPPF; 64 FX; 65 PBT; 66 tax; 67 NPAT. Resolve source label variations through normalization, especially Factory Rent/FRESCO Rent; do not assume uploaded raw row positions match canonical IDs.

BS stocks use the final selected month. CFS flows sum selected months; opening cash uses first month, closing cash last month. Require contiguous periods for opening/closing rollforwards and average capital employed. Capital employed = assets − current liabilities; average opening/closing balances; period ROCE = operating profit/average employed capital, not annualized. Interest cover requires positive interest denominator. Keep exact baseline definitions and explicit denominators.

Preserve historical Budget/Actual labels and source reconciliation residuals. Do not infer product net profitability, expense ownership, operational causation, indirect cash adjustments, approved targets or industry benchmarks from missing evidence.

## Optional generative AI insights

No API key is needed for baseline calculations or deterministic insights. Add generative interpretation only when requested and configured.

- Keep credentials in server-side environment secrets. Never put keys in this skill, HTML, browser JavaScript, localStorage, git, exports or logs. Use hosting secret configuration, not source-code entry.
- Add a server-side insights endpoint accepting selected SBU/period, computed metrics, comparison deltas, coverage, reconciliation differences and source references. Send only necessary data.
- Keep arithmetic deterministic. Ask the model for structured findings with title, observation, metric references, evidence, uncertainty and suggested review action. Restrict it to supplied evidence and distinguish observations from hypotheses.
- Validate referenced metrics and numerical claims against the payload; omit unsupported claims. Label generated interpretation separately from calculated results.
- Cache by SBU, periods, data version and model configuration. Invalidate after upload and discard stale responses after context changes.
- Provide loading, retry and error states without blocking finance menus. Fall back to deterministic insights for absent key, timeout, quota or provider failure. Keep footer connection status accurate.
- Preserve access rules; do not introduce public data access, external enrichment or automated messages as side effects.

## Acceptance checks

1. Check all 16 final routes, selectors, expandable panels, legends, exports, source links and dialogs against bundled baseline. Confirm removed menus stay absent.
2. Exercise every view for AGL, AIL, ACL and a newly imported SBU. Verify active indicator, destination and scenario isolation.
3. Test all-year, individual-year/month and rolling cross-year filters, common SBU months, stock/flow treatment and noncontiguous-period blanks.
4. Test zero, null, missing months, missing comparison, negative profit and zero denominator. No NaN/undefined, fabricated zero or missing-value ranking.
5. Reconcile driver totals to reported profit change, waterfall to NPAT, scenario baseline to source NPAT and financial checks to cells. Retain visible residuals.
6. Test multi-file import, wrong SBU/segment rejection, cancel, replacement scope, persistence, refresh and eight template downloads.
7. Verify visible pointer/keyboard focus, correct tooltip values/units, chart gaps, legend toggles and source clicks. Check responsive layout, print, sorting/search and browser history when browser testing is available.
8. For AI, test missing secrets, failure fallback, stale response isolation and unsupported-claim rejection; verify no client-side secret leakage.
9. Report tests actually performed. Source inspection or VM tests do not constitute visual browser verification. Preserve site access settings during deployment.
