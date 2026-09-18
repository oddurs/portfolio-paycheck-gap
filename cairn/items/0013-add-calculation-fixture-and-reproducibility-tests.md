---
id: 13
title: Add calculation, fixture, and reproducibility tests
type: chore
status: done
milestone: v0.2
assignee: Oddur Sigurdsson
depends_on:
- 12
created: 2026-09-13
updated: 2026-09-17
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

- [x] Hand-calculated fixtures cover the base quarter and representative later quarters.
- [x] Tests detect off-by-one-quarter joins and omitted total-return distributions.
- [x] Rebase invariance and ratio identities are property-tested or exhaustively fixture-tested.
- [x] An offline end-to-end build matches committed golden outputs.
- [x] Intentional output changes require an explicit golden-data update.
- [x] CI runs the complete suite on every proposed change.

## 2026-09-17

Validated 2026-09-17: 187-row golden history reproduces byte-for-byte from pinned raw responses with networking disabled; shifted-quarter and omitted-return mutations are detected; ratio/rebase identities pass exhaustively across all 187 base choices. make check passes 29 tests locally and GitHub Actions run 35300009111 passed.
