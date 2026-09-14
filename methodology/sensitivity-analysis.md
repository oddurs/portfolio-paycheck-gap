# PPG v0.1 sensitivity and failure policy

Status: accepted for methodology v0.1

Cairn item: 0008

Decision date: 2026-09-13

## Scope

This review tests the alternatives a reasonable implementer could choose while
using the accepted open sources: Treasury conversion, market weighting,
paycheck seasonal/price treatment, market timing, and base quarter. It does not
treat proprietary index data or an unrelated worker population as an
implementable alternative; decision 0006 rejects those on rights or scope.

The quantitative comparison uses the transparent 1980 Q1–Q3 reference window.
It is a mechanics stress test, not an estimate of the maximum difference over
the full history. All PPG levels use 1980 Q1 = 100 unless noted.

## Sensitivity results

| Alternative | Q2 PPG | Q3 PPG | Q3 difference | Q2→Q3 change | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Canonical | 114.257990 | 124.847450 | 0.000000 | 9.268026% | Keep |
| Simple annual yield ÷ 12 | 114.185480 | 124.666752 | -0.180698 | 9.179164% | Reject |
| No risk-free return | 111.590424 | 119.171673 | -5.675777 | 6.793816% | Reject |
| Equal-weight market | 115.877131 | 137.400683 | +12.553233 | 18.574460% | Reject |
| Capped-value-weight market | 117.164374 | 130.821808 | +5.974358 | 11.656644% | Reject |
| Unadjusted nominal paycheck | 115.157659 | 127.751577 | +2.904127 | 10.936240% | Reject |
| Real paycheck with nominal market | 117.809541 | 131.565477 | +6.718027 | 11.676419% | Reject |
| Quarterly-average market wealth | 100.398066 | 111.456137 | -13.391313 | 11.014227% | Reject |

`tests/fixtures/sensitivity/expected-results.csv` contains the exact reviewed
table, and `make methodology-check` reproduces it from pinned inputs.

### Decisions

- The geometric Treasury conversion remains canonical. Dividing the annual
  quote by 12 is close in this short window, but it ignores discount-basis day
  count. Omitting the risk-free leg does not reconstruct a total return and is
  already visibly material within six months.
- Value weighting remains canonical because PPG asks about one passive unit of
  the market. Equal weighting changes the question to a frequently rebalanced
  small-company-tilted portfolio. Capped value weighting limits each stock's
  weight at the NYSE 80th-percentile capitalization and therefore also changes
  the portfolio. The size of both effects makes the market proxy a headline
  limitation, not a footnote.
- Seasonally adjusted nominal earnings remain canonical for quarter-to-quarter
  comparison. The unadjusted series changes both level and movement even in
  this small window.
- Pairing a rounded real-paycheck series with a nominal market series is
  dimensionally inconsistent and produces a visible artifact. Deflating both
  unrounded components by the same positive price index is exactly invariant:
  the deflator cancels. Optional real-dollar displays must therefore use one
  common deflator and cannot feed the headline.
- Quarter-end market wealth remains canonical. Averaging its three monthly
  levels changes the economic timestamp and meaningfully changes the result.
  PPG intentionally compares wealth at quarter end with the BLS quarterly
  paycheck statistic.

## Base-period invariance

Rebasing the canonical reference to 1980 Q2 produces PPG levels
`87.521232`, `100.000000`, and `109.268026` for Q1–Q3. The Q2-to-Q3 movement is
still `9.268026%`, exactly as with the Q1 base at the tested precision.

In general, if `R_t = M_t / W_t`, a base `b` gives
`PPG_t^(b) = 100 × R_t / R_b`. For any two quarters `s` and `t`,
`PPG_t^(b) / PPG_s^(b) = R_t / R_s`; the base cancels. A base change alters
display levels, not relative movement.

## Revision measurements

### JKP market vintage

