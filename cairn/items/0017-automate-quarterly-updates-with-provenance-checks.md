---
id: 17
title: Automate quarterly updates with provenance checks
type: feature
status: backlog
milestone: v0.3
depends_on:
- 11
- 13
- 14
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: m
area: automation
---

## Problem

Manual updates will drift, while fully automatic publication can amplify an
upstream revision or malformed response into a false headline number.

## Proposal

Add a scheduled and manually runnable GitHub Actions workflow that retrieves
sources, validates provenance and freshness, rebuilds the series, runs tests,
and prepares a reviewable change. Keep publication gated on passing checks and
human review whenever historical values move beyond the declared tolerance.

## Acceptance criteria

- [ ] The workflow supports both a quarterly schedule and manual dispatch.
- [ ] It records exact source identifiers, retrieval times, and checksums.
- [ ] It refuses incomplete, stale, duplicate, or structurally changed source data.
- [ ] It summarizes the new reading and every changed historical observation.
- [ ] Material revisions require review rather than publishing directly.
- [ ] Re-running for the same release is idempotent and does not create duplicate updates.
