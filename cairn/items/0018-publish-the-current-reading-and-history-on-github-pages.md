---
id: 18
title: Publish the current reading and history on GitHub Pages
type: feature
status: backlog
milestone: v0.3
depends_on:
- 16
- 17
created: 2026-09-13
updated: 2026-09-13
priority: p1
effort: m
area: publishing
---

## Problem

Raw repository files are reusable but do not give a general reader a clear,
shareable destination for the indicator.

## Proposal

Publish a fast static page sourced only from canonical generated artifacts. It
should show the dated current reading, historical chart, recent movement,
interpretation bands only if justified by methodology, source attribution, and
links to download or reproduce the data.

## Acceptance criteria

- [ ] The page is generated from canonical JSON and SVG rather than duplicate calculations.
- [ ] Current value, observation quarter, recent changes, and methodology version are visible.
- [ ] Historical data and methodology are downloadable within one interaction.
- [ ] The chart and headline remain usable on mobile and with assistive technology.
- [ ] Stale-data status is visible when the expected release window has passed.
- [ ] Deployment is reproducible from the default branch without local-only assets.
