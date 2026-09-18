---
id: 15
title: Cut the first reproducible historical-data release
type: chore
status: done
milestone: v0.2
assignee: Oddur Sigurdsson
depends_on:
- 13
- 14
created: 2026-09-13
updated: 2026-09-17
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

- [x] A clean checkout reproduces the committed artifacts with one documented command.
- [x] The release bundles or links the CSV, JSON, SVG, methodology, and provenance manifest.
- [x] The tag identifies exact package and methodology versions.
- [x] Release notes state the coverage period and known limitations.
- [x] Repository and release checks pass from the tagged commit.

## 2026-09-17

Released 2026-09-17: tag v0.2.0 at aedba20 passed GitHub Actions run 35300935203; GitHub prerelease https://github.com/oddurs/portfolio-paycheck-gap/releases/tag/v0.2.0 contains nine assets. A clean remote clone reproduced committed artifacts with make reproduce, and downloaded release assets passed all six declared SHA-256 checks.
