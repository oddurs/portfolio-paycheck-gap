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

Methodology v0.1 is complete. It freezes the definition, source contract,
licensing boundary, reference calculation, sensitivity analysis, and failure
policy. The production historical series is the next milestone; this repository
does not yet publish a current headline reading.

- [Methodology v0.1](methodology/v0.1.md)
- [Data dictionary](methodology/data-dictionary-v0.1.md)
- [Reference notebook](notebooks/ppg_reference.ipynb)
- [Sensitivity and revision analysis](methodology/sensitivity-analysis.md)
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

## Data use

The selected JKP market data is CC BY-NC 4.0. PPG datasets and charts derived
from it are therefore limited to noncommercial use unless a replacement source
or separate permission is obtained. Federal Reserve and BLS attribution rules
also apply. See [data licensing and attribution](DATA_LICENSE.md).

No license is granted for repository code unless and until a code license is
added explicitly.
