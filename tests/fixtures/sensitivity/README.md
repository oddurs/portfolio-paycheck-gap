# Methodology sensitivity fixtures

These compact inputs support Cairn item 0008 and are not production data.

- `jkp-market-weightings.csv` selects January–September 1980 from JKP's
  current United States market files for value, equal, and capped-value
  weighting.
- `bls-paycheck-definitions.csv` selects the matching BLS seasonally adjusted
  nominal (`LES1252881500`), unadjusted nominal (`LEU0252881500`), and
  seasonally adjusted real (`LES1252881600`) series.
- `jkp-revision-1980.csv` compares the legacy JKP S3 object with the 2026
  Python-pipeline vintage. The complete ZIP hashes are
  `0cdeaee6c4980085fae967d70246a79ed0c7274161ba1a3a1d5eeec8bba78f87`
  (legacy) and
  `8c69cc848ebb447f8c47346a4b3eabed65fac03f0b895b04319f3828e3b6e79f`
  (current).
- `bls-revision-2025q1.csv` compares the BLS 2025 Q1 archived release with the
  current 2026 Q2 table/API vintage.
- `expected-results.csv` is the reviewed six-decimal result table reproduced by
  `make methodology-check`.

JKP-derived rows are modified extracts under CC BY-NC 4.0. BLS terms and the
required disclaimer are in `DATA_LICENSE.md`.
