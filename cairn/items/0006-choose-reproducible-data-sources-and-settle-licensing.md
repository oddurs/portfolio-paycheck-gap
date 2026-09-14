---
id: 6
title: Choose reproducible data sources and settle licensing
type: docs
status: done
milestone: v0.1
assignee: Oddur Sigurdsson
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: m
area: data
---

## Problem

A convenient market series may be proprietary, unstable, or legally awkward to
redistribute. The earnings series may be revised or expose multiple similar
measures. The project needs sources that support unattended retrieval and
publication of the resulting index.

## Proposal

Evaluate official and openly accessible candidates for total stock returns and
median usual weekly earnings. Record coverage, frequency, revision behavior,
API reliability, redistribution terms, attribution, and a fallback for each
source. Prefer primary publishers and durable machine-readable endpoints.

## Acceptance criteria

- [x] A source decision record identifies the canonical market and earnings series.
- [x] Stable identifiers, endpoints, coverage dates, units, and release cadence are recorded.
- [x] Terms permit the repository to publish its derived CSV, JSON, and chart.
- [x] A fallback and a policy for source discontinuation are documented.
- [x] Small pinned source samples and their checksums can be retrieved and verified.

## 2026-09-13

Selected JKP usa/mkt/monthly/vw excess returns (CC BY-NC 4.0), Federal Reserve H.15 RIFSGFSM03_N.M via FRED TB3MS for a disclosed Treasury accrual proxy, and BLS LES1252881500. The resulting data artifacts are noncommercial; JKP cadence is irregular and stale readings must be labeled. Live retrieval reproduced all pinned fixtures and the accepted JKP ZIP SHA-256 on 2026-09-13.
