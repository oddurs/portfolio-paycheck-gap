---
id: 2
key: v0.2
title: Produce a reproducible historical index
type: milestone
status: backlog
depends_on:
- 1
created: 2026-09-13
updated: 2026-09-13
priority: p2
---

## Outcome

A clean checkout can acquire the declared inputs, calculate every historical quarter, run verification checks, and regenerate the published artifacts with one documented command.

## Exit criteria

- [ ] The Python package and CLI install in a clean environment.
- [ ] Source snapshots carry provenance and can be replayed offline.
- [ ] The production calculation agrees with the frozen reference calculation.
- [ ] Tests cover formula invariants, data alignment, and known historical fixtures.
- [ ] Versioned CSV, JSON, and SVG outputs are generated deterministically.
