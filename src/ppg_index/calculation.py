"""Pure implementation of the frozen PPG v0.1 calculation methodology.

The public functions accept in-memory values. This module deliberately knows
nothing about URLs, filesystem locations, caches, or presentation artifacts.
"""

from __future__ import annotations

import calendar
import csv
import io
import math
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

BASE_QUARTER = "1980-Q1"
FIRST_PUBLIC_QUARTER = "1979-Q1"
BILL_TERM_DAYS = 91
DISCOUNT_YEAR_DAYS = 360
_MONTH = re.compile(r"^(\d{4})-(0[1-9]|1[0-2])$")
_QUARTER = re.compile(r"^(\d{4})-Q([1-4])$")


class CalculationError(ValueError):
    """Input values cannot produce a conforming PPG result."""


@dataclass(frozen=True, slots=True)
class MarketInput:
    """One decimal monthly US-dollar equity excess return."""

    month: str
    excess_return: float


@dataclass(frozen=True, slots=True)
class TreasuryInput:
    """One annualized Treasury discount quote, in percent per year."""

    month: str
    annual_discount_yield_percent: float


@dataclass(frozen=True, slots=True)
class PaycheckInput:
    """One quarterly median weekly paycheck, in current US dollars."""

    quarter: str
    value: float | None
    missing_reason: str = ""


@dataclass(frozen=True, slots=True)
class MonthlyTrace:
    """Unrounded monthly calculation intermediates and wealth path."""

    month: str
    excess_return: float
    annual_discount_yield_percent: float
    calendar_days: int
    bill_term_days: int
    bill_price: float
    treasury_return: float
    market_return: float
    market_wealth: float


@dataclass(frozen=True, slots=True)
class QuarterlyObservation:
    """Unrounded PPG component and headline values for one complete quarter."""

    quarter: str
    quarter_end: date
    market_value: float
    paycheck_value: float
    market_component: float
    paycheck_component: float
    ppg: float
    ppg_change_qoq_percent: float | None
    ppg_change_yoy_percent: float | None


@dataclass(frozen=True, slots=True)
class CalculationResult:
    """Complete engine output plus freshness metadata."""

    monthly_trace: tuple[MonthlyTrace, ...]
    observations: tuple[QuarterlyObservation, ...]
    latest_input_quarter: str
    latest_complete_quarter: str
    stale: bool


def _read_csv(raw: bytes, expected: list[str], label: str) -> list[dict[str, str]]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise CalculationError(f"{label} input must be UTF-8") from error
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != expected:
        raise CalculationError(f"{label} schema must be {expected}, received {reader.fieldnames}")
    return list(reader)


