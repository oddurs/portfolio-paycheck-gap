---
id: 10
title: Scaffold the Python package and command-line interface
type: chore
status: backlog
milestone: v0.2
depends_on:
- 9
created: 2026-09-13
updated: 2026-09-13
priority: p1
effort: s
area: core
---

## Problem

The calculation needs a conventional, installable home before ingestion and
publication code accumulate around one-off scripts.

## Proposal

Create a modern Python package with separated source, calculation, validation,
and rendering modules. Expose one command that can fetch, build, validate, and
report the index, with narrower subcommands for development and automation.

## Acceptance criteria

- [ ] A clean environment can install the package from the repository.
- [ ] The CLI exposes documented `fetch`, `build`, `check`, and `update` commands.
- [ ] Runtime and development dependencies are pinned through the chosen package workflow.
- [ ] Formatting, linting, and tests have single documented commands.
- [ ] Network access is isolated from calculation and rendering modules.
