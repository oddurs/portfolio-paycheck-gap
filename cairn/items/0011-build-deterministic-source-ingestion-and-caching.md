---
id: 11
title: Build deterministic source ingestion and caching
type: feature
status: backlog
milestone: v0.2
depends_on:
- 6
- 10
created: 2026-09-13
updated: 2026-09-13
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

- [ ] Each source adapter validates identifiers, units, dates, uniqueness, and expected coverage.
- [ ] Raw responses are cached without lossy transformation and named deterministically.
- [ ] A provenance manifest records retrieval metadata and cryptographic checksums.
- [ ] Re-running against the same snapshots produces byte-identical normalized inputs.
- [ ] Partial, malformed, or unexpectedly revised responses fail before publication.
- [ ] The calculation can run without network access once snapshots exist.
