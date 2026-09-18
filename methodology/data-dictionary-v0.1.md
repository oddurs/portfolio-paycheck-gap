# PPG v0.1 data dictionary

Status: normative

Methodology: [v0.1](v0.1.md)

Effective: 2026-09-13

## Conventions

- `string` values are UTF-8; identifiers are case-sensitive.
- `date` values use ISO 8601 `YYYY-MM-DD`.
- `month` uses `YYYY-MM`; `quarter` uses `YYYY-QN`.
- `float64` means IEEE 754 binary64 or higher precision in calculation.
- Decimal returns use `0.01` for one percent. Percent quotes use `1.0` for one
  percent. Index levels use 1980 Q1 = 100.
- “Required” nullability means a missing value fails a canonical historical
  row. Explicit source placeholders may be nullable during normalization but
  cannot appear in a published row.
- Source numeric precision is preserved. Public index values have fixed
  six-decimal serialization with round-to-nearest, ties-to-even.

## Raw JKP market input

Source selection: `usa / mkt / monthly / vw`. One row per calendar month.

| Name | Type | Units / allowed values | Frequency | Nullable | Precision / use |
| --- | --- | --- | --- | --- | --- |
| `location` | string | constant `usa` | monthly | no | Identity validation |
| `name` | string | constant `mkt` | monthly | no | Identity validation |
| `freq` | string | constant `monthly` | monthly | no | Identity validation |
| `weighting` | string | constant `vw` | monthly | no | Identity validation |
| `direction` | string | source marker `na` | monthly | no | Retained provenance; not calculated |
| `n_stocks` | integer | count of eligible securities, > 0 | monthly | no | Exact integer; diagnostic |
| `n_stocks_min` | string/null | source marker `na` | monthly | yes | Retained provenance; not calculated |
| `date` | date | calendar month-end label | monthly | no | Unique, ascending after normalization |
| `ret` | float64 | decimal US-dollar excess return, > -1 | monthly | no | Parse source text without rounding |

## Raw Treasury input

Source series: H.15 `RIFSGFSM03_N.M`, delivered as FRED `TB3MS`. One row per
calendar month.

| Name | Type | Units / allowed values | Frequency | Nullable | Precision / use |
| --- | --- | --- | --- | --- | --- |
| `observation_date` | date | first day label of average month | monthly | no | Map to `YYYY-MM`; unique |
| `TB3MS` | float64 | percent per year, discount basis | monthly | no | Source precision; accepted domain yields `0 < bill_price <= 1` |

## Raw BLS paycheck input

Source series: `LES1252881500`. One row per calendar quarter.

| Name | Type | Units / allowed values | Frequency | Nullable | Precision / use |
| --- | --- | --- | --- | --- | --- |
| `series_id` | string | constant `LES1252881500` | quarterly | no | Identity validation |
| `year` | integer | four-digit calendar year | quarterly | no | Exact integer |
| `period` | string | `Q01`, `Q02`, `Q03`, or `Q04` | quarterly | no | Annual periods are rejected |
| `value` | float64/null | current US dollars per week, > 0 | quarterly | yes during normalization | `-` transforms to null; numeric source precision retained |
| `footnote` | string/null | publisher explanation | quarterly | yes | Provenance only; never parsed as data |

## Monthly calculation fields

These fields remain available in calculation traces; they are not rounded or
required in the headline CSV.

| Name | Type | Units / allowed values | Frequency | Nullable | Precision / definition |
| --- | --- | --- | --- | --- | --- |
| `month` | month | `YYYY-MM` | monthly | no | Join key for market and Treasury |
| `excess_return` | float64 | decimal return, > -1 | monthly | no | JKP `ret` |
| `annual_discount_yield_percent` | float64 | percent per year | monthly | no | H.15 `TB3MS` |
| `calendar_days` | integer | 28–31 days | monthly | no | Gregorian calendar count |
| `bill_term_days` | integer | constant 91 days | monthly | no | Exact methodology constant |
| `bill_price` | float64 | price per 1 redemption value, `(0, 1]` | monthly | no | `1 - (yield / 100) × 91 / 360` |
| `treasury_return` | float64 | decimal monthly proxy return | monthly | no | `bill_price ^ (-calendar_days / 91) - 1` |
| `market_return` | float64 | decimal monthly total-return proxy, > -1 | monthly | no | `excess_return + treasury_return` |
| `market_wealth` | float64 | arbitrary wealth units, > 0 | monthly | no | Prior wealth × `(1 + market_return)` |

