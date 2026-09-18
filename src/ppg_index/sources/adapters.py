"""Strict parsers for the three canonical PPG sources."""

from __future__ import annotations

import calendar
import csv
import io
import json
import math
import zipfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date

from .config import BLS_IDENTIFIER


class SourceValidationError(ValueError):
    """A response does not satisfy its canonical source contract."""


@dataclass(frozen=True, slots=True)
class NormalizedSource:
    """A validated, normalized source payload."""

    data: bytes
    rows: int
    first_period: str
    last_period: str
    release_period: str


def _csv_bytes(fieldnames: Sequence[str], rows: Iterable[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def _finite_number(value: str, label: str) -> float:
    try:
        number = float(value)
    except ValueError as error:
        raise SourceValidationError(f"{label} is not numeric: {value!r}") from error
    if not math.isfinite(number):
        raise SourceValidationError(f"{label} must be finite")
    return number


def _month_sequence(first: str, last: str) -> list[str]:
    year, month = map(int, first.split("-"))
    end_year, end_month = map(int, last.split("-"))
    result: list[str] = []
    while (year, month) <= (end_year, end_month):
        result.append(f"{year:04d}-{month:02d}")
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1
    return result


def normalize_market(raw: bytes) -> NormalizedSource:
    """Validate the JKP ZIP and return canonical monthly excess returns."""

    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile as error:
        raise SourceValidationError("JKP response is not a ZIP archive") from error
    with archive:
        members = [item for item in archive.infolist() if not item.is_dir()]
        if len(members) != 1 or not members[0].filename.endswith(".csv"):
            raise SourceValidationError("JKP archive must contain exactly one CSV")
        member = members[0]
        if member.file_size > 5_000_000:
            raise SourceValidationError("JKP CSV exceeds the 5 MB safety limit")
        if member.filename.startswith("/") or ".." in member.filename.split("/"):
            raise SourceValidationError("JKP archive contains an unsafe member name")
        csv_raw = archive.read(member)

    reader = csv.DictReader(io.StringIO(csv_raw.decode("utf-8-sig")))
    required = {"location", "name", "freq", "weighting", "date", "ret"}
    if reader.fieldnames is None or not required.issubset(reader.fieldnames):
        raise SourceValidationError("JKP CSV is missing required fields")

    observations: dict[str, str] = {}
    for line, row in enumerate(reader, start=2):
        identity = (row["location"], row["name"], row["freq"], row["weighting"])
        if identity != ("usa", "mkt", "monthly", "vw"):
            raise SourceValidationError(f"unexpected JKP identity on line {line}: {identity}")
        try:
            observed = date.fromisoformat(row["date"])
        except ValueError as error:
            raise SourceValidationError(f"invalid JKP date on line {line}") from error
        final_day = calendar.monthrange(observed.year, observed.month)[1]
        if observed.day != final_day:
            raise SourceValidationError(f"JKP date is not month end: {observed}")
        period = observed.strftime("%Y-%m")
        if period in observations:
            raise SourceValidationError(f"duplicate JKP month: {period}")
        value = _finite_number(row["ret"], f"JKP return for {period}")
        if value <= -1:
            raise SourceValidationError(f"JKP return must exceed -1 for {period}")
        observations[period] = row["ret"]

    if not observations:
        raise SourceValidationError("JKP response contains no observations")
    periods = sorted(observations)
    if periods[0] != "1926-01" or periods[-1] < "2025-12":
        raise SourceValidationError(f"unexpected JKP coverage: {periods[0]} through {periods[-1]}")
    if periods != _month_sequence(periods[0], periods[-1]):
        raise SourceValidationError("JKP monthly coverage contains a gap")
    rows = [{"month": period, "excess_return": observations[period]} for period in periods]
    return NormalizedSource(
        _csv_bytes(["month", "excess_return"], rows),
        len(rows),
        periods[0],
        periods[-1],
        periods[-1],
    )


def normalize_treasury(raw: bytes) -> NormalizedSource:
    """Validate FRED TB3MS CSV and return canonical monthly discount rates."""

    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames is None or not {"observation_date", "TB3MS"}.issubset(reader.fieldnames):
        raise SourceValidationError("FRED CSV is missing observation_date or TB3MS")

    observations: dict[str, str] = {}
    for line, row in enumerate(reader, start=2):
        try:
            observed = date.fromisoformat(row["observation_date"])
        except ValueError as error:
            raise SourceValidationError(f"invalid FRED date on line {line}") from error
        if observed.day != 1:
            raise SourceValidationError(f"FRED date is not a month label: {observed}")
        period = observed.strftime("%Y-%m")
        if period in observations:
            raise SourceValidationError(f"duplicate FRED month: {period}")
        value = _finite_number(row["TB3MS"], f"TB3MS for {period}")
        if value < 0 or value >= 100 * 360 / 91:
            raise SourceValidationError(f"unsupported TB3MS quote for {period}: {value}")
        observations[period] = row["TB3MS"]

    if not observations:
        raise SourceValidationError("FRED response contains no observations")
    periods = sorted(observations)
    if periods[0] != "1934-01" or periods[-1] < "2025-09":
        raise SourceValidationError(
            f"unexpected TB3MS coverage: {periods[0]} through {periods[-1]}"
        )
    if periods != _month_sequence(periods[0], periods[-1]):
        raise SourceValidationError("TB3MS monthly coverage contains a gap")
    rows = [{"month": period, "discount_rate_percent": observations[period]} for period in periods]
    return NormalizedSource(
        _csv_bytes(["month", "discount_rate_percent"], rows),
        len(rows),
        periods[0],
        periods[-1],
        periods[-1],
    )


def _quarter_sequence(first: str, last: str) -> list[str]:
    year, quarter = int(first[:4]), int(first[-1])
    end_year, end_quarter = int(last[:4]), int(last[-1])
    result: list[str] = []
    while (year, quarter) <= (end_year, end_quarter):
        result.append(f"{year:04d}-Q{quarter}")
        if quarter == 4:
            year, quarter = year + 1, 1
        else:
            quarter += 1
    return result


def normalize_paycheck(raw_responses: Sequence[bytes]) -> NormalizedSource:
    """Validate BLS responses and return canonical quarterly paycheck rows."""

    if not raw_responses:
        raise SourceValidationError("no BLS responses supplied")
    observations: dict[str, tuple[str, str]] = {}
    for response_number, raw in enumerate(raw_responses, start=1):
        try:
            payload = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise SourceValidationError(f"BLS response {response_number} is not JSON") from error
        if payload.get("status") != "REQUEST_SUCCEEDED":
            raise SourceValidationError(
                f"BLS response {response_number} failed: {payload.get('message')}"
            )
        series = payload.get("Results", {}).get("series", [])
        if len(series) != 1 or series[0].get("seriesID") != BLS_IDENTIFIER:
            raise SourceValidationError("BLS returned an unexpected series identifier")
        data = series[0].get("data")
        if not isinstance(data, list) or not data:
            raise SourceValidationError("BLS response contains no observations")
        for item in data:
            period = item.get("period", "")
            year = item.get("year", "")
            if period not in {"Q01", "Q02", "Q03", "Q04"} or not (
                isinstance(year, str) and len(year) == 4 and year.isdigit()
            ):
                raise SourceValidationError(f"unexpected BLS period: {year} {period}")
            quarter = f"{year}-Q{int(period[-2:])}"
            raw_value = item.get("value")
            if not isinstance(raw_value, str):
                raise SourceValidationError(f"BLS value is not text for {quarter}")
            notes = item.get("footnotes", [])
            if not isinstance(notes, list):
                raise SourceValidationError(f"BLS footnotes are malformed for {quarter}")
            reason = "; ".join(
                note.get("text", "")
                for note in notes
                if isinstance(note, dict) and note.get("text")
            )
            if raw_value == "-":
                value = ""
                if not reason:
                    raise SourceValidationError(
                        f"BLS missing marker has no explanation for {quarter}"
                    )
            else:
                number = _finite_number(raw_value, f"BLS paycheck for {quarter}")
                if number <= 0:
                    raise SourceValidationError(f"BLS paycheck must be positive for {quarter}")
                value = raw_value
            candidate = (value, reason)
            if quarter in observations and observations[quarter] != candidate:
                raise SourceValidationError(f"conflicting duplicate BLS quarter: {quarter}")
            observations[quarter] = candidate

    periods = sorted(observations)
    if periods[0] != "1979-Q1" or periods[-1] < "2025-Q4":
        raise SourceValidationError(f"unexpected BLS coverage: {periods[0]} through {periods[-1]}")
    if periods != _quarter_sequence(periods[0], periods[-1]):
        raise SourceValidationError("BLS quarterly coverage contains a gap")
    rows = [
        {
            "quarter": period,
            "value": observations[period][0],
            "missing_reason": observations[period][1],
        }
        for period in periods
    ]
    return NormalizedSource(
        _csv_bytes(["quarter", "value", "missing_reason"], rows),
        len(rows),
        periods[0],
        periods[-1],
        periods[-1],
    )
