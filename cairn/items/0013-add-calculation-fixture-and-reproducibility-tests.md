---
id: 13
title: Add calculation, fixture, and reproducibility tests
type: chore
status: backlog
milestone: v0.2
depends_on:
- 12
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: m
area: quality
---

## Problem

Ordinary unit tests can miss silent upstream revisions, wrong-quarter joins,
and output drift that changes the published history.

## Proposal

Test mathematical invariants, known fixtures, source validation, temporal
alignment, and complete artifact reproduction. Include an end-to-end test that
runs from pinned raw snapshots with networking disabled.

## Acceptance criteria

- [ ] Hand-calculated fixtures cover the base quarter and representative later quarters.
- [ ] Tests detect off-by-one-quarter joins and omitted total-return distributions.
- [ ] Rebase invariance and ratio identities are property-tested or exhaustively fixture-tested.
- [ ] An offline end-to-end build matches committed golden outputs.
- [ ] Intentional output changes require an explicit golden-data update.
- [ ] CI runs the complete suite on every proposed change.
