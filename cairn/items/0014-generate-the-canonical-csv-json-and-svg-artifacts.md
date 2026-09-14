---
id: 14
title: Generate the canonical CSV, JSON, and SVG artifacts
type: feature
status: backlog
milestone: v0.2
depends_on:
- 12
created: 2026-09-13
updated: 2026-09-13
priority: p1
effort: m
area: publishing
---

## Problem

Different consumers need a complete dataset, a tiny current-value payload, and
a chart, but all three must describe the same build.

## Proposal

Generate a stable quarterly CSV, a machine-friendly latest-reading JSON file,
and an accessible SVG history chart from one validated result table. Stamp
artifacts with methodology version, observation date, and source-manifest
identity where the format allows it.

## Acceptance criteria

- [ ] CSV columns and types match the published data dictionary.
- [ ] JSON includes value, observation period, comparison changes, methodology version, and provenance reference.
- [ ] SVG includes title, units, base level, source note, and accessible text.
- [ ] Empty or stale inputs cannot overwrite valid public artifacts.
- [ ] Repeated builds from identical inputs are byte-identical except for declared metadata.
- [ ] A consistency check proves all artifacts contain the same latest reading.
