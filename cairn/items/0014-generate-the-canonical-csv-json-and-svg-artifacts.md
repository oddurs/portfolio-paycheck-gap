---
id: 14
title: Generate the canonical CSV, JSON, and SVG artifacts
type: feature
status: done
milestone: v0.2
assignee: Oddur Sigurdsson
depends_on:
- 12
created: 2026-09-13
updated: 2026-09-17
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

- [x] CSV columns and types match the published data dictionary.
- [x] JSON includes value, observation period, comparison changes, methodology version, and provenance reference.
- [x] SVG includes title, units, base level, source note, and accessible text.
- [x] Empty or stale inputs cannot overwrite valid public artifacts.
- [x] Repeated builds from identical inputs are byte-identical except for declared metadata.
- [x] A consistency check proves all artifacts contain the same latest reading.

## 2026-09-17

Validated 2026-09-17: deterministic CSV/latest JSON/provenance JSON/SVG artifacts contain 187 quarters through 2025-Q3 at PPG 4217.405914, all bound to snapshot 4156e87c2524a9ce and methodology 0.1. Byte-identical rebuild, cross-format consistency, accessible SVG, empty-result rejection, and stale-overwrite protection pass in 33 tests and make check.
