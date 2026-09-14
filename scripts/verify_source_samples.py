#!/usr/bin/env python3
"""Reproduce and verify the small source samples accepted for PPG v0.1."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "sources"
USER_AGENT = "ppg-index-source-verifier/0.1 (+https://github.com/)"

JKP_URL = (
    "https://jkpfactors-data.s3.amazonaws.com/public/"
    "%5Busa%5D_%5Bmkt%5D_%5Bmonthly%5D_%5Bvw%5D.zip"
)
JKP_ARCHIVE_SHA256 = (
    "8c69cc848ebb447f8c47346a4b3eabed65fac03f0b895b04319f3828e3b6e79f"
)
JKP_DATES = {
    "1979-12-31",
    "1980-01-31",
    "1980-02-29",
    "1980-03-31",
    "1980-04-30",
    "1980-05-31",
    "1980-06-30",
    "1980-07-31",
    "1980-08-31",
    "1980-09-30",
    "2025-07-31",
    "2025-08-31",
    "2025-09-30",
}

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS"
FRED_DATES = {
    "1979-12-01",
    "1980-01-01",
    "1980-02-01",
    "1980-03-01",
    "1980-04-01",
    "1980-05-01",
    "1980-06-01",
    "1980-07-01",
    "1980-08-01",
    "1980-09-01",
    "2025-07-01",
    "2025-08-01",
    "2025-09-01",
}

BLS_SERIES = "LES1252881500"
BLS_PERIODS = {
    ("1979", "Q04"),
    ("1980", "Q01"),
    ("1980", "Q02"),
    ("1980", "Q03"),
    ("2025", "Q03"),
    ("2025", "Q04"),
}


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read()


def serialize(fieldnames: list[str], rows: list[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def select_csv(raw: bytes, key: str, wanted: set[str]) -> bytes:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames is None:
        raise ValueError("source CSV has no header")
    rows = [row for row in reader if row[key] in wanted]
    rows.sort(key=lambda row: row[key])
    found = {row[key] for row in rows}
    if found != wanted:
        raise ValueError(f"missing {key} values: {sorted(wanted - found)}")
    return serialize(reader.fieldnames, rows)


def reproduce_jkp() -> bytes:
    archive = fetch(JKP_URL)
    actual_hash = hashlib.sha256(archive).hexdigest()
    if actual_hash != JKP_ARCHIVE_SHA256:
        raise ValueError(
            "JKP source vintage changed: "
            f"expected {JKP_ARCHIVE_SHA256}, got {actual_hash}"
        )
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        members = [name for name in bundle.namelist() if name.endswith(".csv")]
        if len(members) != 1:
            raise ValueError(f"expected one CSV in JKP ZIP, found {members}")
        info = bundle.getinfo(members[0])
        if info.file_size > 5_000_000:
            raise ValueError("JKP CSV exceeds the verifier's 5 MB safety limit")
        raw = bundle.read(info)
    return select_csv(raw, "date", JKP_DATES)


def reproduce_fred() -> bytes:
    return select_csv(fetch(FRED_URL), "observation_date", FRED_DATES)


def reproduce_bls() -> bytes:
    observations: dict[tuple[str, str], dict[str, str]] = {}
    for start, end in ((1979, 1980), (2025, 2025)):
        url = (
            "https://api.bls.gov/publicAPI/v2/timeseries/data/"
            f"{BLS_SERIES}?startyear={start}&endyear={end}"
        )
        payload = json.loads(fetch(url))
        if payload.get("status") != "REQUEST_SUCCEEDED":
            raise ValueError(f"BLS request failed: {payload.get('message')}")
        series = payload["Results"]["series"]
        if len(series) != 1 or series[0]["seriesID"] != BLS_SERIES:
            raise ValueError("BLS returned an unexpected series")
        for item in series[0]["data"]:
            key = (item["year"], item["period"])
            if key not in BLS_PERIODS:
                continue
            notes = [note.get("text", "") for note in item.get("footnotes", [])]
            observations[key] = {
                "series_id": BLS_SERIES,
                "year": item["year"],
                "period": item["period"],
                "value": item["value"],
                "footnote": "; ".join(note for note in notes if note),
            }
    if set(observations) != BLS_PERIODS:
        raise ValueError(f"BLS periods differ: {sorted(observations)}")
    rows = [observations[key] for key in sorted(observations)]
    return serialize(["series_id", "year", "period", "value", "footnote"], rows)


def expected_hashes() -> dict[str, str]:
    result: dict[str, str] = {}
    path = FIXTURES / "SHA256SUMS"
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, filename = line.split("  ", 1)
        result[filename] = digest
    return result


def verify(name: str, reproduced: bytes, hashes: dict[str, str]) -> None:
    fixture = (FIXTURES / name).read_bytes()
    digest = hashlib.sha256(fixture).hexdigest()
    if hashes.get(name) != digest:
        raise ValueError(f"local checksum mismatch for {name}")
    if reproduced != fixture:
        raise ValueError(f"live source does not reproduce {name}")
    print(f"ok  {digest}  {name}")


def main() -> int:
    try:
        hashes = expected_hashes()
        verify("jkp-usa-mkt-monthly-vw.csv", reproduce_jkp(), hashes)
        verify("fred-tb3ms.csv", reproduce_fred(), hashes)
        verify("bls-les1252881500.csv", reproduce_bls(), hashes)
    except Exception as error:  # A concise CLI boundary; details retain the cause.
        print(f"source verification failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
