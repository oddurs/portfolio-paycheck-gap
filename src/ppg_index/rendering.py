"""Pure deterministic serialization of validated PPG results."""

from __future__ import annotations

import csv
import io
import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape

from .calculation import BASE_QUARTER, CalculationResult, QuarterlyObservation

METHODOLOGY_VERSION = "0.1"
SOURCE_NOTICE = (
    "Market: Jensen, Kelly, and Pedersen Global Factor Data, modified, CC BY-NC 4.0 "
    "(noncommercial). Treasury: Board of Governors of the Federal Reserve System via "
    "FRED TB3MS. Paycheck: U.S. Bureau of Labor Statistics LES1252881500. BLS.gov "
    "cannot vouch for the data or analyses derived from these data after the data have "
    "been retrieved from BLS.gov."
)
CSV_FIELDS = [
    "quarter",
    "quarter_end",
    "paycheck_value",
    "market_component",
    "paycheck_component",
    "ppg",
]


class RenderingError(ValueError):
    """A validated result cannot be serialized as canonical artifacts."""


@dataclass(frozen=True, slots=True)
class ArtifactSet:
    """Canonical artifact bytes generated from one calculation result."""

    csv: bytes
    latest_json: bytes
    svg: bytes
    provenance_json: bytes
    latest_quarter: str
    latest_ppg: float

    def files(self) -> dict[str, bytes]:
        return {
            "ppg.csv": self.csv,
            "latest.json": self.latest_json,
            "ppg.svg": self.svg,
            "provenance.json": self.provenance_json,
        }


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def _six(value: float) -> str:
    return f"{value:.6f}"


def _source_map(manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    sources = manifest.get("sources")
    if not isinstance(sources, list):
        raise RenderingError("source manifest has no sources list")
    result: dict[str, dict[str, object]] = {}
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("name"), str):
            raise RenderingError("source manifest contains an invalid source")
        result[str(source["name"])] = source
    if set(result) != {"market", "treasury", "paycheck"}:
        raise RenderingError("source manifest must contain market, treasury, and paycheck")
    return result


def _raw_bundle_digest(source: dict[str, object]) -> str:
    bundle = source.get("raw_bundle_sha256")
    if isinstance(bundle, str) and len(bundle) == 64:
        return bundle
    raw = source.get("raw")
    if not isinstance(raw, list) or not raw:
        raise RenderingError("source manifest has no raw checksum")
    digests: list[str] = []
    for item in raw:
        if not isinstance(item, dict) or not isinstance(item.get("sha256"), str):
            raise RenderingError("source manifest has an invalid raw checksum")
        digests.append(str(item["sha256"]))
    if len(digests) == 1:
        return digests[0]
    raise RenderingError("multi-file source manifest lacks a raw bundle checksum")


def _single_raw_digest(source: dict[str, object]) -> str:
    raw = source.get("raw")
    if not isinstance(raw, list) or len(raw) != 1 or not isinstance(raw[0], dict):
        raise RenderingError("source does not contain exactly one raw response")
    digest = raw[0].get("sha256")
    if not isinstance(digest, str):
        raise RenderingError("source manifest has an invalid raw checksum")
    return digest


