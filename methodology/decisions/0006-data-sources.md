# PPG canonical data sources

Status: accepted for methodology v0.1

Cairn item: 0006

Decision date: 2026-09-13

## Decision

PPG v0.1 uses three inputs:

| Role | Canonical series | Stable identifier |
| --- | --- | --- |
| Equity excess return | Global Factor Data, United States market, monthly, value weighted | `usa / mkt / monthly / vw` |
| Treasury return proxy | Federal Reserve H.15, 3-month Treasury bill secondary-market rate, monthly average, discount basis | `H15/H15/RIFSGFSM03_N.M` (`TB3MS` at FRED) |
| Median paycheck | BLS Current Population Survey, median usual weekly nominal earnings, full-time wage and salary workers age 16+ | `LES1252881500` |

The first two inputs are combined into the canonical market return described
below. This choice makes the complete calculation inspectable and permits
noncommercial publication. It is not a claim that a free source is identical
to a licensed commercial total-return index.

## Market return

### Equity series

The equity input is Jensen, Kelly, and Pedersen (JKP) Global Factor Data's
monthly value-weighted United States market return:

- endpoint:
  `https://jkpfactors-data.s3.amazonaws.com/public/%5Busa%5D_%5Bmkt%5D_%5Bmonthly%5D_%5Bvw%5D.zip`;
- fields used: `location`, `name`, `freq`, `weighting`, `date`, and `ret`;
- units: decimal monthly **excess** return in US dollars; and
- observed coverage at the accepted vintage: January 1926 through December
  2025, inclusive.

`date` is a calendar month-end label. The return covers the publisher's final
eligible observation in that month. PPG compounds the three monthly returns in
a calendar quarter; it never sums returns.

The JKP universe applies its main-observation, main-exchange, primary-security,
and common-stock screens, then weights eligible securities by lagged market
equity. `usa` identifies the country of exchange. This is a broad US-listed
market proxy, but it is not a literal float-adjusted index and does not
guarantee US issuer domicile. Those are explicit deviations from the ideal
boundary in decision 0005.

JKP does not promise a fixed release calendar. The accepted file was published
as part of the April 2026 refresh through December 2025. PPG therefore labels
its latest complete quarter and its source vintage prominently; it must never
imply that the market leg is current when the JKP file is stale.

### Converting excess return to a total-return proxy

JKP publishes excess rather than total market return. For each month `m`, let:

- `e_m` be JKP's decimal value in `ret`;
- `y_m` be the H.15 monthly-average 3-month Treasury bill discount rate in
  percent per year;
- `D_m` be the number of calendar days in the month; and
- `N = 91` be the assumed bill term in days.

Convert the discount quote into a geometrically accrued monthly return:

```text
bill_price_m = 1 - (y_m / 100) × (N / 360)
rf_proxy_m   = bill_price_m ^ (-D_m / N) - 1
market_ret_m = e_m + rf_proxy_m
```

Require `0 < bill_price_m <= 1` and `market_ret_m > -1`. Inputs or outputs that
do not satisfy those conditions fail the build. The quarter-end market wealth
index is the cumulative product of `1 + market_ret_m`; its arbitrary initial
level cancels when PPG is rebased.

The risk-free term is an approximation. JKP constructs its excess return using
its own one-month Treasury/Fama-French risk-free input, while H.15 provides an
average yield rather than the realized return on that exact instrument. The
formula assumes a 91-day bill and smooth accrual during the month; it does not
model mark-to-market price changes or the term structure. This mismatch is
small relative to equity returns but cannot be called exact. Decision 0008
must quantify it against at least a simple `y_m / 1200` conversion and a
zero-risk-free reconstruction.

### Treasury source and delivery

The source series is the Federal Reserve Board's H.15
`H15/H15/RIFSGFSM03_N.M`, “3-month Treasury bill secondary market rate discount
basis.” It is monthly, percent per year, not seasonally adjusted, and is the
average of business-day observations. Its coverage begins in January 1934,
before the equity series.

Automated retrieval uses the Federal Reserve Bank of St. Louis FRED CSV mirror:

```text
https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS
```

FRED identifier `TB3MS` maps to the H.15 identifier above. The Federal Reserve
has announced retirement work on its legacy custom Data Download Program, so
the FRED transport is the more durable no-key endpoint. The publisher remains
the Board of Governors, not PPG or FRED.

## Paycheck series

The paycheck input is BLS series `LES1252881500`, “Employed full time: Median
usual weekly nominal earnings (second quartile): Wage and salary workers: 16
years and over.” It is quarterly, seasonally adjusted, in current US dollars,
and available from 1979 Q1.

Canonical retrieval uses the no-key BLS Public Data API v2:

```text
https://api.bls.gov/publicAPI/v2/timeseries/data/LES1252881500
```

