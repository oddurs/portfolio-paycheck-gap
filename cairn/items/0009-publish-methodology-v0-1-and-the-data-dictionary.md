---
id: 9
title: Publish methodology v0.1 and the data dictionary
type: docs
status: done
milestone: v0.1
assignee: Oddur Sigurdsson
depends_on:
- 8
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: s
area: documentation
---

## Problem

Implementation cannot be reviewed against a moving or incomplete definition.

## Proposal

Turn the accepted specification and source decisions into a versioned
methodology document plus a data dictionary for every input, intermediate
column, and public output field.

## Acceptance criteria

- [x] Methodology v0.1 contains the formula, scope, sources, transformations, and limitations.
- [x] The data dictionary defines names, types, units, frequency, nullability, and precision.
- [x] Every normative choice links to its evidence or decision record.
- [x] A changelog begins with the v0.1 definition.
- [x] A reader can independently implement the index using only the published documents.

## 2026-09-13

Published methodology v0.1, its 43-field typed data dictionary, navigation index, implementation checklist, and initial changelog. The document links the accepted core/source/sensitivity decisions, exact reference fixture, rights notice, and executable offline conformance checks; all local links and required sections validate.