The legacy JKP object through December 2023 (ZIP SHA-256
`0cdeaee6c4980085fae967d70246a79ed0c7274161ba1a3a1d5eeec8bba78f87`)
was compared with the accepted Python-pipeline vintage (ZIP SHA-256
`8c69cc848ebb447f8c47346a4b3eabed65fac03f0b895b04319f3828e3b6e79f`).
Across all 1,176 overlapping months from January 1926 through December 2023:

- all monthly values differ, partly because the current file carries greater
  precision and partly because the production pipeline/universe changed;
- mean absolute revision is `0.000123317` return, or 1.233 basis points;
- median absolute revision is `0.000054055`, or 0.541 basis point;
- the empirical 95th-percentile absolute revision is `0.000449749`, or 4.497
  basis points; and
- the largest absolute revision is `0.002624009`, or 26.240 basis points, in
  March 1933.

Using the same canonical Treasury proxy and rebasing at 1980 Q1, the current
market component at 2023 Q4 is 2.229920% above the legacy-vintage component
(`14,132.563216` versus `13,824.292525`). In the reference window, the revised
PPG is 0.040800 point higher in Q2 and 0.035118 point higher in Q3. Small monthly
revisions therefore compound into a material long-horizon level change.

The observed distribution is not a future bound. Every new JKP archive hash
requires a full overlap comparison; a changed historical value blocks automatic
publication until reviewed.

### BLS paycheck vintage

The BLS 2025 Q1 archived release was compared with the current 2026 Q2
table/API vintage for 2024 Q1 through 2025 Q1. Four of five paycheck values are
unchanged. 2024 Q1 moved from `$1,135` to `$1,136`, a one-dollar or 0.088106%
revision. Holding the base and market fixed, that lowers PPG for the quarter by
0.088028%.

This small sample agrees with BLS's announced annual seasonal-adjustment
revision behavior, but it is not a bound. A production update records both
vintages and reports the actual point and percentage effect across every
changed quarter.

Sources: JKP's [April 2026 data update](https://github.com/bkelly-lab/jkp-data/discussions/89),
the BLS [2025 Q1 archived release](https://www.bls.gov/news.release/archives/wkyeng_04162025.htm),
and the BLS [current quarterly table](https://www.bls.gov/news.release/wkyeng.t01.htm).

## Edge-case contract

| Condition | Action | Public consequence |
| --- | --- | --- |
| Latest quarter incomplete in any input | Warn; omit incomplete quarter | Retain prior reading and label it stale |
| Missing historical month or quarter | Fail | No canonical artifact |
| Duplicate period | Fail | No arbitrary last/first-value selection |
| Nonfinite, zero, or negative level | Fail | No canonical artifact |
| Monthly market return `<= -1` | Fail | Wealth compounding is undefined/nonpositive |
| Treasury price proxy outside `(0, 1]` | Fail pending methodology review | Negative or malformed discount quotes are not silently transformed |
| BLS `-` placeholder | Transform to missing, then apply gap rule | The marker is never parsed as zero |
| Rows arrive unsorted | Stable sort by period; warn in provenance | Numerical result is deterministic |
| Required field missing or renamed | Fail schema validation | Upstream schema changes cannot shift columns silently |
| Extra upstream field | Warn and ignore by explicit field name | Additive schemas do not break calculation |
| Unexpected series ID, frequency, units, or seasonal flag | Fail identity validation | Prevents a plausible-but-wrong series swap |
| Source archive checksum changes | Quarantine and compare vintages | No publication until revision is accepted |
| Network/source outage | Warn; use verified cache only for reproduction | Never claim a cache as a fresh reading |
| Intermediate rounded before final storage | Fail parity test | Calculations use unrounded values |

The executable methodology check exercises valid input, missing-latest,
missing-history, duplicate, zero, nonfinite, additive-schema,
missing-required-field, and unsupported-negative-yield paths. Production code
must preserve these outcomes rather than inventing recovery behavior.

## Consequences

The headline is robust to base choice and a common deflator, but not to market
weighting or timestamp. Source revisions are individually small in typical
months yet compound over decades. Publications must show both component paths,
name the exact vintage, and avoid causal interpretation of sensitivity
differences.
