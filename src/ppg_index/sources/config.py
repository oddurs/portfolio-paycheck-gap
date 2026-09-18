"""Canonical source contracts for the PPG index."""

from __future__ import annotations

JKP_URL = (
    "https://jkpfactors-data.s3.amazonaws.com/public/%5Busa%5D_%5Bmkt%5D_%5Bmonthly%5D_%5Bvw%5D.zip"
)
JKP_IDENTIFIER = "usa / mkt / monthly / vw"
JKP_RAW_NAME = "jkp-usa-mkt-monthly-vw.zip"

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS"
FRED_IDENTIFIER = "H15/H15/RIFSGFSM03_N.M (FRED TB3MS)"
FRED_RAW_NAME = "fred-tb3ms.csv"

BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/LES1252881500"
BLS_IDENTIFIER = "LES1252881500"
BLS_FIRST_YEAR = 1979
# The public, unregistered API permits ten years per request.
BLS_MAX_YEARS_PER_REQUEST = 10

PARSER_VERSION = "1"
USER_AGENT = "ppg-index/0.2 (+https://github.com/oddurs/portfolio-paycheck-gap)"