## Quarterly calculation fields

| Name | Type | Units / allowed values | Frequency | Nullable | Precision / definition |
| --- | --- | --- | --- | --- | --- |
| `quarter` | quarter | `YYYY-QN` | quarterly | no | Unique chronological key |
| `quarter_end` | date | calendar quarter end | quarterly | no | March, June, September, or December end |
| `market_value` | float64 | arbitrary wealth units, > 0 | quarterly | no | Ending `market_wealth` for quarter |
| `paycheck_value` | float64 | current US dollars per week, > 0 | quarterly | no | Numeric BLS `value` |
| `market_component` | float64 | index, 1980 Q1 = 100 | quarterly | no | Unrounded until publication; then 6 decimals |
| `paycheck_component` | float64 | index, 1980 Q1 = 100 | quarterly | no | Unrounded until publication; then 6 decimals |
| `ppg` | float64 | index, 1980 Q1 = 100 | quarterly | no | Unrounded until publication; then 6 decimals |
| `ppg_change_qoq_percent` | float64 | percent change | quarterly | yes for first observation | `(PPG_t / PPG_(t-1) - 1) × 100`, calculated from unrounded values |
| `ppg_change_yoy_percent` | float64 | percent change | quarterly | yes for first four observations | `(PPG_t / PPG_(t-4) - 1) × 100`, calculated from unrounded values |

## Public observation row

CSV rows and JSON observation objects expose the same fields. No public row
contains nulls; an incomplete quarter is omitted.

| Name | Type | Units / allowed values | Frequency | Nullable | Precision / definition |
| --- | --- | --- | --- | --- | --- |
| `quarter` | quarter | `YYYY-QN` | quarterly | no | Canonical observation key |
| `quarter_end` | date | ISO calendar quarter end | quarterly | no | Machine date; earnings cover the quarter |
| `paycheck_value` | decimal | current US dollars per week | quarterly | no | Source precision, no invented cents |
| `market_component` | decimal | unitless index | quarterly | no | Exactly 6 decimal places |
| `paycheck_component` | decimal | unitless index | quarterly | no | Exactly 6 decimal places |
| `ppg` | decimal | unitless index | quarterly | no | Exactly 6 decimal places |

## Public metadata record

The companion JSON metadata applies to the artifact as a whole.

| Name | Type | Units / allowed values | Frequency | Nullable | Precision / definition |
| --- | --- | --- | --- | --- | --- |
| `methodology_version` | string | constant `0.1` | per release | no | Governs calculation and schema |
| `generated_at` | string | ISO 8601 UTC timestamp | per release | no | Second precision, suffix `Z` |
| `latest_quarter` | quarter | newest complete observation | per release | no | Must equal final row key |
| `stale` | boolean | `true` or `false` | per release | no | True when a newer calendar quarter lacks complete inputs |
| `market_retrieved_at` | string | ISO 8601 UTC timestamp | per source vintage | no | Second precision, suffix `Z` |
| `market_sha256` | string | 64 lowercase hexadecimal characters | per source vintage | no | Hash of raw JKP ZIP bytes |
| `treasury_retrieved_at` | string | ISO 8601 UTC timestamp | per source vintage | no | Second precision, suffix `Z` |
| `treasury_sha256` | string | 64 lowercase hexadecimal characters | per source vintage | no | Hash of raw delivered bytes |
| `paycheck_retrieved_at` | string | ISO 8601 UTC timestamp | per source vintage | no | Second precision, suffix `Z` |
| `paycheck_sha256` | string | 64 lowercase hexadecimal characters | per source vintage | no | Hash of canonical raw-response bundle |
| `source_notice` | string | attribution and BLS disclaimer | per release | no | Exact release notice, UTF-8 |

Artifact encoding and filenames may be elaborated by a later publication
version, but removing, renaming, changing the meaning, or reducing the
precision of a v0.1 field is a schema/methodology change.
