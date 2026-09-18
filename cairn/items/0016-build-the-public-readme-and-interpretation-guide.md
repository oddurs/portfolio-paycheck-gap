---
id: 16
title: Build the public README and interpretation guide
type: docs
status: done
milestone: v0.3
assignee: Oddur Sigurdsson
depends_on:
- 9
- 14
created: 2026-09-13
updated: 2026-09-18
priority: p1
effort: m
area: documentation
---

## Problem

The index will be misunderstood if the repository leads with implementation
details or leaves readers to infer what a high number means.

## Proposal

Make the README function as the front page of an economic indicator: one-line
question, current reading, historical chart, three-point interpretation,
formula, sources, limitations, and paths to the data and methodology. Add a
longer guide for responsible comparisons and commentary.

## Acceptance criteria

- [x] The opening screen answers what PPG measures and shows the latest dated reading.
- [x] A reading of 100 and movements above or below it are explained with examples.
- [x] The difference between level, quarterly change, and annual change is clear.
- [x] Non-claims and important limitations appear beside interpretation guidance.
- [x] Data, methodology, provenance, reproduction, and citation links are easy to find.
- [x] No prose implies that the median worker owns the represented portfolio.
