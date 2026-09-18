---
id: 10
title: Scaffold the Python package and command-line interface
type: chore
status: done
milestone: v0.2
assignee: Oddur Sigurdsson
depends_on:
- 9
created: 2026-09-13
updated: 2026-09-17
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

- [x] A clean environment can install the package from the repository.
- [x] The CLI exposes documented `fetch`, `build`, `check`, and `update` commands.
- [x] Runtime and development dependencies are pinned through the chosen package workflow.
- [x] Formatting, linting, and tests have single documented commands.
- [x] Network access is isolated from calculation and rendering modules.

## 2026-09-17

Validated on 2026-09-17: make check passes (10 pytest tests plus methodology/reference/docs gates), uv build succeeds, and a clean temporary virtual environment installs the wheel and exposes fetch/build/check/update.
