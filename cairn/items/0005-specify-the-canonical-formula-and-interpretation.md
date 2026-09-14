---
id: 5
title: Specify the canonical formula and interpretation
type: docs
status: done
milestone: v0.1
assignee: Oddur Sigurdsson
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: m
area: methodology
---

## Problem

The ratio sounds simple, but choices about the market proxy, earnings
population, dividends, inflation, quarter alignment, and rebasing can produce
different results. Leaving those choices implicit would make the headline
number impossible to audit.

## Proposal

Write a normative specification for PPG. Begin with both components rebased to
100 in the chosen base quarter and define the headline as 100 times the market
growth index divided by the paycheck growth index. Specify total-return
treatment, earnings population, frequency, alignment, missing values,
revisions, precision, and supported interpretations.

## Acceptance criteria

- [x] The formula is expressed mathematically and as language-independent pseudocode.
- [x] The market and paycheck concepts each have an explicit inclusion boundary.
- [x] Base period, quarterly alignment, inflation treatment, missing-data behavior, and rounding are decided.
- [x] Readings above, equal to, and below 100 have precise interpretations.
- [x] The document says PPG is not a valuation, affordability, wealth, or complete inequality measure.

## 2026-09-13

Defined PPG as the relative cumulative growth of a broad US equity gross-total-return portfolio and BLS median usual weekly earnings, rebased to 1980 Q1. Nominal inputs are canonical because a common inflation deflator cancels. The base is a scale, not fair value; v0.1 has no normative interpretation bands.
