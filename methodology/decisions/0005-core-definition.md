# PPG core definition

Status: accepted for methodology v0.1

Cairn item: 0005

Decision date: 2026-09-13

## Question

The Portfolio–Paycheck Gap Index (PPG) answers one question:

> How has the cumulative return to a representative US stock-market investment
> changed relative to the median full-time paycheck?

It compares growth factors, not the dollar levels of a portfolio and a
paycheck. It is a descriptive index, not a claim about what either level should
be.

## Canonical formula

For quarter `t`, let:

- `M_t` be the nominal value at the close of the final trading day of quarter
  `t` of one unit invested in the canonical broad US equity gross total-return
  benchmark, with cash distributions reinvested;
- `W_t` be the seasonally adjusted quarterly average of nominal median usual
  weekly earnings for US full-time wage and salary workers age 16 and older;
- `b` be the base quarter, 1980 Q1.

Define the rebased components:

```text
MARKET_t   = 100 × M_t / M_b
PAYCHECK_t = 100 × W_t / W_b
```

The headline index is:

```text
PPG_t = 100 × MARKET_t / PAYCHECK_t
```

Equivalently:

```text
PPG_t = 100 × (M_t / M_b) / (W_t / W_b)
```

This equivalence is a required calculation invariant.

## Language-independent pseudocode

```text
INPUT market observations, paycheck observations
CONSTANT base_quarter = 1980-Q1

REQUIRE one complete market observation and one complete paycheck observation
        for every published quarter
REQUIRE every input value is finite and strictly greater than zero
REQUIRE base_quarter exists in both inputs

market_base   := market value for base_quarter
paycheck_base := paycheck value for base_quarter

FOR EACH quarter present and complete in both inputs, ordered ascending:
    market_component   := 100 * market_value[quarter] / market_base
    paycheck_component := 100 * paycheck_value[quarter] / paycheck_base
    ppg                := 100 * market_component / paycheck_component

    EMIT quarter,
         market_component rounded only for storage,
         paycheck_component rounded only for storage,
         ppg rounded only for storage
END
```

Calculations use unrounded inputs and intermediates. Comparisons and changes
are calculated from unrounded values, not from display values.

## Market boundary

The market concept is the gross total return of a passive, broad US public
equity portfolio:

- common equity of US-domiciled companies listed on major US exchanges;
- weighted by investable or float-adjusted market capitalization;
- regular cash distributions reinvested on the benchmark provider's declared
  effective date;
- before investor taxes, fund expenses, transaction costs, and tracking error;
- no leverage and no external contributions or withdrawals.

It excludes non-US equity, private equity, bonds, cash, housing, pensions, and
the distribution of actual household portfolios. It represents the return to
owning the market, not the wealth of a typical household.

The source decision may choose an existing benchmark or a reproducible return
series only if it satisfies this conceptual boundary. The exact canonical
series and any unavoidable deviations belong to the source decision in Cairn
item 0006; changing that series after v0.1 is a methodology change, not a silent
data-provider swap.

## Paycheck boundary

The paycheck concept is the quarterly median of usual weekly earnings for
civilian US wage and salary workers who:

- are age 16 or older;
- usually work at least 35 hours per week at their sole or principal job; and
- receive wages, salaries, commissions, tips, payment in kind, or piece rates.

Earnings are before taxes and deductions. They include usual overtime,
commissions, and tips at the principal job. Earnings reported for another time
period are converted to a weekly equivalent.

The measure excludes part-time workers, self-employed workers, employer-paid
benefits, capital income, transfers, secondary-job earnings, household size,
and people without wage or salary work. It is a median across the workers in
each quarter, not a panel following the same people through time. Workforce
composition changes can therefore move the series.

These boundaries follow the Bureau of Labor Statistics definitions for the
Current Population Survey usual-weekly-earnings release. BLS notes that the
median is estimated from grouped observations and that changing subgroup
weights or clustering near the median can affect movement in the overall
series.

## Time and alignment rules

- **Frequency:** calendar quarter.
- **Base:** 1980 Q1 equals 100. The preceding 1979 observations, if available,
  may appear in the dataset with values calculated against the same base.
- **Market timestamp:** official benchmark close on the final eligible US
  trading day of the quarter.
- **Paycheck timestamp:** seasonally adjusted average of the three monthly CPS
  samples represented by the published quarterly observation.
- **Label:** the calendar quarter, stored as `YYYY-QN`; any machine date is the
  calendar quarter end and does not imply that earnings were measured only on
  that date.
- **Release rule:** publish a quarter only when both canonical observations are
  complete. Do not interpolate, extrapolate, or carry a value forward.
