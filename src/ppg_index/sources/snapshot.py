"""Acquire, store, and verify immutable source snapshots."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import tempfile
import time
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

from .adapters import NormalizedSource, normalize_market, normalize_paycheck, normalize_treasury
from .config import (
    BLS_FIRST_YEAR,
    BLS_IDENTIFIER,
    BLS_MAX_YEARS_PER_REQUEST,
    BLS_URL,
    FRED_IDENTIFIER,
    FRED_RAW_NAME,
    FRED_URL,
    JKP_IDENTIFIER,
    JKP_RAW_NAME,
    JKP_URL,
    PARSER_VERSION,
    USER_AGENT,
)

Fetcher = Callable[[str], bytes]
MANIFEST_NAME = "manifest.json"


class SnapshotError(ValueError):
    """A snapshot cannot be safely created or replayed."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_url(url: str) -> bytes:
    last_error: OSError | None = None
    for attempt in range(3):
        request = Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urlopen(request, timeout=60) as response:
                return response.read()
        except OSError as error:
            last_error = error
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def _bls_ranges(end_year: int) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start = BLS_FIRST_YEAR
    while start <= end_year:
        end = min(start + BLS_MAX_YEARS_PER_REQUEST - 1, end_year)
        ranges.append((start, end))
        start = end + 1
    return ranges


def _source_record(
    *,
    name: str,
    publisher: str,
    identifier: str,
    url: str,
    units: str,
    raw_files: Sequence[tuple[str, bytes]],
    normalized_name: str,
    normalized: NormalizedSource,
) -> dict[str, object]:
    return {
        "name": name,
        "publisher": publisher,
        "identifier": identifier,
        "url": url,
        "units": units,
        "release_period": normalized.release_period,
        "coverage": {
            "first": normalized.first_period,
            "last": normalized.last_period,
            "rows": normalized.rows,
        },
        "raw": [
            {"path": f"raw/{filename}", "sha256": sha256(data), "bytes": len(data)}
            for filename, data in raw_files
        ],
        "normalized": {
            "path": f"normalized/{normalized_name}",
            "sha256": sha256(normalized.data),
            "bytes": len(normalized.data),
        },
    }


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def _snapshot_id(records: Sequence[dict[str, object]]) -> str:
    identity = []
    for record in records:
        raw = record["raw"]
        assert isinstance(raw, list)
        identity.append(
            {
                "name": record["name"],
                "raw": [item["sha256"] for item in raw],
            }
        )
    return sha256(_canonical_json(identity))[:16]


def _load_manifest(snapshot_dir: Path) -> dict[str, object]:
    try:
        manifest = json.loads((snapshot_dir / MANIFEST_NAME).read_bytes())
    except (OSError, json.JSONDecodeError) as error:
        raise SnapshotError(f"cannot read snapshot manifest at {snapshot_dir}") from error
    if not isinstance(manifest, dict):
        raise SnapshotError("snapshot manifest must be a JSON object")
    return manifest


def verify_snapshot(snapshot_dir: Path) -> dict[str, object]:
    """Verify every declared file checksum and core manifest identity."""

    manifest = _load_manifest(snapshot_dir)
    if manifest.get("schema_version") != 1 or manifest.get("parser_version") != PARSER_VERSION:
        raise SnapshotError("unsupported snapshot manifest or parser version")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or len(sources) != 3:
        raise SnapshotError("snapshot must declare exactly three sources")
    for source in sources:
        if not isinstance(source, dict):
            raise SnapshotError("source manifest entry must be an object")
        files = [*source.get("raw", []), source.get("normalized")]
        for item in files:
            if not isinstance(item, dict):
                raise SnapshotError("snapshot file entry must be an object")
            relative = item.get("path")
            if (
                not isinstance(relative, str)
                or Path(relative).is_absolute()
                or ".." in Path(relative).parts
            ):
                raise SnapshotError("unsafe snapshot path")
            path = snapshot_dir / relative
            try:
                data = path.read_bytes()
            except OSError as error:
                raise SnapshotError(f"missing snapshot file: {relative}") from error
            if sha256(data) != item.get("sha256") or len(data) != item.get("bytes"):
                raise SnapshotError(f"snapshot checksum mismatch: {relative}")
    if manifest.get("snapshot_id") != _snapshot_id(sources):
        raise SnapshotError("snapshot identifier does not match raw checksums")
    return manifest


def _normalized_rows(snapshot_dir: Path, source: dict[str, object]) -> dict[str, dict[str, str]]:
    normalized = source["normalized"]
    assert isinstance(normalized, dict)
    path = snapshot_dir / str(normalized["path"])
    reader = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    key = {"market": "month", "treasury": "month", "paycheck": "quarter"}[str(source["name"])]
    return {row[key]: row for row in reader}


