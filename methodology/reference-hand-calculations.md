# Reference hand calculations

Status: accepted for methodology v0.1

Cairn item: 0007

Checked: 2026-09-13

These calculations independently anchor the reference notebook. Source values
are copied from the pinned fixtures; arithmetic was evaluated at 50-decimal
precision and rounded only at the six-decimal output boundary using
round-to-nearest, ties-to-even.

For each month, the Treasury proxy and reconstructed market return are:

```text
p = 1 - (yield_percent / 100) × 91 / 360
rf = p ^ (-calendar_days_in_month / 91) - 1
r  = excess_return + rf
```

Starting with market wealth `1` immediately before January 1980, compounding
the nine pinned monthly inputs gives:

| Month | Treasury proxy | Total-return proxy | Ending wealth |
| --- | ---: | ---: | ---: |
| 1980-01 | 0.010548546457 | 0.067763383577 | 1.067763383577 |
| 1980-02 | 0.010587215285 | 0.001458330499 | 1.069320535485 |
| 1980-03 | 0.013436441836 | -0.119218473157 | 0.941837773929 |
| 1980-04 | 0.011250520253 | 0.050914934843 | 0.989791382821 |
| 1980-05 | 0.007497598566 | 0.059881298394 | 1.049061375964 |
| 1980-06 | 0.005962654846 | 0.037913578481 | 1.088835046772 |
| 1980-07 | 0.007036877137 | 0.071158375030 | 1.166314779376 |
| 1980-08 | 0.007985804038 | 0.025490353697 | 1.196044555625 |
| 1980-09 | 0.008709087851 | 0.029571097078 | 1.231412905288 |

With 1980 Q1 as base, the independent quarterly calculations are:

```text
1980-Q1
MARKET   = 100 × 0.941837773929 / 0.941837773929 = 100.000000
PAYCHECK = 100 × 254 / 254                       = 100.000000
PPG      = 100 × 100 / 100                       = 100.000000

1980-Q2
MARKET   = 100 × 1.088835046772 / 0.941837773929 = 115.607494
PAYCHECK = 100 × 257 / 254                       = 101.181102
PPG      = 100 × 115.607494... / 101.181102...   = 114.257990

1980-Q3
MARKET   = 100 × 1.231412905288 / 0.941837773929 = 130.745755
PAYCHECK = 100 × 266 / 254                       = 104.724409
PPG      = 100 × 130.745755... / 104.724409...   = 124.847450
```

The six-decimal results are pinned in
`tests/fixtures/reference-calculation.csv`. The notebook must reproduce that
file byte for byte.
