"""Public-facing documentation stays aligned with canonical artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
GUIDE = (ROOT / "docs" / "interpretation-guide.md").read_text(encoding="utf-8")
LATEST = json.loads((ROOT / "public" / "data" / "latest.json").read_text(encoding="utf-8"))
with (ROOT / "public" / "data" / "ppg.csv").open(encoding="utf-8", newline="") as handle:
    LATEST_ROW = list(csv.DictReader(handle))[-1]


def signed_percent(value: float) -> str:
    return f"{value:+.1f}%"


def test_readme_headline_matches_latest_artifact() -> None:
    period = LATEST["observation_period"].replace("-", " ")

    assert period in README
    assert f"{LATEST['value']:,.1f}" in README
    assert signed_percent(LATEST["changes"]["quarter_over_quarter_percent"]) in README
    assert signed_percent(LATEST["changes"]["year_over_year_percent"]) in README
    assert ("**Stale**" in README) is LATEST["stale"]
    assert LATEST["snapshot_id"] in README


def test_displayed_components_match_latest_csv_row() -> None:
    market_component = float(LATEST_ROW["market_component"])
    paycheck_component = float(LATEST_ROW["paycheck_component"])
    relative_factor = float(LATEST_ROW["ppg"]) / 100

    for document in (README, GUIDE):
        assert f"{market_component:,.1f}" in document
        assert f"{paycheck_component:,.1f}" in document
        assert f"{relative_factor:.2f}" in document


def test_readme_surfaces_canonical_public_resources() -> None:
    for target in (
        "public/data/ppg.csv",
        "public/data/latest.json",
        "public/data/ppg.svg",
        "public/data/provenance.json",
        "methodology/v0.1.md",
        "docs/interpretation-guide.md",
    ):
        assert target in README


def test_interpretation_keeps_populations_and_claims_separate() -> None:
    combined = f"{README}\n{GUIDE}".lower()

    assert "does not measure the portfolio holdings" in combined
    assert "not a percentage gap" in combined
    assert "not its cause" in combined
    assert "changing cross-sectional median" in combined
