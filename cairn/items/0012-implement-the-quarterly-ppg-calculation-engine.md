---
id: 12
title: Implement the quarterly PPG calculation engine
type: feature
status: done
milestone: v0.2
assignee: Oddur Sigurdsson
depends_on:
- 9
- 11
created: 2026-09-13
updated: 2026-09-17
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

- [x] The engine implements every normative rule in methodology v0.1.
- [x] Inputs and outputs have validated schemas and explicit units.
- [x] Results match the reference fixture within the published tolerance.
- [x] Base-quarter PPG is exactly 100 at the published precision.
- [x] Duplicate, missing, nonfinite, or out-of-order observations fail clearly.
- [x] The engine has no network, filesystem-location, or charting assumptions.

## 2026-09-17

Validated 2026-09-17: the pure engine produces 187 complete quarters (1979-Q1..2025-Q3), marks the missing 2025-Q4 paycheck as stale, emits QoQ/YoY changes, reproduces all frozen reference components and PPG values at six decimals, and fixes 1980-Q1 exactly at 100.0. All 25 tests and repository gates pass.
