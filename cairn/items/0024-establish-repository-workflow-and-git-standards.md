---
id: 24
title: Establish repository workflow and Git standards
type: docs
status: done
milestone: v0.1
assignee: Oddur Sigurdsson
created: 2026-09-13
updated: 2026-09-13
priority: p0
effort: s
area: governance
---

## Problem

The project is about to make methodological and data choices whose history must
remain reviewable. Without an agreed workflow, work can bypass its Cairn
record, generated roadmap changes can drift, and unrelated decisions can become
entangled in a commit or pull request.

## Proposal

Initialize the repository on `main` and adopt a small trunk-based workflow. One
Cairn item is active at a time; each non-bootstrap change uses an item-scoped
branch, Conventional Commit subject with a Cairn reference, and a focused pull
request. Provide repository-wide text rules, safe ignores, a pull-request
template, and one validation command that checks Cairn state and generated
roadmap consistency.

## Acceptance criteria

- [x] Git is initialized with `main` as the default branch.
- [x] Contribution rules define the Cairn, branch, commit, review, and close sequence.
- [x] One active item at a time is the default and exceptions must be explicit.
- [x] Root attributes, ignores, and editor settings establish a portable baseline.
- [x] Pull requests disclose methodology, data, generated-artifact, and compatibility effects.
- [x] One local command validates Cairn items, roadmap freshness, and Git whitespace.
- [x] Agent instructions preserve these rules for later work.

## 2026-09-13

Adopted a lightweight trunk-based workflow: one active Cairn item, short item-scoped branches after bootstrap, Conventional Commit subjects with [cairn:NNNN], review through focused pull requests, and make check as the stable validation entry point. The bootstrap remains uncommitted until the user explicitly requests a commit.
