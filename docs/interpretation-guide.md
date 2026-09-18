# Interpreting the Portfolio–Paycheck Gap Index

This guide explains how to compare and describe PPG readings without assigning
the index claims it cannot support. The versioned
[methodology](../methodology/v0.1.md) remains authoritative if a summary here
ever conflicts with it.

## The question PPG answers

PPG asks how the cumulative growth of a broad US stock-market investment has
changed relative to the growth of the median full-time paycheck since 1980 Q1.
It divides one rebased growth factor by another:

```text
PPG = 100 × market growth factor / paycheck growth factor
```

The numerator describes a hypothetical passive market investment with
distributions reinvested. The denominator is the BLS cross-sectional median of
usual weekly earnings for full-time wage and salary workers. These are distinct
concepts and populations. PPG does not measure the portfolio holdings of the
workers represented by the earnings series.

## Levels: 100, above 100, and below 100

The index equals 100 in 1980 Q1 by construction. That base is a measuring
reference, not an estimate of equilibrium or fairness.

Suppose the market component has risen from 100 to 300 while the paycheck
component has risen from 100 to 200. Then:

```text
PPG = 100 × 300 / 200 = 150
```

A reading of 150 says the market growth factor is 1.5 times the paycheck growth
factor since the base quarter. It does not say that the market rose 150%, that
pay fell, or that either series is mispriced.

If the market component were 160 and the paycheck component were 200, PPG
would be 80. The market may still have grown in absolute terms; it simply grew
0.8 times as much as the paycheck over the selected span.

The current published reading is 4,217.4 for 2025 Q3. Its components are:

| Component | Index value | Growth factor since 1980 Q1 |
| --- | ---: | ---: |
| Market | 20,173.8 | 201.74× |
| Paycheck | 478.3 | 4.78× |
| PPG | 4,217.4 | Market factor is 42.17× the paycheck factor |

The large PPG level is therefore an index scale, not a percent. Saying “PPG is
4,217.4%” would be incorrect.

## Level versus quarterly and annual change

Three published numbers answer three different questions:

| Measure | Comparison | What it answers |
| --- | --- | --- |
| PPG level | Each component versus 1980 Q1 | How far the relative growth paths have diverged since the base |
| Quarter-over-quarter change | Current PPG versus previous quarter | How the relative gap moved in the latest quarter |
| Year-over-year change | Current PPG versus the same quarter one year earlier | How the relative gap moved over four quarters |

For 2025 Q3, PPG is 4,217.4, up 7.6% from 2025 Q2 and 14.0% from 2024 Q3. The
7.6% and 14.0% changes describe movement in the ratio. They are neither the
market return nor paycheck growth alone. PPG can rise because the market rises
faster, because the market falls less, because pay falls, or through some
combination of movements in both components. Inspect the component series
before explaining a change.

## Comparisons that hold up

Good comparisons name both the interval and the quantity:

- “PPG rose 7.6% quarter over quarter in 2025 Q3.”
- “The market growth factor was 42.17 times the paycheck growth factor between
  1980 Q1 and 2025 Q3.”
- “The PPG level was higher in 2025 Q3 than one year earlier.”

When comparing arbitrary dates, calculate the percentage change in PPG between
those dates and state the endpoints. Do not subtract index points and label the
result a percent. Do not switch the base quarter merely to obtain a preferred
narrative; a rebased analysis should be visibly labeled and should not replace
the canonical headline series.

Before attributing a movement, compare the market and paycheck components.
PPG by itself establishes relative movement, not its cause.

## Claims the index cannot support

Do not describe PPG as:

- evidence that a median worker held, could have held, or failed to hold the
  represented market portfolio;
- a measure of the wealth, income, consumption, or living standard of a
  particular household;
- proof that stocks are overvalued, paychecks are underpaid, or 1980 represented
  a fair relationship;
- a forecast of returns, recessions, wages, or inequality;
- a cost-of-living or purchasing-power measure; or
- causal evidence about policy, technology, bargaining power, or any other
  proposed driver.

PPG can motivate questions about access to capital growth and labor-market
outcomes. Answering those questions requires evidence beyond this index.

## Population and measurement boundaries

The paycheck series covers civilian US wage and salary workers age 16 or older
who usually work at least 35 hours per week at their sole or principal job. It
excludes part-time and self-employed workers, people without wage or salary
work, benefits, capital income, transfers, household size, and secondary-job
earnings. Because it is a changing cross-sectional median, changes can reflect
who is working as well as changes in individual pay.

The open market proxy is a value-weighted portfolio of common, primary
securities on main US exchanges, classified by exchange country. It is not a
record of household portfolios. The total return reconstructs a risk-free leg
from a 3-month Treasury-bill yield and therefore differs from an exact
float-adjusted retail benchmark after fees and taxes.

Pay is a quarterly average while market wealth is observed at quarter end. BLS
sampling and grouped-data estimation, composition changes, historical
revisions, and irregular market-source refreshes can all affect readings.

## Freshness and revisions

A PPG reading is published only when both source legs are complete for a
quarter. If just the newest paycheck quarter is missing, the previous reading
is retained and marked **stale**; no value is interpolated or carried forward.
The current snapshot is stale at 2025 Q3 because the required BLS observation
for 2025 Q4 was not produced, even though market data extend further.

Source publishers can revise history. Every release therefore names a
methodology version and immutable snapshot ID. Use the
[provenance record](../public/data/provenance.json) to identify retrieval times,
checksums, source series, and the latest mutually complete quarter. Comparisons
across releases should first check whether the data vintage or methodology
changed.

## Responsible reporting checklist

Before publishing a PPG claim:

1. Name the observation quarter and whether the reading is stale.
2. Distinguish the index level from its quarterly or annual percentage change.
3. Describe PPG as a ratio of growth factors, not a percentage gap.
4. Inspect both components before explaining a movement.
5. Keep market ownership and paycheck populations conceptually separate.
6. Avoid valuation, welfare, optimality, forecasting, and causal claims.
7. Cite the methodology version and released data snapshot.
8. Preserve source attribution and noncommercial-use terms.

## Data, provenance, and citation

- [Historical observations](../public/data/ppg.csv)
- [Machine-readable latest reading](../public/data/latest.json)
- [Snapshot provenance](../public/data/provenance.json)
- [Methodology v0.1](../methodology/v0.1.md)
- [Data dictionary](../methodology/data-dictionary-v0.1.md)
- [Data licensing and attribution](../DATA_LICENSE.md)
- [Release v0.2.1](../releases/v0.2.1.md)

For the current release, cite:

> Portfolio–Paycheck Gap Index, v0.2.1, methodology v0.1, snapshot
> `2266e3ee4151567d`, 2026-09-18,
> <https://github.com/oddurs/portfolio-paycheck-gap/releases/tag/v0.2.1>.
