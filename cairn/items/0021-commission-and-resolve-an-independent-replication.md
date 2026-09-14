---
id: 21
title: Commission and resolve an independent replication
type: chore
status: backlog
milestone: v1.0
depends_on:
- 19
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: l
area: quality
---

## Problem

The same implementation cannot independently demonstrate that the written
methodology is complete or that the published history is reproducible.

## Proposal

Give the public methodology and source identifiers, but not internal code, to
an independent reviewer or clean-room implementer. Compare component and
headline series for every quarter, classify discrepancies, and resolve them in
the specification, data, or implementation.

## Acceptance criteria

- [ ] A second implementation is produced without copying production calculation code.
- [ ] Every quarterly component and headline value is compared at declared precision.
- [ ] Discrepancies are classified and resolved or documented with impact.
- [ ] Ambiguities discovered in the methodology are corrected before 1.0.
- [ ] A signed or attributable replication report is published with enough detail to repeat it.
