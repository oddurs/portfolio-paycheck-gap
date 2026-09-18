---
id: 27
title: Build the static frontend foundation
type: feature
status: done
milestone: v0.3
assignee: Oddur Sigurdsson
depends_on:
- 16
created: 2026-09-18
updated: 2026-09-18
priority: p1
effort: m
area: publishing
---

## Problem

The repository has canonical data and an explanatory README, but no designed, browser-native public surface. GitHub Pages deployment is intentionally blocked on update automation, yet the static interface can be built and validated independently now.

## Proposal

Create a zero-runtime-dependency static site in `public/`, generated deterministically from the canonical JSON, CSV, provenance, and SVG artifacts. Establish semantic HTML, reusable design tokens, responsive layout, accessible states, and local preview/check commands without deploying the page.

## Acceptance criteria

- [x] A deterministic build renders the page from canonical artifacts without recalculating PPG or hand-maintaining headline values.
- [x] The page presents the current level, quarter, quarterly and annual changes, methodology version, and stale status in a coherent visual hierarchy.
- [x] Historical data, provenance, methodology, and reproduction paths are reachable within one interaction.
- [x] Semantic structure, focus treatment, contrast, chart alternatives, mobile layout, and print behavior are intentionally supported.
- [x] The frontend uses no remote assets or runtime JavaScript and remains complete when served as static files.
- [x] Repository checks detect stale generated HTML, broken local links, and violations of the public-page contract.
