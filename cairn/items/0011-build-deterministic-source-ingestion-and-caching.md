---
id: 11
title: Build deterministic source ingestion and caching
type: feature
status: done
milestone: v0.2
assignee: Oddur Sigurdsson
depends_on:
- 6
- 10
created: 2026-09-13
updated: 2026-09-17
priority: p0
effort: m
area: data
---

## Problem

Live APIs change, revise history, time out, and occasionally return plausible
but incomplete data. Without raw snapshots, an old release cannot be explained
or reproduced.

## Proposal

Implement adapters for the canonical sources that validate response shape and
coverage before storing immutable snapshots. Pair each snapshot with source
URL, series identifier, retrieval time, release period, checksum, and parser
version. Permit the rest of the build to run offline from a selected snapshot.

## Acceptance criteria

- [x] Each source adapter validates identifiers, units, dates, uniqueness, and expected coverage.
- [x] Raw responses are cached without lossy transformation and named deterministically.
- [x] A provenance manifest records retrieval metadata and cryptographic checksums.
- [x] Re-running against the same snapshots produces byte-identical normalized inputs.
- [x] Partial, malformed, or unexpectedly revised responses fail before publication.
- [x] The calculation can run without network access once snapshots exist.

## 2026-09-17

Validated 2026-09-17: the committed 4156e87c2524a9ce snapshot preserves exact raw responses and covers market 1926-01..2025-12, Treasury 1934-01..2026-08, and paycheck 1979-Q1..2026-Q2. Offline replay is byte-identical; 16 tests and all repository gates pass, including malformed, tampered, duplicate, identity, and revision-quarantine cases.