def _number(value: str, label: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise CalculationError(f"{label} is not numeric: {value!r}") from error
    if not math.isfinite(parsed):
        raise CalculationError(f"{label} must be finite")
    return parsed


def parse_normalized_inputs(
    market_csv: bytes,
    treasury_csv: bytes,
    paycheck_csv: bytes,
) -> tuple[list[MarketInput], list[TreasuryInput], list[PaycheckInput]]:
    """Parse the exact normalized CSV schemas without accessing a filesystem."""

    market_rows = _read_csv(market_csv, ["month", "excess_return"], "market")
    treasury_rows = _read_csv(treasury_csv, ["month", "discount_rate_percent"], "treasury")
    paycheck_rows = _read_csv(paycheck_csv, ["quarter", "value", "missing_reason"], "paycheck")
    market = [
        MarketInput(row["month"], _number(row["excess_return"], "market excess return"))
        for row in market_rows
    ]
    treasury = [
        TreasuryInput(
            row["month"],
            _number(row["discount_rate_percent"], "Treasury discount rate"),
        )
        for row in treasury_rows
    ]
    paycheck = [
        PaycheckInput(
            row["quarter"],
            None if row["value"] == "" else _number(row["value"], "paycheck value"),
            row["missing_reason"],
        )
        for row in paycheck_rows
    ]
    return market, treasury, paycheck


def _month_ordinal(month: str) -> int:
    match = _MONTH.fullmatch(month)
    if match is None:
        raise CalculationError(f"invalid month label: {month!r}")
    return int(match[1]) * 12 + int(match[2]) - 1


def _quarter_ordinal(quarter: str) -> int:
    match = _QUARTER.fullmatch(quarter)
    if match is None:
        raise CalculationError(f"invalid quarter label: {quarter!r}")
    return int(match[1]) * 4 + int(match[2]) - 1


def _month_from_ordinal(ordinal: int) -> str:
    year, zero_based_month = divmod(ordinal, 12)
    return f"{year:04d}-{zero_based_month + 1:02d}"


def _quarter_from_ordinal(ordinal: int) -> str:
    year, zero_based_quarter = divmod(ordinal, 4)
    return f"{year:04d}-Q{zero_based_quarter + 1}"


def _quarter_for_month(month: str) -> str:
    match = _MONTH.fullmatch(month)
    if match is None:
        raise CalculationError(f"invalid month label: {month!r}")
    return f"{match[1]}-Q{(int(match[2]) - 1) // 3 + 1}"


def _quarter_end(quarter: str) -> date:
    match = _QUARTER.fullmatch(quarter)
    if match is None:
        raise CalculationError(f"invalid quarter label: {quarter!r}")
    year, quarter_number = int(match[1]), int(match[2])
    month = quarter_number * 3
    return date(year, month, calendar.monthrange(year, month)[1])


def _validate_ordered_months(values: Sequence[object], label: str) -> list[int]:
    if not values:
        raise CalculationError(f"{label} input is empty")
    ordinals: list[int] = []
    for item in values:
        ordinal = _month_ordinal(item.month)  # type: ignore[attr-defined]
        if ordinals and ordinal == ordinals[-1]:
            raise CalculationError(f"duplicate {label} month: {item.month}")  # type: ignore[attr-defined]
        if ordinals and ordinal < ordinals[-1]:
            raise CalculationError(f"{label} observations are out of order at {item.month}")  # type: ignore[attr-defined]
        if ordinals and ordinal != ordinals[-1] + 1:
            expected = _month_from_ordinal(ordinals[-1] + 1)
            raise CalculationError(f"missing {label} month: expected {expected}")
        ordinals.append(ordinal)
    return ordinals


def _validate_inputs(
    market: Sequence[MarketInput],
    treasury: Sequence[TreasuryInput],
    paycheck: Sequence[PaycheckInput],
) -> None:
    _validate_ordered_months(market, "market")
    _validate_ordered_months(treasury, "Treasury")
    if not paycheck:
        raise CalculationError("paycheck input is empty")

    for item in market:
        if not math.isfinite(item.excess_return) or item.excess_return <= -1:
            raise CalculationError(f"invalid market excess return for {item.month}")
    for item in treasury:
        if not math.isfinite(item.annual_discount_yield_percent):
            raise CalculationError(f"nonfinite Treasury quote for {item.month}")

    prior: int | None = None
    for item in paycheck:
        ordinal = _quarter_ordinal(item.quarter)
        if prior is not None and ordinal == prior:
            raise CalculationError(f"duplicate paycheck quarter: {item.quarter}")
        if prior is not None and ordinal < prior:
            raise CalculationError(f"paycheck observations are out of order at {item.quarter}")
        if prior is not None and ordinal != prior + 1:
            raise CalculationError(
                f"missing paycheck quarter: expected {_quarter_from_ordinal(prior + 1)}"
            )
        if item.value is not None and (not math.isfinite(item.value) or item.value <= 0):
            raise CalculationError(f"invalid paycheck value for {item.quarter}")
        if item.value is None and not item.missing_reason:
            raise CalculationError(f"missing paycheck has no reason for {item.quarter}")
        prior = ordinal


def _latest_complete_market_quarter(last_month: str) -> str:
    ordinal = _month_ordinal(last_month)
    year, zero_based_month = divmod(ordinal, 12)
    complete_month = ((zero_based_month + 1) // 3) * 3
    if complete_month == 0:
        return f"{year - 1:04d}-Q4"
    return f"{year:04d}-Q{complete_month // 3}"


def calculate_ppg(
    market: Sequence[MarketInput],
    treasury: Sequence[TreasuryInput],
    paycheck: Sequence[PaycheckInput],
) -> CalculationResult:
    """Calculate PPG from validated monthly and quarterly in-memory inputs."""

    _validate_inputs(market, treasury, paycheck)
    market_by_month = {item.month: item.excess_return for item in market}
    treasury_by_month = {item.month: item.annual_discount_yield_percent for item in treasury}
    paycheck_by_quarter = {item.quarter: item for item in paycheck}

    first_month = "1979-01"
    last_month_ordinal = min(_month_ordinal(market[-1].month), _month_ordinal(treasury[-1].month))
    first_month_ordinal = _month_ordinal(first_month)
    if last_month_ordinal < first_month_ordinal:
        raise CalculationError("monthly inputs do not reach the publication range")

    monthly_trace: list[MonthlyTrace] = []
    quarter_market: dict[str, float] = {}
    wealth = 1.0
    for ordinal in range(first_month_ordinal, last_month_ordinal + 1):
        month = _month_from_ordinal(ordinal)
        if month not in market_by_month:
            raise CalculationError(f"missing market month in publication range: {month}")
        if month not in treasury_by_month:
            raise CalculationError(f"missing Treasury month in publication range: {month}")
        excess_return = market_by_month[month]
        annual_yield = treasury_by_month[month]
        year, month_number = map(int, month.split("-"))
        days = calendar.monthrange(year, month_number)[1]
        bill_price = 1 - (annual_yield / 100) * (BILL_TERM_DAYS / DISCOUNT_YEAR_DAYS)
        if not math.isfinite(bill_price) or not 0 < bill_price <= 1:
            raise CalculationError(f"unsupported Treasury quote for {month}")
        treasury_return = bill_price ** (-days / BILL_TERM_DAYS) - 1
        market_return = excess_return + treasury_return
        if not math.isfinite(market_return) or market_return <= -1:
            raise CalculationError(f"invalid reconstructed market return for {month}")
        wealth *= 1 + market_return
        if not math.isfinite(wealth) or wealth <= 0:
            raise CalculationError(f"invalid market wealth for {month}")
        monthly_trace.append(
            MonthlyTrace(
                month,
                excess_return,
                annual_yield,
                days,
                BILL_TERM_DAYS,
                bill_price,
                treasury_return,
                market_return,
                wealth,
            )
        )
        if month_number in {3, 6, 9, 12}:
            quarter_market[_quarter_for_month(month)] = wealth

    latest_input_quarter = min(
        _latest_complete_market_quarter(_month_from_ordinal(last_month_ordinal)),
        paycheck[-1].quarter,
    )
    first_ordinal = _quarter_ordinal(FIRST_PUBLIC_QUARTER)
    last_ordinal = _quarter_ordinal(latest_input_quarter)
    if last_ordinal < _quarter_ordinal(BASE_QUARTER):
        raise CalculationError(f"inputs do not include base quarter {BASE_QUARTER}")

    complete_quarters: list[str] = []
    for ordinal in range(first_ordinal, last_ordinal + 1):
        quarter = _quarter_from_ordinal(ordinal)
        if quarter not in quarter_market:
            raise CalculationError(f"missing market quarter: {quarter}")
        if quarter not in paycheck_by_quarter:
            raise CalculationError(f"missing paycheck quarter: {quarter}")
        if paycheck_by_quarter[quarter].value is None:
            if ordinal != last_ordinal:
                raise CalculationError(f"missing historical paycheck value: {quarter}")
            continue
        complete_quarters.append(quarter)

    if not complete_quarters:
        raise CalculationError("no complete publication quarters")
    if BASE_QUARTER not in complete_quarters:
        raise CalculationError(f"base quarter {BASE_QUARTER} is incomplete")
    latest_complete = complete_quarters[-1]
    stale = latest_complete != latest_input_quarter
    base_market = quarter_market[BASE_QUARTER]
    base_paycheck = paycheck_by_quarter[BASE_QUARTER].value
    assert base_paycheck is not None

    observations: list[QuarterlyObservation] = []
    for quarter in complete_quarters:
        paycheck_value = paycheck_by_quarter[quarter].value
        assert paycheck_value is not None
        market_component = 100 * quarter_market[quarter] / base_market
        paycheck_component = 100 * paycheck_value / base_paycheck
        ppg = 100 * market_component / paycheck_component
        direct = 100 * (quarter_market[quarter] / base_market) / (paycheck_value / base_paycheck)
        if not math.isclose(ppg, direct, rel_tol=0, abs_tol=0.0000005):
            raise CalculationError(f"direct-ratio invariant failed for {quarter}")
        if quarter == BASE_QUARTER:
            market_component = paycheck_component = ppg = 100.0
        prior_ppg = observations[-1].ppg if observations else None
        year_prior_ppg = observations[-4].ppg if len(observations) >= 4 else None
        observations.append(
            QuarterlyObservation(
                quarter=quarter,
                quarter_end=_quarter_end(quarter),
                market_value=quarter_market[quarter],
                paycheck_value=paycheck_value,
                market_component=market_component,
                paycheck_component=paycheck_component,
                ppg=ppg,
                ppg_change_qoq_percent=(None if prior_ppg is None else 100 * (ppg / prior_ppg - 1)),
                ppg_change_yoy_percent=(
                    None if year_prior_ppg is None else 100 * (ppg / year_prior_ppg - 1)
                ),
            )
        )

    return CalculationResult(
        monthly_trace=tuple(monthly_trace),
        observations=tuple(observations),
        latest_input_quarter=latest_input_quarter,
        latest_complete_quarter=latest_complete,
        stale=stale,
    )
