"""Cross-artifact validation for canonical PPG outputs."""

from __future__ import annotations

import csv
import io
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from .rendering import CSV_FIELDS, ArtifactSet


class PPGError(Exception):
    """Base class for expected PPG validation and build failures."""


@dataclass(frozen=True, slots=True)
class ArtifactSummary:
    latest_quarter: str
    latest_ppg: float
    rows: int
    snapshot_id: str


def _json_object(raw: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PPGError(f"{label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise PPGError(f"{label} must be a JSON object")
    return value


def validate_artifacts(artifacts: ArtifactSet) -> ArtifactSummary:
    """Prove that all four artifacts describe the same latest reading."""

    reader = csv.DictReader(io.StringIO(artifacts.csv.decode("utf-8")))
    if reader.fieldnames != CSV_FIELDS:
        raise PPGError(f"CSV columns differ from the public schema: {reader.fieldnames}")
    rows = list(reader)
    if not rows:
        raise PPGError("CSV contains no observations")
    six_decimals = re.compile(r"^-?\d+\.\d{6}$")
    for row in rows:
        for field in ("market_component", "paycheck_component", "ppg"):
            if not six_decimals.fullmatch(row[field]):
                raise PPGError(f"CSV {field} is not serialized to six decimals")
        if not row["paycheck_value"] or float(row["paycheck_value"]) <= 0:
            raise PPGError("CSV paycheck value must be positive")
    latest_row = rows[-1]
    latest_quarter = latest_row["quarter"]
    latest_ppg = float(latest_row["ppg"])

    latest = _json_object(artifacts.latest_json, "latest.json")
    provenance = _json_object(artifacts.provenance_json, "provenance.json")
    try:
        svg = ET.fromstring(artifacts.svg)
    except ET.ParseError as error:
        raise PPGError("ppg.svg is not valid XML") from error
    svg_title = svg.find("{http://www.w3.org/2000/svg}title")
    svg_description = svg.find("{http://www.w3.org/2000/svg}desc")
    if (
        svg_title is None
        or not svg_title.text
        or svg_description is None
        or not svg_description.text
    ):
        raise PPGError("ppg.svg lacks an accessible title or description")

    periods = {
        latest_quarter,
        str(latest.get("observation_period")),
        str(provenance.get("latest_quarter")),
        str(svg.get("data-latest-quarter")),
        artifacts.latest_quarter,
    }
    values = {
        f"{latest_ppg:.6f}",
        f"{float(latest.get('value')):.6f}",
        str(svg.get("data-latest-value")),
        f"{artifacts.latest_ppg:.6f}",
    }
    if len(periods) != 1:
        raise PPGError(f"artifact latest quarters disagree: {sorted(periods)}")
    if len(values) != 1:
        raise PPGError(f"artifact latest PPG values disagree: {sorted(values)}")
    if latest.get("provenance") != "provenance.json":
        raise PPGError("latest.json has an invalid provenance reference")
    snapshot_ids = {
        str(latest.get("snapshot_id")),
        str(provenance.get("snapshot_id")),
        str(svg.get("data-snapshot-id")),
    }
    if len(snapshot_ids) != 1:
        raise PPGError("artifact snapshot identities disagree")
    return ArtifactSummary(latest_quarter, latest_ppg, len(rows), snapshot_ids.pop())


def validate_artifact_directory(path: Path) -> ArtifactSummary:
    """Load and validate the canonical files in a publication directory."""

    required = {
        "ppg.csv": "csv",
        "latest.json": "latest_json",
        "ppg.svg": "svg",
        "provenance.json": "provenance_json",
    }
    try:
        data = {attribute: (path / name).read_bytes() for name, attribute in required.items()}
    except OSError as error:
        raise PPGError(f"cannot read canonical artifacts from {path}") from error
    latest = _json_object(data["latest_json"], "latest.json")
    return validate_artifacts(
        ArtifactSet(
            **data,
            latest_quarter=str(latest.get("observation_period")),
            latest_ppg=float(latest.get("value")),
        )
    )
