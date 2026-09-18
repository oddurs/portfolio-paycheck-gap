#!/usr/bin/env python3
"""Explicitly regenerate the full-history calculation golden file."""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ppg_index.calculation import calculate_ppg, parse_normalized_inputs  # noqa: E402
from ppg_index.sources import resolve_current, verify_snapshot  # noqa: E402
from ppg_index.sources.adapters import (  # noqa: E402
    normalize_market,
    normalize_paycheck,
    normalize_treasury,
)

GOLDEN = ROOT / "tests" / "fixtures" / "golden" / "ppg-calculation.csv"
FIELDS = [
    "quarter",
    "quarter_end",
    "paycheck_value",
    "market_component",
    "paycheck_component",
    "ppg",
    "ppg_change_qoq_percent",
    "ppg_change_yoy_percent",
]


def _six(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def build_golden(root: Path = ROOT) -> bytes:
    """Replay exact raw responses and serialize the calculation contract."""

    snapshot = resolve_current(root / "data")
    if snapshot is None:
        raise ValueError("data/current.json does not select a snapshot")
    verify_snapshot(snapshot)
    market = normalize_market((snapshot / "raw/jkp-usa-mkt-monthly-vw.zip").read_bytes())
    treasury = normalize_treasury((snapshot / "raw/fred-tb3ms.csv").read_bytes())
    paycheck = normalize_paycheck(
        [path.read_bytes() for path in sorted((snapshot / "raw").glob("bls-*.json"))]
    )
    result = calculate_ppg(*parse_normalized_inputs(market.data, treasury.data, paycheck.data))

    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
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
                "ppg_change_qoq_percent": _six(item.ppg_change_qoq_percent),
                "ppg_change_yoy_percent": _six(item.ppg_change_yoy_percent),
            }
        )
    return output.getvalue().encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate the reviewed full-history golden calculation."
    )
    parser.add_argument(
        "--accept",
        action="store_true",
        help="Confirm that the resulting historical output change is intentional.",
    )
    args = parser.parse_args(argv)
    if not args.accept:
        parser.error("refusing to update golden data without --accept")
    data = build_golden()
    GOLDEN.parent.mkdir(parents=True, exist_ok=True)
    GOLDEN.write_bytes(data)
    print(f"wrote {GOLDEN.relative_to(ROOT)} ({data.count(bytes([10])) - 1} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
