from __future__ import annotations

import csv
import math
from dataclasses import replace
from pathlib import Path

import pytest

from ppg_index.calculation import (
    CalculationError,
    MarketInput,
    PaycheckInput,
    TreasuryInput,
    calculate_ppg,
    parse_normalized_inputs,
)
from ppg_index.sources import resolve_current

ROOT = Path(__file__).resolve().parents[1]


def canonical_inputs() -> tuple[list[MarketInput], list[TreasuryInput], list[PaycheckInput]]:
    snapshot = resolve_current(ROOT / "data")
    assert snapshot is not None
    return parse_normalized_inputs(
        (snapshot / "normalized/market.csv").read_bytes(),
        (snapshot / "normalized/treasury.csv").read_bytes(),
        (snapshot / "normalized/paycheck.csv").read_bytes(),
    )


def test_engine_reproduces_reference_fixture_at_published_precision() -> None:
    result = calculate_ppg(*canonical_inputs())
    actual = {item.quarter: item for item in result.observations}
    with (ROOT / "tests/fixtures/reference-calculation.csv").open(newline="") as handle:
        expected = list(csv.DictReader(handle))

    for row in expected:
        item = actual[row["quarter"]]
        assert item.paycheck_value == float(row["paycheck_value"])
        assert f"{item.market_component:.6f}" == row["market_component"]
        assert f"{item.paycheck_component:.6f}" == row["paycheck_component"]
        assert f"{item.ppg:.6f}" == row["ppg"]


def test_base_freshness_trace_and_comparison_contract() -> None:
    result = calculate_ppg(*canonical_inputs())
    by_quarter = {item.quarter: item for item in result.observations}
    base = by_quarter["1980-Q1"]
    assert (base.market_component, base.paycheck_component, base.ppg) == (100.0, 100.0, 100.0)
    assert result.monthly_trace[0].month == "1979-01"
    assert result.monthly_trace[-1].month == "2025-12"
    assert result.latest_input_quarter == "2025-Q4"
    assert result.latest_complete_quarter == "2025-Q3"
    assert result.stale is True

    latest = result.observations[-1]
    previous = result.observations[-2]
    year_prior = result.observations[-5]
    assert latest.ppg_change_qoq_percent == pytest.approx(100 * (latest.ppg / previous.ppg - 1))
    assert latest.ppg_change_yoy_percent == pytest.approx(100 * (latest.ppg / year_prior.ppg - 1))


def test_normalized_schema_is_exact_and_numeric_values_are_finite() -> None:
    with pytest.raises(CalculationError, match="market schema"):
        parse_normalized_inputs(
            b"month,wrong\n1980-01,0.1\n",
            b"month,discount_rate_percent\n1980-01,10\n",
            b"quarter,value,missing_reason\n1980-Q1,1,\n",
        )
    with pytest.raises(CalculationError, match="must be finite"):
        parse_normalized_inputs(
            b"month,excess_return\n1980-01,nan\n",
            b"month,discount_rate_percent\n1980-01,10\n",
            b"quarter,value,missing_reason\n1980-Q1,1,\n",
        )


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda rows: [rows[0], rows[0], *rows[1:]], "duplicate market month"),
        (lambda rows: [rows[1], rows[0], *rows[2:]], "out of order"),
        (lambda rows: [rows[0], *rows[2:]], "missing market month"),
        (
            lambda rows: [replace(rows[0], excess_return=math.inf), *rows[1:]],
            "invalid market excess return",
        ),
    ],
)
def test_bad_monthly_observations_fail_clearly(mutate: object, message: str) -> None:
    market, treasury, paycheck = canonical_inputs()
    changed = mutate(market)  # type: ignore[operator]
    with pytest.raises(CalculationError, match=message):
        calculate_ppg(changed, treasury, paycheck)


def test_historical_missing_paycheck_fails_but_newest_missing_is_stale() -> None:
    market, treasury, paycheck = canonical_inputs()
    historical = [
        replace(item, value=None, missing_reason="test gap") if item.quarter == "2000-Q1" else item
        for item in paycheck
    ]
    with pytest.raises(CalculationError, match="missing historical paycheck value: 2000-Q1"):
        calculate_ppg(market, treasury, historical)

    result = calculate_ppg(market, treasury, paycheck)
    assert result.stale
    assert result.observations[-1].quarter == "2025-Q3"


def test_invalid_units_domain_fails_at_transformation_boundary() -> None:
    market, treasury, paycheck = canonical_inputs()
    invalid = [
        replace(item, annual_discount_yield_percent=-0.01) if item.month == "1980-01" else item
        for item in treasury
    ]
    with pytest.raises(CalculationError, match="unsupported Treasury quote for 1980-01"):
        calculate_ppg(market, invalid, paycheck)