Production requests supply explicit `startyear` and `endyear` values and obey
the current unregistered-request limits. The identifier, rather than the human
title, selects the series. Only periods `Q01` through `Q04` are accepted; annual
averages or placeholder values such as `-` are not observations.

BLS normally publishes the quarterly release in the month following quarter
end. It may omit a quarter: for example, 2025 Q4 was not produced because
October 2025 CPS data were not collected during the federal shutdown. The PPG
completeness rule from decision 0005 applies without exception.

BLS seasonally adjusted quarterly earnings may be revised. BLS says five years
of seasonally adjusted data are revised after each calendar year. Every PPG
build records the retrieval date, retains the raw response, and compares the
new source vintage with the preceding one before publication.

## Rights and attribution

This decision permits publication, but only within the following boundary:

- JKP licenses its distributed data under
  [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Source
  fixtures and PPG CSV, JSON, and charts derived from this market series must
  be attributed, identify modifications, link the license, and be used only
  for noncommercial purposes unless a separate permission or replacement
  source is obtained.
- Federal Reserve `TB3MS` is tagged “Public Domain: Citation Requested” by
  FRED. PPG cites the Board of Governors as source and FRED as retrieval
  service.
- BLS places no end-use controls on API data. Every publication records its
  retrieval date and includes the required statement: “BLS.gov cannot vouch
  for the data or analyses derived from these data after the data have been
  retrieved from BLS.gov.” The BLS logo is not used.

The data and derived-artifact boundary is summarized in the repository's
`DATA_LICENSE.md`. Repository code may be licensed separately; a code license
does not override these data terms. Commercial publication is out of scope for
v0.1 and requires a separately licensed market source.

## Provenance and pinned samples

`tests/fixtures/sources/` contains small canonical extracts around the base
quarter and the newest mutually complete quarter in the accepted vintage.
`SHA256SUMS` pins their exact bytes. Run:

```sh
make source-check
```

The check first verifies local fixture checksums, then retrieves all three
endpoints, selects the declared observations, canonicalizes line endings and
field order, and compares the result byte for byte. It also pins the complete
JKP ZIP at this vintage because its URL is mutable.

A failed online check is a review signal, not permission to overwrite a
fixture. Determine whether the failure is a benign publisher revision, a
schema change, or a compromised/incorrect response; record the new vintage and
its effects before accepting it.

## Fallback and discontinuation policy

Transport fallback does not authorize a source substitution:

- **JKP:** retry the same object and consult the publisher's availability
  manifest and release notes. A locally retained, checksum-verified vintage
  may reproduce old releases but cannot create a newer quarter. If the series
  is withdrawn, stop at the last verified quarter.
- **H.15:** retrieve the same H.15 identifier from the Federal Reserve XML or
  successor service if FRED is unavailable. This is a transport change because
  the underlying series is unchanged.
- **BLS:** use the BLS `le` bulk files or a previously retained raw API response
  for the same series identifier if the API is temporarily unavailable. A
  cached vintage may reproduce history but cannot be presented as newly
  retrieved data.

Any replacement identifier, return definition, universe, seasonal treatment,
or publisher is a methodology change. Open a Cairn decision item, run an
overlap study, calculate the full historical effect, document rights, and
version the methodology before publishing the replacement. Never splice a new
source silently. Until the change is accepted, retain the last valid reading
and mark it stale.

## Alternatives rejected for v0.1

- S&P, Dow Jones, Wilshire, CRSP, and commercial terminal series are clearer
  total-return benchmarks but do not grant this repository a general right to
  redistribute derived index data under their standard public terms.
- Price-only index series omit distributions and violate the total-return
  concept.
- ETF or mutual-fund returns begin too late, include fund expenses and tracking
  error, and substitute a product for the defined market portfolio.
- Unlicensed web aggregators provide weaker provenance and redistribution
  terms than the selected sources.

The selected reconstruction is less cosmetically simple than a proprietary
index ticker, but every transformation and legal constraint is visible.

## Normative references

- JKP, [Global Factor Data downloads](https://jkpfactors.com/data) and
  [documentation](https://jkpfactors-data.s3.amazonaws.com/documents/Documentation.pdf).
- JKP, [data-generation repository and data license](https://github.com/bkelly-lab/jkp-data).
- Federal Reserve Board, [H.15 monthly series preview](https://www.federalreserve.gov/datadownload/Preview.aspx?pi=400&preview=H15%2FH15%2FRIFSGFSM03_N.M&rel=H15).
- FRED, [`TB3MS` series metadata](https://fred.stlouisfed.org/series/TB3MS).
- BLS, [Public Data API](https://www.bls.gov/developers/) and
  [API terms of service](https://www.bls.gov/developers/termsOfService.htm).
- BLS, [usual weekly earnings technical note](https://www.bls.gov/news.release/wkyeng.tn.htm)
  and [earnings FAQ](https://www.bls.gov/cps/earnings-faqs.htm).
