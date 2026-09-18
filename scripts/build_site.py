#!/usr/bin/env python3
"""Render the static public page from canonical PPG artifacts."""

from __future__ import annotations

import argparse
import csv
import difflib
import html
import json
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path
from string import Template
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "public" / "data"
TEMPLATE_PATH = ROOT / "site" / "index.html.template"
OUTPUT_PATH = ROOT / "public" / "index.html"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def display_period(period: str) -> str:
    return period.replace("-", " ")


def display_date(value: str) -> str:
    parsed = date.fromisoformat(value)
    return f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"


def display_generated_date(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    return f"{parsed.strftime('%B')} {parsed.day}, {parsed.year}"


def signed_percent(value: float) -> str:
    return f"{value:+.1f}%"


def render() -> str:
    latest = load_json(DATA_DIR / "latest.json")
    provenance = load_json(DATA_DIR / "provenance.json")
    chart = ET.parse(DATA_DIR / "ppg.svg").getroot()
    with (DATA_DIR / "ppg.csv").open(encoding="utf-8", newline="") as handle:
        observations = list(csv.DictReader(handle))

    if not observations:
        raise ValueError("public/data/ppg.csv has no observations")

    final_row = observations[-1]
    period = str(latest["observation_period"])
    if final_row["quarter"] != period:
        raise ValueError("latest.json and ppg.csv disagree on the latest quarter")
    if float(final_row["ppg"]) != float(latest["value"]):
        raise ValueError("latest.json and ppg.csv disagree on the latest PPG value")
    if provenance["snapshot_id"] != latest["snapshot_id"]:
        raise ValueError("latest.json and provenance.json disagree on the snapshot")
    if provenance["methodology_version"] != latest["methodology_version"]:
        raise ValueError("latest.json and provenance.json disagree on the methodology version")
    if chart.attrib.get("data-latest-quarter") != period:
        raise ValueError("latest.json and ppg.svg disagree on the latest quarter")
    if chart.attrib.get("data-snapshot-id") != latest["snapshot_id"]:
        raise ValueError("latest.json and ppg.svg disagree on the snapshot")

    stale = bool(latest["stale"])
    values = {
        "first_period": display_period(observations[0]["quarter"]),
        "generated_date": display_generated_date(str(provenance["generated_at"])),
        "market_component": f"{float(final_row['market_component']):,.1f}",
        "methodology_version": str(latest["methodology_version"]),
        "observation_count": f"{len(observations):,}",
        "observation_date": display_date(str(latest["observation_date"])),
        "observation_date_iso": str(latest["observation_date"]),
        "paycheck_component": f"{float(final_row['paycheck_component']):,.1f}",
        "period": display_period(period),
        "period_code": period,
        "qoq": signed_percent(float(latest["changes"]["quarter_over_quarter_percent"])),
        "snapshot_id": str(latest["snapshot_id"]),
        "status_class": "stale" if stale else "current",
        "status_label": "Stale reading" if stale else "Current reading",
        "status_note": (
            "No newer mutually complete market and paycheck quarter is available. "
            "The missing value is not estimated."
            if stale
            else "This is the newest mutually complete market and paycheck quarter."
        ),
        "value": f"{float(latest['value']):,.1f}",
        "yoy": signed_percent(float(latest["changes"]["year_over_year_percent"])),
    }
    escaped = {key: html.escape(value, quote=True) for key, value in values.items()}
    template = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return template.substitute(escaped).rstrip() + "\n"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary_name, path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if public/index.html does not match a fresh render",
    )
    args = parser.parse_args()
    rendered = render()

    if args.check:
        existing = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if existing != rendered:
            diff = difflib.unified_diff(
                existing.splitlines(),
                rendered.splitlines(),
                fromfile=str(OUTPUT_PATH.relative_to(ROOT)),
                tofile="fresh render",
                lineterm="",
            )
            print("\n".join(diff), file=sys.stderr)
            print("error: public page is stale; run `make site`", file=sys.stderr)
            return 1
        print("ok  public/index.html matches canonical artifacts")
        return 0

    write_atomic(OUTPUT_PATH, rendered)
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
