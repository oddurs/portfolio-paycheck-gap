from __future__ import annotations

import csv
import io
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from ppg_index.publication import build_artifacts, publish_artifacts
from ppg_index.rendering import CSV_FIELDS, RenderingError, render_artifacts
from ppg_index.sources import resolve_current, verify_snapshot
from ppg_index.validation import PPGError, validate_artifacts

ROOT = Path(__file__).resolve().parents[1]


def canonical_publication():
    return build_artifacts(ROOT / "data")


def canonical_manifest() -> dict[str, object]:
    snapshot = resolve_current(ROOT / "data")
    assert snapshot is not None
    return verify_snapshot(snapshot)


def test_artifacts_match_public_contract_and_latest_reading() -> None:
    publication = canonical_publication()
    summary = validate_artifacts(publication.artifacts)
    assert summary.rows == 187
    assert summary.latest_quarter == "2025-Q3"
    assert summary.latest_ppg == pytest.approx(4217.405914)

    reader = csv.DictReader(io.StringIO(publication.artifacts.csv.decode()))
    assert reader.fieldnames == CSV_FIELDS
    rows = list(reader)
    assert rows[0]["quarter"] == "1979-Q1"
    assert rows[-1]["ppg"] == "4217.405914"

    latest = json.loads(publication.artifacts.latest_json)
    assert latest == {
        "base": "1980-Q1 = 100",
        "changes": {
            "quarter_over_quarter_percent": 7.627364,
            "year_over_year_percent": 13.979511,
        },
        "methodology_version": "0.1",
        "observation_date": "2025-09-30",
        "observation_period": "2025-Q3",
        "provenance": "provenance.json",
        "snapshot_id": "4156e87c2524a9ce",
        "stale": True,
        "unit": "index points",
        "value": 4217.405914,
    }


def test_svg_is_accessible_and_self_describing() -> None:
    svg = canonical_publication().artifacts.svg.decode()
    assert 'role="img"' in svg
    assert 'aria-labelledby="chart-title chart-desc"' in svg
    assert "<title" in svg and "<desc" in svg
    assert "Index level (1980-Q1 = 100)" in svg
    assert "JKP Global Factor Data" in svg
    assert "BLS LES1252881500" in svg
    assert 'data-latest-quarter="2025-Q3"' in svg
    assert 'data-latest-value="4217.405914"' in svg


def test_repeated_builds_are_byte_identical() -> None:
    first = canonical_publication().artifacts
    second = canonical_publication().artifacts
    assert first.files() == second.files()


def test_empty_result_cannot_render_or_publish() -> None:
    publication = canonical_publication()
    empty = replace(publication.calculation, observations=())
    with pytest.raises(RenderingError, match="empty"):
        render_artifacts(empty, canonical_manifest())


def test_older_result_cannot_overwrite_newer_valid_artifacts(tmp_path: Path) -> None:
    publication = canonical_publication()
    latest = publication.calculation.observations[-1]
    newer_row = replace(
        latest,
        quarter="2026-Q1",
        quarter_end=date(2026, 3, 31),
        ppg=4300.0,
        ppg_change_qoq_percent=100 * (4300 / latest.ppg - 1),
        ppg_change_yoy_percent=5.0,
    )
    newer_result = replace(
        publication.calculation,
        observations=(*publication.calculation.observations, newer_row),
        latest_input_quarter="2026-Q1",
        latest_complete_quarter="2026-Q1",
        stale=False,
    )
    newer = render_artifacts(newer_result, canonical_manifest())
    output = tmp_path / "public-data"
    publish_artifacts(output, newer)
    before = {path.name: path.read_bytes() for path in output.iterdir()}

    with pytest.raises(PPGError, match="stale 2025-Q3 input"):
        publish_artifacts(output, publication.artifacts)
    assert {path.name: path.read_bytes() for path in output.iterdir()} == before


def test_cross_artifact_mismatch_fails_before_write() -> None:
    artifacts = canonical_publication().artifacts
    latest = json.loads(artifacts.latest_json)
    latest["value"] = 1
    corrupted = replace(
        artifacts,
        latest_json=(json.dumps(latest, sort_keys=True) + "\n").encode(),
    )
    with pytest.raises(PPGError, match="values disagree"):
        validate_artifacts(corrupted)
