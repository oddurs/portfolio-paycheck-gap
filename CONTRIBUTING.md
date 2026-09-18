# Contributing

PPG treats its methodology, source data, code, and published artifacts as one
reviewable system. Every change begins with a Cairn record of intent and ends
with evidence that its acceptance criteria are true.

## Workflow

1. Run `cairn next` and select one ready item.
2. Claim it with `cairn claim <ID>`. Only one item should be active at a time
   unless parallel work was explicitly agreed in advance.
3. After the bootstrap commit, branch from current `main` using
   `<type>/<item>-<slug>`, such as `docs/0005-index-formula` or
   `feat/0012-calculation-engine`. Use `feat`, `fix`, `docs`, `test`, `chore`,
   or `refactor` as the type.
4. Keep the branch limited to that item. Record durable decisions with
   `cairn note <ID> "..."`; create a new item instead of expanding scope
   silently.
5. Run `make check` and any item-specific validation. Tick only acceptance
   criteria demonstrated by the result.
6. Use `cairn render`, include the resulting `ROADMAP.md` change, and open a
   focused pull request. The item may close after every criterion and required
   check passes.
7. Squash or rebase before merge so `main` remains linear unless preserving
   separate commits materially improves the decision record. Delete the branch
   after merge.

GitHub issues are not the project backlog. Cairn items under `cairn/items` are
the source of truth; a pull request should name its item and link its file.

## Development environment

The project requires Python 3.11 or newer and uses
[uv](https://docs.astral.sh/uv/) for dependency locking and command execution.

```sh
make setup       # install the exact environment from uv.lock
make format      # apply Ruff formatting and safe lint fixes
make lint        # check formatting and lint rules
make test        # run the test suite
make check       # run every local repository gate
```

Runtime code lives under `src/ppg_index`. Remote I/O belongs only in
`ppg_index.sources`; calculation and rendering accept local values and must
remain usable with networking disabled.

Source acquisition writes immutable, content-addressed snapshots. Never edit a
snapshot in place or replace `data/current.json` by hand. Fetch a candidate to
`data/cache`, review any reported historical movement, and only then promote a
new snapshot and its manifest in the Cairn item that explains the change.

## Commits

Use an imperative Conventional Commit subject with a scope when useful, ending
in the four-digit Cairn reference:

```text
docs(methodology): define quarterly alignment [cairn:0005]
feat(index): calculate rebased component ratio [cairn:0012]
```

Keep commits cohesive. Do not mix formatting, dependency updates, or unrelated
cleanup into an item. Commit generated outputs with the source or data change
that produced them. Never commit credentials, local caches, or unreviewed API
responses.

## Review gates

Every pull request must pass `make check` plus the checks declared by its Cairn
item. That command checks both staged and unstaged Git changes. Once Python
tooling exists, `make check` remains the front door and will grow to include
formatting, linting, tests, and deterministic artifact builds.

Changes to the formula, source series, temporal alignment, revision behavior,
or public output schema require explicit methodology or compatibility review.
Unexpected historical data movement must be explained before publication.

## Bootstrap exception

The initial repository structure and these standards may form the first commit
directly on the unborn `main` branch. All later work follows the branch and
pull-request workflow above.
