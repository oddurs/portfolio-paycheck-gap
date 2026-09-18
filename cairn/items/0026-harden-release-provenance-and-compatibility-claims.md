---
id: 26
title: Harden release provenance and compatibility claims
type: bug
status: done
assignee: Oddur Sigurdsson
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

- [x] Source retrieval and artifact generation timestamps are distinct, truthful, validated, and deterministic for a pinned release.
- [x] Every source manifest records a verified SHA-256 over a documented framed raw-response bundle.
- [x] Unexpected revisions are retained in quarantine while the reviewed current pointer remains unchanged.
- [x] CI passes the full supported Python boundary on 3.11 and 3.13.
- [x] A clean checkout reproduces the corrected v0.2.1 artifacts byte for byte.
- [x] The public v0.2.1 patch release documents the v0.2.0 provenance corrections and passes tag CI plus asset checksum verification.

## 2026-09-17

Released v0.2.1 on 2026-09-17/18 at tag c1cf9b6. Actual source retrieval 2026-09-18T02:57:09Z and artifact generation 02:57:21Z are distinct; normalized values match v0.2.0. Python 3.11/3.13 tag CI run 35301616732 passed, a clean clone passed make reproduce, the GitHub prerelease contains nine assets, and all six declared download checksums passed.
