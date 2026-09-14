---
id: 19
title: Launch the public indicator and document its first reading
type: chore
status: backlog
milestone: v0.3
depends_on:
- 17
- 18
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: s
area: release
---

## Problem

A public URL without a dated release, explanation, and provenance record leaves
no clear point at which PPG became a published indicator.

## Proposal

Publish the first official quarterly reading with a concise interpretation that
describes what moved without claiming causation. Tag the exact build and verify
all repository, release, and Pages links from an unauthenticated browser.

## Acceptance criteria

- [ ] The release identifies the observation quarter, value, changes, and methodology version.
- [ ] Its narrative distinguishes measured movement from possible explanations.
- [ ] CSV, JSON, SVG, methodology, and provenance are attached or permanently linked.
- [ ] The README and Pages site display the same value as the release.
- [ ] All automated checks pass and the update can be reproduced from the tag.
