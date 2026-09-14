---
id: 8
title: Test sensitivity, revisions, and edge cases
type: chore
status: done
milestone: v0.1
assignee: Oddur Sigurdsson
depends_on:
- 7
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: m
area: methodology
---

## Problem

An index can tell a persuasive but fragile story if its shape depends on one
proxy, base quarter, data vintage, or timing convention.

## Proposal

Compare plausible market proxies, earnings definitions, base periods,
quarter-end versus quarterly-average alignment, and revised versus previously
published data. Exercise missing releases, duplicate periods, nonpositive
values, and abrupt upstream schema changes.

## Acceptance criteria

- [x] A sensitivity table quantifies the effect of every plausible methodological alternative.
- [x] Base-period changes are shown not to alter relative movements after correct rebasing.
- [x] Materially different proxies are either rejected with reasons or disclosed as limitations.
- [x] Revision behavior and expected historical drift are measured.
- [x] Edge cases have an explicit fail, warn, or transform policy.

## 2026-09-13

Measured eight implementable variants, proved base and common-deflator invariance, and rejected weighting/timing/seasonality alternatives with quantified effects. Compared 1,176 JKP months across pinned legacy/current archives (2.229920% cumulative component drift by 2023 Q4) and an archived/current BLS window (maximum one-dollar revision). Executable checks cover the explicit fail/warn/transform contract.
