---
id: 12
title: Implement the quarterly PPG calculation engine
type: feature
status: backlog
milestone: v0.2
depends_on:
- 9
- 11
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: m
area: core
---

## Problem

The reference notebook is intentionally explanatory; publication needs a small,
testable implementation with stable inputs and outputs.

## Proposal

Implement the frozen methodology as pure transformations over normalized input
tables. Emit the market component, paycheck component, headline PPG level, and
declared comparison changes for each quarter. Keep presentation and fetching
outside the calculation boundary.

## Acceptance criteria

- [ ] The engine implements every normative rule in methodology v0.1.
- [ ] Inputs and outputs have validated schemas and explicit units.
- [ ] Results match the reference fixture within the published tolerance.
- [ ] Base-quarter PPG is exactly 100 at the published precision.
- [ ] Duplicate, missing, nonfinite, or out-of-order observations fail clearly.
- [ ] The engine has no network, filesystem-location, or charting assumptions.