def _utc_timestamp(value: object, label: str) -> tuple[str, datetime]:
    if not isinstance(value, str):
        raise RenderingError(f"{label} must be an ISO 8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise RenderingError(f"{label} must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None:
        raise RenderingError(f"{label} must include a timezone")
    utc = parsed.astimezone(UTC).replace(microsecond=0)
    return utc.isoformat().replace("+00:00", "Z"), utc


def render_csv(result: CalculationResult) -> bytes:
    if not result.observations:
        raise RenderingError("cannot render an empty result")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for item in result.observations:
        writer.writerow(
            {
                "quarter": item.quarter,
                "quarter_end": item.quarter_end.isoformat(),
                "paycheck_value": format(item.paycheck_value, "g"),
                "market_component": _six(item.market_component),
                "paycheck_component": _six(item.paycheck_component),
                "ppg": _six(item.ppg),
            }
        )
    return output.getvalue().encode("utf-8")


def render_latest_json(result: CalculationResult, snapshot_id: str) -> bytes:
    if not result.observations:
        raise RenderingError("cannot render an empty result")
    item = result.observations[-1]
    return _json_bytes(
        {
            "base": f"{BASE_QUARTER} = 100",
            "changes": {
                "quarter_over_quarter_percent": round(item.ppg_change_qoq_percent, 6)
                if item.ppg_change_qoq_percent is not None
                else None,
                "year_over_year_percent": round(item.ppg_change_yoy_percent, 6)
                if item.ppg_change_yoy_percent is not None
                else None,
            },
            "methodology_version": METHODOLOGY_VERSION,
            "observation_date": item.quarter_end.isoformat(),
            "observation_period": item.quarter,
            "provenance": "provenance.json",
            "snapshot_id": snapshot_id,
            "stale": result.stale,
            "unit": "index points",
            "value": round(item.ppg, 6),
        }
    )


def render_provenance(
    result: CalculationResult,
    manifest: dict[str, object],
    generated_at: str,
) -> bytes:
    if not result.observations:
        raise RenderingError("cannot render an empty result")
    sources = _source_map(manifest)
    snapshot_id = manifest.get("snapshot_id")
    if not isinstance(snapshot_id, str):
        raise RenderingError("source manifest lacks retrieval time or snapshot identity")
    retrieved_at, retrieved_time = _utc_timestamp(manifest.get("retrieved_at"), "retrieved_at")
    generated_at, generated_time = _utc_timestamp(generated_at, "generated_at")
    if generated_time < retrieved_time:
        raise RenderingError("generated_at cannot precede source retrieval")
    source_records = []
    for name in ("market", "treasury", "paycheck"):
        source = sources[name]
        source_records.append(
            {
                "identifier": source.get("identifier"),
                "name": name,
                "raw_bundle_sha256": _raw_bundle_digest(source),
                "release_period": source.get("release_period"),
                "retrieved_at": retrieved_at,
                "url": source.get("url"),
            }
        )
    return _json_bytes(
        {
            "generated_at": generated_at,
            "latest_quarter": result.latest_complete_quarter,
            "market_retrieved_at": retrieved_at,
            "market_sha256": _single_raw_digest(sources["market"]),
            "methodology_version": METHODOLOGY_VERSION,
            "paycheck_retrieved_at": retrieved_at,
            "paycheck_sha256": _raw_bundle_digest(sources["paycheck"]),
            "snapshot_id": snapshot_id,
            "source_notice": SOURCE_NOTICE,
            "sources": source_records,
            "stale": result.stale,
            "treasury_retrieved_at": retrieved_at,
            "treasury_sha256": _single_raw_digest(sources["treasury"]),
        }
    )


def _x(index: int, count: int) -> float:
    return 92 + (index / max(count - 1, 1)) * 1058


def _y(value: float, low: float, high: float) -> float:
    return 535 - (math.log(value) - math.log(low)) / (math.log(high) - math.log(low)) * 420


def _chart_path(rows: tuple[QuarterlyObservation, ...], low: float, high: float) -> str:
    points = [
        f"{_x(index, len(rows)):.2f},{_y(item.ppg, low, high):.2f}"
        for index, item in enumerate(rows)
    ]
    return "M " + " L\n    ".join(points)


def render_svg(result: CalculationResult, snapshot_id: str) -> bytes:
    if not result.observations:
        raise RenderingError("cannot render an empty result")
    rows = result.observations
    latest = rows[-1]
    low = 100.0
    high = 5000.0
    y_ticks = [100, 200, 500, 1000, 2000, 5000]
    x_years = [1980, 1990, 2000, 2010, 2020, int(latest.quarter[:4])]
    first_year = int(rows[0].quarter[:4])
    final_year = int(rows[-1].quarter[:4])
    year_span = max(final_year - first_year, 1)
    grid = []
    for tick in y_ticks:
        y = _y(tick, low, high)
        grid.append(
            f'<line x1="92" y1="{y:.2f}" x2="1150" y2="{y:.2f}" class="grid"/>'
            f'<text x="78" y="{y + 5:.2f}" text-anchor="end" class="tick">{tick:,}</text>'
        )
    x_labels = []
    for year in dict.fromkeys(x_years):
        x = 92 + ((year - first_year) / year_span) * 1058
        x_labels.append(
            f'<line x1="{x:.2f}" y1="535" x2="{x:.2f}" y2="541" class="axis"/>'
            f'<text x="{x:.2f}" y="561" text-anchor="middle" class="tick">{year}</text>'
        )
    path = _chart_path(rows, low, high)
    latest_x = _x(len(rows) - 1, len(rows))
    latest_y = _y(latest.ppg, low, high)
    stale_note = "Latest available; source gap after this quarter." if result.stale else "Current."
    title = "Portfolio-Paycheck Gap Index"
    description = (
        f"Quarterly PPG history from {rows[0].quarter} through {latest.quarter}. "
        f"The latest value is {latest.ppg:.1f} index points, with {BASE_QUARTER} equal to 100."
    )
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675"
  width="1200" height="675" role="img" aria-labelledby="chart-title chart-desc"
  data-latest-quarter="{latest.quarter}" data-latest-value="{latest.ppg:.6f}"
  data-methodology-version="{METHODOLOGY_VERSION}" data-snapshot-id="{snapshot_id}">
  <title id="chart-title">{escape(title)}</title>
  <desc id="chart-desc">{escape(description)}</desc>
  <style>
    .bg {{ fill: #f8f6f0; }}
    .grid {{ stroke: #d9d4c8; stroke-width: 1; }}
    .axis {{ stroke: #4b4b47; stroke-width: 1.5; }}
    .series {{ fill: none; stroke: #0f766e; stroke-width: 4;
      stroke-linejoin: round; stroke-linecap: round; }}
    .base {{ stroke: #b45309; stroke-width: 1.5; stroke-dasharray: 7 6; }}
    .title {{ fill: #17211f; font: 700 30px system-ui, sans-serif; }}
    .subtitle {{ fill: #4b5563; font: 16px system-ui, sans-serif; }}
    .tick {{ fill: #5f625e; font: 13px system-ui, sans-serif; }}
    .label {{ fill: #17211f; font: 600 15px system-ui, sans-serif; }}
    .note {{ fill: #5f625e; font: 12px system-ui, sans-serif; }}
    .latest {{ fill: #0f766e; font: 700 17px system-ui, sans-serif; }}
  </style>
  <rect class="bg" width="1200" height="675"/>
  <text x="60" y="48" class="title">{escape(title)}</text>
  <text x="60" y="76" class="subtitle">Quarterly index • {BASE_QUARTER} = 100 •
    log scale • through {latest.quarter}</text>
  <text x="60" y="99" class="note">{escape(stale_note)}</text>
  <text x="22" y="325" class="label" transform="rotate(-90 22 325)">
    Index level ({BASE_QUARTER} = 100)</text>
  {"".join(grid)}
  <line x1="92" y1="535" x2="1150" y2="535" class="axis"/>
  <line x1="92" y1="115" x2="92" y2="535" class="axis"/>
  {"".join(x_labels)}
  <line x1="92" y1="{_y(100, low, high):.2f}" x2="1150" y2="{_y(100, low, high):.2f}" class="base"/>
  <path d="{path}" class="series"/>
  <circle cx="{latest_x:.2f}" cy="{latest_y:.2f}" r="6" fill="#0f766e"/>
  <text x="{latest_x - 8:.2f}" y="{latest_y - 13:.2f}"
    text-anchor="end" class="latest">{latest.ppg:.1f}</text>
  <text x="60" y="606" class="note">Units: PPG index points.
    Base level: {BASE_QUARTER} = 100. Methodology v{METHODOLOGY_VERSION}.</text>
  <text x="60" y="628" class="note">Sources: JKP Global Factor Data;
    Federal Reserve H.15 via FRED; BLS LES1252881500.</text>
  <text x="60" y="650" class="note">JKP-derived chart: CC BY-NC 4.0,
    modified, noncommercial. Snapshot {snapshot_id}.</text>
</svg>
'''
    return svg.encode("utf-8")


def render_artifacts(
    result: CalculationResult,
    manifest: dict[str, object],
    generated_at: str,
) -> ArtifactSet:
    """Render every canonical output from one validated result and manifest."""

    if not result.observations:
        raise RenderingError("cannot render an empty result")
    snapshot_id = manifest.get("snapshot_id")
    if not isinstance(snapshot_id, str) or not snapshot_id:
        raise RenderingError("source manifest has no snapshot identity")
    latest = result.observations[-1]
    if latest.quarter != result.latest_complete_quarter:
        raise RenderingError("result latest-quarter metadata is inconsistent")
    return ArtifactSet(
        csv=render_csv(result),
        latest_json=render_latest_json(result, snapshot_id),
        svg=render_svg(result, snapshot_id),
        provenance_json=render_provenance(result, manifest, generated_at),
        latest_quarter=latest.quarter,
        latest_ppg=latest.ppg,
    )
