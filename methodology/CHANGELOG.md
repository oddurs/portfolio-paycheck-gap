# Methodology changelog

All notable changes to the PPG definition, sources, transformations, and public
field contract are recorded here. Source-value revisions that do not change a
rule belong in release provenance, with their historical effect, rather than a
new methodology version.

## v0.1 — 2026-09-13

Initial accepted definition.

- Defined PPG as the ratio of a rebased broad US-listed equity total-return
  proxy to rebased median usual weekly nominal earnings, with 1980 Q1 = 100.
- Selected JKP's monthly value-weighted US excess-market return, Federal
  Reserve H.15 `RIFSGFSM03_N.M`, and BLS `LES1252881500`.
- Defined the disclosed Treasury-bill accrual proxy used to reconstruct total
  market return and monthly compounding into quarter-end wealth.
- Fixed quarterly alignment, completeness, rounding, revision, stale-reading,
  source-discontinuation, and interpretation rules.
- Restricted JKP-derived PPG data and charts to noncommercial use under CC
  BY-NC 4.0 and adopted the Federal Reserve/BLS attribution notices.
- Published a typed data dictionary, three-quarter reference fixture,
  sensitivity table, revision measurements, and executable conformance checks.
- Declared the additive quarter-over-quarter and year-over-year comparison
  fields emitted by the production engine; the formula and public observation
  schema are unchanged.

Evidence: [core decision](decisions/0005-core-definition.md), [source
decision](decisions/0006-data-sources.md), and [sensitivity
analysis](sensitivity-analysis.md).
