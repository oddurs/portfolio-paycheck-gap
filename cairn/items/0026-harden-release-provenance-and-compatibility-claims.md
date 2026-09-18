---
id: 26
title: Harden release provenance and compatibility claims
type: bug
status: doing
assignee: Oddur Sigurdsson
claimed: 2026-09-17
depends_on:
- 15
created: 2026-09-17
updated: 2026-09-17
priority: p0
area: quality
---

## Problem

v0.2.0 is reproducible, but its manually pinned source timestamp is not the actual retrieval time, artifact generation time is conflated with retrieval time, the multi-response paycheck checksum algorithm is implicit, rejected revisions are not retained for inspection, and CI does not exercise the minimum supported Python.

## Proposal

Cut a v0.2.1 patch that records honest source and build timestamps separately, defines and verifies framed raw-bundle checksums, preserves quarantined revision candidates without advancing the reviewed pointer, and tests Python 3.11 plus 3.13. Rebuild and republish all provenance-bound artifacts.

## Acceptance criteria

- [ ] Source retrieval and artifact generation timestamps are distinct, truthful, validated, and deterministic for a pinned release.
- [ ] Every source manifest records a verified SHA-256 over a documented framed raw-response bundle.
- [ ] Unexpected revisions are retained in quarantine while the reviewed current pointer remains unchanged.
- [ ] CI passes the full supported Python boundary on 3.11 and 3.13.
- [ ] A clean checkout reproduces the corrected v0.2.1 artifacts byte for byte.
- [ ] The public v0.2.1 patch release documents the v0.2.0 provenance corrections and passes tag CI plus asset checksum verification.
