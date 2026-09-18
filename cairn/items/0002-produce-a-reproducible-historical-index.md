---
id: 2
key: v0.2
title: Produce a reproducible historical index
type: milestone
status: done
assignee: Oddur Sigurdsson
depends_on:
- 1
created: 2026-09-13
updated: 2026-09-17
priority: p2
---

## Outcome

A clean checkout can acquire the declared inputs, calculate every historical quarter, run verification checks, and regenerate the published artifacts with one documented command.

## Exit criteria

- [x] The Python package and CLI install in a clean environment.
- [x] Source snapshots carry provenance and can be replayed offline.
- [x] The production calculation agrees with the frozen reference calculation.
- [x] Tests cover formula invariants, data alignment, and known historical fixtures.
- [x] Versioned CSV, JSON, and SVG outputs are generated deterministically.

## 2026-09-17

Completed by v0.2.0: installable package/CLI, immutable offline source snapshot, reference-matched engine, 35-test reproducibility suite, deterministic CSV/JSON/SVG artifacts, clean-checkout reproduction, tag CI, and checksummed public prerelease.
