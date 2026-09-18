---
id: 18
title: Publish the current reading and history on GitHub Pages
type: feature
status: backlog
milestone: v0.3
depends_on:
- 16
- 17
- 27
created: 2026-09-13
updated: 2026-09-18
priority: p1
effort: m
area: publishing
---

## Problem

Raw repository files are reusable but do not give a general reader a clear,
shareable destination for the indicator.

## Proposal

Deploy the validated static frontend from `public/` through GitHub Pages after
the quarterly update workflow is in place. Keep deployment read-only,
reproducible from the default branch, and independently smoke-tested.

## Acceptance criteria

- [ ] GitHub Pages deploys the exact validated `public/` tree from the default branch.
- [ ] The deployment workflow has least-privilege permissions and pinned third-party actions.
- [ ] CI rebuilds the page and refuses to deploy stale or inconsistent generated HTML.
- [ ] A post-deploy smoke test verifies the page and canonical data endpoints.
- [ ] The public URL is linked from the repository description and README.
- [ ] A clean checkout can reproduce every deployed asset without local-only inputs.
