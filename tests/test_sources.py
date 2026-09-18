from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

from ppg_index.sources import SnapshotError, acquire_snapshot, resolve_current, verify_snapshot
from ppg_index.sources.adapters import (
    SourceValidationError,
    normalize_market,
    normalize_paycheck,
    normalize_treasury,
)
from ppg_index.sources.config import BLS_IDENTIFIER, BLS_URL, FRED_URL, JKP_URL

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def canonical_snapshot() -> Path:
    snapshot = resolve_current(DATA)
    assert snapshot is not None
    return snapshot


def raw_source_map(snapshot: Path) -> dict[str, bytes]:
    result = {
        JKP_URL: (snapshot / "raw/jkp-usa-mkt-monthly-vw.zip").read_bytes(),
        FRED_URL: (snapshot / "raw/fred-tb3ms.csv").read_bytes(),
    }
    for path in sorted((snapshot / "raw").glob("bls-*.json")):
        start, end = path.stem.rsplit("-", 2)[-2:]
        result[f"{BLS_URL}?startyear={start}&endyear={end}"] = path.read_bytes()
    return result


def test_committed_snapshot_and_checksums_are_valid() -> None:
    snapshot = canonical_snapshot()
    manifest = verify_snapshot(snapshot)
    assert manifest["snapshot_id"] == snapshot.name
    assert [source["name"] for source in manifest["sources"]] == [
        "market",
        "treasury",
        "paycheck",
    ]


def test_raw_snapshot_replays_to_byte_identical_normalized_inputs() -> None:
    snapshot = canonical_snapshot()
    market = normalize_market((snapshot / "raw/jkp-usa-mkt-monthly-vw.zip").read_bytes())
    treasury = normalize_treasury((snapshot / "raw/fred-tb3ms.csv").read_bytes())
    paycheck = normalize_paycheck(
        [path.read_bytes() for path in sorted((snapshot / "raw").glob("bls-*.json"))]
    )
    for name, normalized in (
        ("market", market),
        ("treasury", treasury),
        ("paycheck", paycheck),
    ):
        assert normalized.data == (snapshot / f"normalized/{name}.csv").read_bytes()


def test_offline_fetcher_preserves_raw_bytes(tmp_path: Path) -> None:
    expected = raw_source_map(canonical_snapshot())
    created = acquire_snapshot(
        tmp_path,
        end_year=2026,
        retrieved_at="2026-09-17T16:00:00Z",
        fetcher=expected.__getitem__,
    )
    verify_snapshot(created)
    actual = raw_source_map(created)
    assert actual == expected


def test_duplicate_or_wrong_source_identity_is_rejected() -> None:
    snapshot = canonical_snapshot()
    treasury = (snapshot / "raw/fred-tb3ms.csv").read_bytes()
    first_observation = treasury.splitlines(keepends=True)[1]
    with pytest.raises(SourceValidationError, match="duplicate FRED month"):
        normalize_treasury(treasury + first_observation)

    paycheck = (snapshot / "raw/bls-LES1252881500-2019-2026.json").read_bytes()
    wrong_series = paycheck.replace(BLS_IDENTIFIER.encode(), b"WRONG_SERIES", 1)
    with pytest.raises(SourceValidationError, match="series identifier"):
        normalize_paycheck([wrong_series])


def test_checksum_tampering_is_rejected(tmp_path: Path) -> None:
    expected = raw_source_map(canonical_snapshot())
    created = acquire_snapshot(
        tmp_path,
        end_year=2026,
        retrieved_at="2026-09-17T16:00:00Z",
        fetcher=expected.__getitem__,
    )
    path = created / "normalized/market.csv"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(SnapshotError, match="checksum mismatch"):
        verify_snapshot(created)


def test_changed_overlap_is_quarantined_until_explicitly_accepted(tmp_path: Path) -> None:
    expected = raw_source_map(canonical_snapshot())
    acquire_snapshot(
        tmp_path,
        end_year=2026,
        retrieved_at="2026-09-17T16:00:00Z",
        fetcher=expected.__getitem__,
    )

    original = expected[JKP_URL]
    with zipfile.ZipFile(BytesIO(original)) as archive:
        member = archive.namelist()[0]
        csv_data = archive.read(member)
    lines = csv_data.splitlines(keepends=True)
    columns = lines[1].decode().rstrip("\r\n").split(",")
    columns[-1] = str(float(columns[-1]) + 0.000001)
    lines[1] = (",".join(columns) + "\n").encode()
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, b"".join(lines))
    revised = {**expected, JKP_URL: buffer.getvalue()}

    with pytest.raises(SnapshotError, match="unexpected source revision"):
        acquire_snapshot(
            tmp_path,
            end_year=2026,
            retrieved_at="2026-09-18T16:00:00Z",
            fetcher=revised.__getitem__,
        )
    pointer = json.loads((tmp_path / "current.json").read_text())
    assert pointer["snapshot_id"] == canonical_snapshot().name
