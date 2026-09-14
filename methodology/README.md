# PPG methodology

The current normative specification is [Methodology
v0.1](v0.1.md), accompanied by its [data
dictionary](data-dictionary-v0.1.md) and [changelog](CHANGELOG.md).

The specification consolidates three accepted decision records:

- [core definition](decisions/0005-core-definition.md);
- [canonical data sources](decisions/0006-data-sources.md); and
- [sensitivity and failure policy](sensitivity-analysis.md).

The [reference hand calculations](reference-hand-calculations.md) and
[`ppg_reference.ipynb`](../notebooks/ppg_reference.ipynb) are executable
conformance evidence. Run `make methodology-check` from the repository root.

If a summary conflicts with the versioned methodology, the versioned
methodology controls. A change to a normative rule requires a new Cairn item
and a changelog entry; source data may never redefine the method silently.
