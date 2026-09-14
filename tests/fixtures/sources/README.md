# Pinned source samples

These are row-selected, canonically serialized samples of the three PPG v0.1
inputs. They cover the first three reference-calculation quarters beginning at
the 1980 Q1 base and the latest mutually complete quarter in the accepted
source vintage, 2025 Q3. The BLS sample also preserves the
publisher's missing-value marker and explanation for 2025 Q4.

Accepted on 2026-09-13:

- JKP United States market, monthly, value weighted; mutable source ZIP SHA-256
  `8c69cc848ebb447f8c47346a4b3eabed65fac03f0b895b04319f3828e3b6e79f`;
- Federal Reserve H.15 `RIFSGFSM03_N.M`, delivered by FRED `TB3MS`; and
- BLS `LES1252881500`, delivered by the BLS Public Data API v2.

Run `make source-check` to verify the local checksums and reproduce the samples
from the live endpoints. A mismatch requires source-review; do not refresh a
fixture blindly.

The JKP sample is a modified extract under CC BY-NC 4.0. Federal Reserve data
is public domain with citation requested. BLS secondary use and attribution
requirements are recorded in `DATA_LICENSE.md`.
