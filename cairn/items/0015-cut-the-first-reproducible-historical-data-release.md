---
id: 15
title: Cut the first reproducible historical-data release
type: chore
status: backlog
milestone: v0.2
depends_on:
- 13
- 14
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: s
area: release
---

## Problem

Having generated files on the default branch does not identify a durable,
reproducible version of the historical series.

## Proposal

Create a tagged pre-public release that binds code, methodology, source
manifest, tests, and generated artifacts. Rebuild the tag in a clean checkout
before declaring the engine milestone complete.

## Acceptance criteria

- [ ] A clean checkout reproduces the committed artifacts with one documented command.
- [ ] The release bundles or links the CSV, JSON, SVG, methodology, and provenance manifest.
- [ ] The tag identifies exact package and methodology versions.
- [ ] Release notes state the coverage period and known limitations.
- [ ] Repository and release checks pass from the tagged commit.
