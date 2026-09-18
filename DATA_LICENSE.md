# Data licensing and attribution

Repository code and source-derived data are separate works. A code license
does not grant additional rights in source data.

The JKP Global Factor Data snapshot under `data/`, its samples under
`tests/fixtures/sources/`, and PPG artifacts derived from them are licensed by
Jensen, Kelly, and Pedersen under the
[Creative Commons Attribution-NonCommercial 4.0 International
license](https://creativecommons.org/licenses/by-nc/4.0/). They have been
modified by selecting rows, normalizing serialization, reconstructing a
total-return proxy, compounding, rebasing, and charting. These materials are
published for noncommercial use with the same attribution and license
restriction unless stated otherwise.

The Treasury-bill observations originate with the Board of Governors of the
Federal Reserve System and are retrieved through FRED series `TB3MS`. FRED
labels the series “Public Domain: Citation Requested.”

The earnings observations originate with the US Bureau of Labor Statistics,
series `LES1252881500`. They are selected and reserialized from the BLS Public
Data API. BLS requires the retrieval date and this notice:

> BLS.gov cannot vouch for the data or analyses derived from these data after
> the data have been retrieved from BLS.gov.

See `methodology/decisions/0006-data-sources.md` for exact endpoints,
transformations, and source terms. This file is a project data-use notice, not
legal advice.
