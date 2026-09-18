# Portfolio–Paycheck Gap Index

PPG is a transparent quarterly measure of how the cumulative return to owning
the US stock market has changed relative to the median full-time paycheck.

```text
PPG_t = 100 × (market wealth_t / market wealth_1980-Q1)
            / (median paycheck_t / median paycheck_1980-Q1)
```

A reading above 100 means the market growth factor has outpaced the paycheck
growth factor since 1980 Q1. It is not a valuation signal, forecast, or complete
measure of inequality.

## Project status

Release v0.2.0 is the first reproducible historical series. It contains 187
quarterly observations from 1979 Q1 through 2025 Q3. The latest PPG reading is
`4217.405914` (1980 Q1 = 100), up `7.627364%` quarter over quarter and
`13.979511%` year over year.

The reading is explicitly stale: market data exist for 2025 Q4, but BLS did
not produce the required 2025 Q4 paycheck observation after the federal
shutdown. The build omits that quarter instead of filling it.

- [Methodology v0.1](methodology/v0.1.md)
- [Data dictionary](methodology/data-dictionary-v0.1.md)
- [Reference notebook](notebooks/ppg_reference.ipynb)
- [Sensitivity and revision analysis](methodology/sensitivity-analysis.md)
- [Historical CSV](public/data/ppg.csv)
- [Latest reading JSON](public/data/latest.json)
- [History chart](public/data/ppg.svg)
- [Release notes](releases/v0.2.0.md)
- [Roadmap](ROADMAP.md)

## Validate

Install the exact development environment with
[uv](https://docs.astral.sh/uv/), then run every repository gate:

```sh
uv sync --locked --all-groups
make check
```

To retrieve the live sources and verify their accepted checksums and revision
measurements:

```sh
make source-check
```

The reviewed full-source vintage is committed under [`data/`](data/README.md),
including exact raw responses, normalized inputs, and a SHA-256 provenance
manifest. To acquire a new candidate without changing the reviewed snapshot:

```sh
uv run ppg fetch --cache-dir data/cache
```

The fetch fails on schema, identity, unit, date, coverage, uniqueness, or
overlapping-value changes. A historical revision requires inspection and an
explicit `--accept-revision` run.

The project backlog and milestone state live in plain Markdown through
[Cairn](https://github.com/oddurs/cairn). Run `cairn roadmap` or `cairn next`
to inspect the work.

## Command line

The installed `ppg` command provides four workflow boundaries:

```text
ppg fetch   # retrieve and cache immutable source snapshots
ppg build   # calculate and render from a selected local snapshot
ppg check   # validate snapshots, calculations, and artifacts
ppg update  # fetch, build, and check without automatic publication
```

Run `ppg COMMAND --help` for command-specific paths and options. Fetching is
isolated in `ppg_index.sources`; calculation and rendering remain offline.

Build the canonical dataset, latest-reading payload, chart, and provenance
record entirely from the reviewed local snapshot, then verify that all four
agree byte-for-byte with a fresh calculation:

```sh
uv run ppg build --snapshot-dir data --output-dir public/data
uv run ppg check --snapshot-dir data --artifact-dir public/data
```

`make artifacts` is the short form for the build command.

A clean checkout reproduces and verifies the committed artifacts with one
command:

```sh
make reproduce
```

To fetch current live inputs into an ignored review workspace, then build and
check a local candidate without publishing it:

```sh
uv run ppg update
```

The generated files are `ppg.csv`, `latest.json`, `ppg.svg`, and
`provenance.json`. Publication is atomic and refuses to replace a newer valid
reading with an older input.

## Data use

The selected JKP market data is CC BY-NC 4.0. PPG datasets and charts derived
from it are therefore limited to noncommercial use unless a replacement source
or separate permission is obtained. Federal Reserve and BLS attribution rules
also apply. See [data licensing and attribution](DATA_LICENSE.md).

No license is granted for repository code unless and until a code license is
added explicitly.
