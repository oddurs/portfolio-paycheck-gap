---
id: 23
title: Release PPG Index 1.0
type: chore
status: backlog
milestone: v1.0
depends_on:
- 20
- 21
- 22
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: s
area: release
---

## Problem

The project needs a stable point that users can cite with confidence rather
than treating every default-branch update as an interchangeable version.

## Proposal

Cut 1.0 only after governance and independent replication are complete. Bind
the stable methodology, full series, source manifest, generated artifacts,
replication report, and software release under one versioned record.

## Acceptance criteria

- [ ] All earlier milestone exit criteria and all 1.0 dependencies are complete.
- [ ] Independent replication agrees within tolerance and remaining caveats are disclosed.
- [ ] The tagged release rebuilds successfully in a clean environment.
- [ ] DOI-ready citation metadata and immutable artifact checksums are published.
- [ ] README, Pages, dataset, methodology, and release all identify version 1.0 consistently.
