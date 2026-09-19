---
id: 28
title: Refine frontend density and type ramp
type: feature
status: done
milestone: v0.3
assignee: Oddur Sigurdsson
depends_on:
- 27
created: 2026-09-18
updated: 2026-09-18
priority: p1
effort: s
area: publishing
---

## Problem

The first static interface is visually confident but oversized and vertically loose for a compact economic indicator. Its headline, reading card, section spacing, and resource cards consume more space than the information requires.

## Proposal

Refine the existing design system toward a minimalist, slightly smaller and denser presentation. Establish an explicit fluid type and spacing ramp, reduce decorative weight, tighten component dimensions, and preserve readable line lengths and clear grouping across desktop and mobile.

## Acceptance criteria

- [x] The stylesheet defines and consistently uses a compact type and spacing ramp.
- [x] The hero, current-reading card, sections, component panels, and resources are materially denser without crowding.
- [x] Shadows, fills, borders, and accents are restrained into a minimalist hierarchy.
- [x] Desktop and mobile layouts retain legible line lengths, touch targets, focus states, and visual grouping.
- [x] The generated page remains canonical, dependency-free, and fully covered by repository checks.
- [x] A rendered visual review confirms the intended density and hierarchy.
