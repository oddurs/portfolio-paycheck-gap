---
id: 3
key: v0.3
title: Publish an automated public indicator
type: milestone
status: backlog
depends_on:
- 2
created: 2026-09-13
updated: 2026-09-13
priority: p2
---

## Outcome

Someone encountering the repository can understand the current PPG reading, inspect its history, download the data, and reproduce the result. Quarterly updates are automated but remain reviewable before publication.

## Exit criteria

- [ ] The README explains the index in under a minute and leads with the current chart.
- [ ] GitHub Pages publishes the current reading, history, interpretation, and methodology link.
- [ ] A scheduled and manually runnable workflow prepares quarterly updates.
- [ ] Failed validation cannot silently publish a new reading.
- [ ] The first public release includes data, provenance, methodology, and a dated interpretation.
