---
id: 7
title: Implement a reference calculation notebook
type: feature
status: done
milestone: v0.1
assignee: Oddur Sigurdsson
depends_on:
- 5
- 6
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: m
area: methodology
---

## Problem

The written formula needs an inspectable implementation that exposes each
transformation before production abstractions hide mistakes.

## Proposal

Create a small reference notebook that loads pinned source snapshots, cleans
and aligns them, rebases both components, calculates PPG, and plots the result.
Treat it as an explanatory oracle, not the production pipeline.

## Acceptance criteria

- [x] Every transformation is visible and accompanied by units and rationale.
- [x] The notebook runs from a clean environment against pinned local inputs.
- [x] At least three hand-calculated quarters agree with the notebook output.
- [x] Intermediate market and paycheck component series are retained for inspection.
- [x] A compact fixture is exported for production parity tests.

## 2026-09-13

Implemented an offline, standard-library Jupyter notebook that exposes source loading, Treasury reconstruction, monthly compounding, quarterly alignment, rebasing, invariant checking, six-decimal serialization, and SVG plotting. It reproduces three independent 50-decimal hand calculations byte-for-byte and exports the compact production parity fixture under build/reference.