def _find_revisions(
    previous_dir: Path,
    previous: dict[str, object],
    current_records: Sequence[dict[str, object]],
    current_normalized: dict[str, NormalizedSource],
) -> list[str]:
    revisions: list[str] = []
    sources = previous["sources"]
    assert isinstance(sources, list)
    previous_sources = {source["name"]: source for source in sources}
    for record in current_records:
        name = str(record["name"])
        old_source = previous_sources.get(name)
        if old_source is None:
            revisions.append(f"{name}: source was not present in prior snapshot")
            continue
        old_rows = _normalized_rows(previous_dir, old_source)
        new_reader = csv.DictReader(current_normalized[name].data.decode("utf-8").splitlines())
        key = {"market": "month", "treasury": "month", "paycheck": "quarter"}[name]
        new_rows = {row[key]: row for row in new_reader}
        changed = sorted(
            period
            for period in old_rows.keys() & new_rows.keys()
            if old_rows[period] != new_rows[period]
        )
        removed = sorted(old_rows.keys() - new_rows.keys())
        if changed:
            revisions.append(
                f"{name}: {len(changed)} overlapping period(s) changed ({', '.join(changed[:5])})"
            )
        if removed:
            revisions.append(f"{name}: {len(removed)} prior period(s) disappeared")
    return revisions


def resolve_current(cache_dir: Path) -> Path | None:
    """Resolve the current snapshot pointer beneath a cache root."""

    pointer = cache_dir / "current.json"
    if not pointer.exists():
        return None
    try:
        data = json.loads(pointer.read_bytes())
        snapshot_id = data["snapshot_id"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise SnapshotError("current snapshot pointer is malformed") from error
    if not isinstance(snapshot_id, str) or not snapshot_id:
        raise SnapshotError("current snapshot pointer has an invalid identifier")
    return cache_dir / "snapshots" / snapshot_id


def acquire_snapshot(
    cache_dir: Path,
    *,
    end_year: int,
    retrieved_at: str | None = None,
    accept_revision: bool = False,
    fetcher: Fetcher = fetch_url,
) -> Path:
    """Fetch, validate, and atomically store an immutable source snapshot."""

    if end_year < 2025:
        raise SnapshotError("end year must include the accepted 2025 source vintage")
    timestamp = retrieved_at or datetime.now(UTC).replace(microsecond=0).isoformat()
    try:
        parsed_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as error:
        raise SnapshotError("retrieved-at must be an ISO 8601 timestamp") from error
    if parsed_timestamp.tzinfo is None:
        raise SnapshotError("retrieved-at must include a timezone")

    market_raw = fetcher(JKP_URL)
    treasury_raw = fetcher(FRED_URL)
    bls_files: list[tuple[str, bytes]] = []
    for start, end in _bls_ranges(end_year):
        url = f"{BLS_URL}?startyear={start}&endyear={end}"
        bls_files.append((f"bls-{BLS_IDENTIFIER}-{start}-{end}.json", fetcher(url)))

    normalized = {
        "market": normalize_market(market_raw),
        "treasury": normalize_treasury(treasury_raw),
        "paycheck": normalize_paycheck([data for _, data in bls_files]),
    }
    records = [
        _source_record(
            name="market",
            publisher="Jensen, Kelly, and Pedersen Global Factor Data",
            identifier=JKP_IDENTIFIER,
            url=JKP_URL,
            units="decimal monthly excess return",
            raw_files=[(JKP_RAW_NAME, market_raw)],
            normalized_name="market.csv",
            normalized=normalized["market"],
        ),
        _source_record(
            name="treasury",
            publisher="Board of Governors of the Federal Reserve System via FRED",
            identifier=FRED_IDENTIFIER,
            url=FRED_URL,
            units="percent per year, discount basis",
            raw_files=[(FRED_RAW_NAME, treasury_raw)],
            normalized_name="treasury.csv",
            normalized=normalized["treasury"],
        ),
        _source_record(
            name="paycheck",
            publisher="US Bureau of Labor Statistics",
            identifier=BLS_IDENTIFIER,
            url=BLS_URL,
            units="current US dollars per week, seasonally adjusted",
            raw_files=bls_files,
            normalized_name="paycheck.csv",
            normalized=normalized["paycheck"],
        ),
    ]
    snapshot_id = _snapshot_id(records)
    snapshots_dir = cache_dir / "snapshots"
    destination = snapshots_dir / snapshot_id
    if destination.exists():
        verify_snapshot(destination)
        return destination

    previous_dir = resolve_current(cache_dir)
    if previous_dir is not None:
        previous = verify_snapshot(previous_dir)
        revisions = _find_revisions(previous_dir, previous, records, normalized)
        if revisions and not accept_revision:
            raise SnapshotError(
                "unexpected source revision; inspect and rerun with --accept-revision: "
                + "; ".join(revisions)
            )

    manifest = {
        "schema_version": 1,
        "snapshot_id": snapshot_id,
        "parser_version": PARSER_VERSION,
        "retrieved_at": parsed_timestamp.astimezone(UTC).replace(microsecond=0).isoformat(),
        "sources": records,
    }
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{snapshot_id}-", dir=snapshots_dir))
    try:
        (temporary / "raw").mkdir()
        (temporary / "normalized").mkdir()
        raw_files = [(JKP_RAW_NAME, market_raw), (FRED_RAW_NAME, treasury_raw), *bls_files]
        for name, data in raw_files:
            (temporary / "raw" / name).write_bytes(data)
        for name, source in normalized.items():
            (temporary / "normalized" / f"{name}.csv").write_bytes(source.data)
        (temporary / MANIFEST_NAME).write_bytes(_canonical_json(manifest))
        verify_snapshot(temporary)
        os.replace(temporary, destination)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    pointer = {"snapshot_id": snapshot_id}
    pointer_temp = cache_dir / ".current.json.tmp"
    pointer_temp.write_bytes(_canonical_json(pointer))
    os.replace(pointer_temp, cache_dir / "current.json")
    return destination
