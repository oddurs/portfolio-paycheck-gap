---
id: 20
title: Adopt a methodology and source-revision policy
type: docs
status: backlog
milestone: v1.0
depends_on:
- 19
created: 2026-09-13
updated: 2026-09-13
priority: p1
effort: m
area: governance
---

## Problem

Official data revisions and better methodological choices are inevitable. If
they are handled ad hoc, users cannot tell a corrected observation from a
redefined index.

## Proposal

Define separate procedures for routine source revisions, source corrections,
calculation bugs, source substitutions, and methodological changes. State when
history is restated, when a new methodology version is required, and how old
releases remain discoverable.

## Acceptance criteria

- [ ] Each revision class has an approval, versioning, disclosure, and republication rule.
- [ ] Numerical tolerances distinguish routine drift from review-required changes.
- [ ] Methodology changes require parallel old/new series before adoption.
- [ ] Corrections preserve an audit trail and never rewrite tagged releases silently.
- [ ] Source discontinuation and emergency-update procedures are included.