- **Missing latest quarter:** retain the prior public reading and mark it stale;
  never relabel it as current.
- **Missing historical quarter:** fail the canonical build. A separately
  labeled experimental series may bridge gaps but cannot replace the headline.
- **Duplicate, nonfinite, zero, or negative input:** fail the build.
- **Revisions:** recompute affected history from the recorded source vintage
  and disclose changed published observations. Detailed revision thresholds
  are deferred to the v1.0 revision policy; until then, every historical change
  requires review.

The end-of-quarter market observation and quarterly-average paycheck measure
are intentionally different summaries. One is the value of an investment at
the reporting date; the other is the best available level of a typical weekly
paycheck during that reporting period. Sensitivity to this convention must be
tested in Cairn item 0008.

## Inflation treatment

The headline is calculated from nominal market and paycheck series. This does
not make it an inflation forecast or a comparison of nominal dollars. A common
positive price deflator `C_t` cancels from the ratio:

```text
((M_t / C_t) / (M_b / C_b)) / ((W_t / C_t) / (W_b / C_b))
= (M_t / M_b) / (W_t / W_b)
```

Using nominal inputs therefore avoids adding a redundant source and its
revisions. Optional real-dollar component charts may deflate both components by
the same CPI-U series, but they cannot alter headline PPG.

## Precision

- Validate and calculate using IEEE 754 binary64 or higher precision.
- Do not round source values or intermediate results.
- Store component and headline levels to six decimal places using round to
  nearest, ties to even.
- Display the headline to one decimal place and percentage changes to one
  decimal place, derived from unrounded levels.
- Treat a difference no greater than `0.0000005` index point as equal at the
  canonical six-decimal storage precision.

## Interpretation

`PPG_b` is exactly 100 before display rounding.

- **Above 100:** since 1980 Q1, the market total-return growth factor is larger
  than the median-paycheck growth factor.
- **Equal to 100:** the two growth factors are equal relative to 1980 Q1.
- **Below 100:** since 1980 Q1, the median-paycheck growth factor is larger than
  the market total-return growth factor.
- **A value of 150:** the market growth factor is 1.5 times the paycheck growth
  factor since the base quarter. It does not mean stocks or workers are 50%
  overvalued or undervalued.
- **Change between any two quarters `s` and `t`:** use
  `100 × (PPG_t / PPG_s - 1)` percent. Subtracting index points is not a
  percentage change.

A rising PPG can result from market gains, paycheck declines, or both. A falling
PPG can result from market losses, paycheck gains, or both. Interpretation must
show the component movements before offering explanations. The index does not
assign causal weight to policy, productivity, bargaining power, demographics,
or market sentiment.

No qualitative bands such as `balanced`, `stretched`, or `worker-led` are part
of v0.1. The base value is a scaling convention, not an economic equilibrium or
normative target.

## Claims outside scope

PPG is not:

- a stock valuation or market-timing signal;
- a recession or return forecast;
- a cost-of-living or affordability index;
- a measure of household wealth, portfolio ownership, or retirement readiness;
- a complete measure of income, wealth, or economic inequality;
- a measure of labor's share of national income, productivity, or compensation;
- evidence that a median worker could have earned the market return; or
- a statement that a higher or lower reading is socially optimal.

## Normative references

- US Bureau of Labor Statistics, [Usual Weekly Earnings Technical
  Note](https://www.bls.gov/news.release/wkyeng.tn.htm). Defines the CPS sample,
  usual weekly earnings, median construction, wage and salary workers,
  full-time workers, constant-dollar treatment, reliability, and seasonal
  adjustment.
- S&P Dow Jones Indices, [Methodology
  Matters](https://www.spglobal.com/spdji/en/research-insights/index-literacy/methodology-matters/).
  Distinguishes price return from total return and explains reinvested cash
  distributions. This reference defines the return concept; it does not decide
  the licensed canonical source.
- S&P Dow Jones Indices, [S&P U.S. Indices
  Methodology](https://www.spglobal.com/spdji/en/methodology/article/sp-us-indices-methodology/).
  Describes broad US equity universes and float-adjusted market-cap weighting.

## Consequences

The definition favors a legible comparison over a model of lived household
finances. It deliberately compares an investable market return with a worker
earnings statistic even though they describe different populations. That
asymmetry is the subject of the index, but it also limits the claims the project
can make.

The base quarter changes the numerical scale, not movements or period-to-period
relative growth. Total return is required because omitting distributions would
systematically omit part of the reward to owning equities. Seasonally adjusted
earnings are required because the public series is quarterly and intended for
quarter-to-quarter comparison.
