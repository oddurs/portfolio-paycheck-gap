#!/usr/bin/env python3
"""Executable sensitivity and edge-case evidence for PPG methodology v0.1."""

from __future__ import annotations

import csv
import hashlib
import io
import math
import statistics
import sys
import zipfile
from calendar import monthrange
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "tests" / "fixtures" / "sources"
SENSITIVITY = ROOT / "tests" / "fixtures" / "sensitivity"
JKP_CURRENT_URL = (
    "https://jkpfactors-data.s3.amazonaws.com/public/%5Busa%5D_%5Bmkt%5D_%5Bmonthly%5D_%5Bvw%5D.zip"
)
JKP_LEGACY_URL = (
    "https://jkpfactors.s3.amazonaws.com/public/%5Busa%5D_%5Bmkt%5D_%5Bmonthly%5D_%5Bvw%5D.zip"
)
JKP_CURRENT_HASH = "8c69cc848ebb447f8c47346a4b3eabed65fac03f0b895b04319f3828e3b6e79f"
JKP_LEGACY_HASH = "0cdeaee6c4980085fae967d70246a79ed0c7274161ba1a3a1d5eeec8bba78f87"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def treasury_return(year: int, month: int, annual_yield: float, mode: str) -> float:
    if mode == "zero":
        return 0.0
    if mode == "simple":
        return annual_yield / 100.0 / 12.0
    days = monthrange(year, month)[1]
    bill_price = 1.0 - (annual_yield / 100.0) * (91.0 / 360.0)
    if not 0.0 < bill_price <= 1.0:
        raise ValueError("Treasury discount quote is outside the accepted domain")
    return bill_price ** (-days / 91.0) - 1.0


def calculate(
    market_weighting: str = "vw",
    risk_free: str = "canonical",
    paycheck_column: str = "seasonally_adjusted_nominal",
    market_timing: str = "quarter_end",
    base_index: int = 0,
) -> list[float]:
    market = read_csv(SENSITIVITY / "jkp-market-weightings.csv")
    yields = {
        row["observation_date"][:7]: float(row["TB3MS"])
        for row in read_csv(SOURCES / "fred-tb3ms.csv")
    }
    paychecks = read_csv(SENSITIVITY / "bls-paycheck-definitions.csv")

    wealth = 1.0
    monthly_wealth: list[float] = []
    for row in market:
        year, month, _ = map(int, row["date"].split("-"))
        rf = treasury_return(year, month, yields[row["date"][:7]], risk_free)
        total_return = float(row[market_weighting]) + rf
        if total_return <= -1.0:
            raise ValueError("monthly market return must be greater than -1")
        wealth *= 1.0 + total_return
        monthly_wealth.append(wealth)

    quarter_market: list[float] = []
    for start in range(0, 9, 3):
        values = monthly_wealth[start : start + 3]
        selected = values[-1] if market_timing == "quarter_end" else sum(values) / 3.0
        quarter_market.append(selected)

    paycheck_values = [float(row[paycheck_column]) for row in paychecks]
    result: list[float] = []
    for market_value, paycheck_value in zip(quarter_market, paycheck_values, strict=True):
        market_component = 100.0 * market_value / quarter_market[base_index]
        paycheck_component = 100.0 * paycheck_value / paycheck_values[base_index]
        result.append(100.0 * market_component / paycheck_component)
    return result


def sensitivity_csv() -> str:
    variants = [
        ("canonical", {}, "keep"),
        ("simple_yield_divided_by_12", {"risk_free": "simple"}, "reject"),
        ("zero_risk_free", {"risk_free": "zero"}, "reject"),
        ("equal_weight_market", {"market_weighting": "ew"}, "reject"),
        ("capped_value_weight_market", {"market_weighting": "vw_cap"}, "reject"),
        (
            "not_seasonally_adjusted_paycheck",
            {"paycheck_column": "not_seasonally_adjusted_nominal"},
            "reject",
        ),
        (
            "real_paycheck_without_deflated_market",
            {"paycheck_column": "seasonally_adjusted_real"},
            "reject",
        ),
        ("quarterly_average_market", {"market_timing": "average"}, "reject"),
    ]
    canonical = calculate()
    fieldnames = [
        "alternative",
        "ppg_1980_q2",
        "ppg_1980_q3",
        "q3_difference_from_canonical",
        "q2_to_q3_change_percent",
        "decision",
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for name, arguments, decision in variants:
        values = calculate(**arguments)
        writer.writerow(
            {
                "alternative": name,
                "ppg_1980_q2": f"{values[1]:.6f}",
                "ppg_1980_q3": f"{values[2]:.6f}",
                "q3_difference_from_canonical": f"{values[2] - canonical[2]:.6f}",
                "q2_to_q3_change_percent": f"{100.0 * (values[2] / values[1] - 1.0):.6f}",
                "decision": decision,
            }
        )
    return output.getvalue()


def test_rebasing_and_inflation() -> None:
    base_q1 = calculate(base_index=0)
    base_q2 = calculate(base_index=1)
    q2_q3_a = base_q1[2] / base_q1[1]
    q2_q3_b = base_q2[2] / base_q2[1]
    assert abs(q2_q3_a - q2_q3_b) <= 1e-15
    assert f"{base_q2[0]:.6f}" == "87.521232"
    assert f"{base_q2[1]:.6f}" == "100.000000"
    assert f"{base_q2[2]:.6f}" == "109.268026"

    market = [80.0, 100.0, 130.0]
    paycheck = [200.0, 250.0, 275.0]
    deflator = [90.0, 110.0, 125.0]
    nominal = (market[2] / market[0]) / (paycheck[2] / paycheck[0])
    real = ((market[2] / deflator[2]) / (market[0] / deflator[0])) / (
        (paycheck[2] / deflator[2]) / (paycheck[0] / deflator[0])
    )
    assert abs(nominal - real) <= 1e-15


def test_revision_evidence() -> None:
    rows = read_csv(SENSITIVITY / "bls-revision-2025q1.csv")
    for row in rows:
        old = float(row["archived_2025_q1_release"])
        new = float(row["current_2026_q2_vintage"])
        assert float(row["dollar_revision"]) == new - old
        expected_effect = 100.0 * (old / new - 1.0)
        assert abs(float(row["ppg_effect_percent_if_base_unchanged"]) - expected_effect) < 5e-7

    market_rows = read_csv(SENSITIVITY / "jkp-revision-1980.csv")
    assert len(market_rows) == 9
    assert all(row["archived_vintage"] != row["current_vintage"] for row in market_rows)


def validate_periods(rows: list[tuple[str, float]], expected: list[str]) -> str:
    labels = [label for label, _ in rows]
    if len(labels) != len(set(labels)):
        raise ValueError("duplicate period")
    for _, value in rows:
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError("nonfinite or nonpositive value")
    missing = set(expected) - set(labels)
    if not missing:
        return "ok"
    if missing == {expected[-1]}:
        return "warn_stale"
    raise ValueError("missing historical period")


def validate_schema(fields: set[str], required: set[str]) -> str:
    if not required <= fields:
        raise ValueError("missing required field")
    return "warn_ignore_extra" if fields - required else "ok"


def expect_failure(callback) -> None:
    try:
        callback()
    except ValueError:
        return
    raise AssertionError("case should have failed")


def test_edge_policies() -> None:
    expected = ["1980-Q1", "1980-Q2", "1980-Q3"]
    valid = [("1980-Q1", 1.0), ("1980-Q2", 2.0), ("1980-Q3", 3.0)]
    assert validate_periods(valid, expected) == "ok"
    assert validate_periods(valid[:-1], expected) == "warn_stale"
    expect_failure(lambda: validate_periods([valid[0], valid[2]], expected))
    expect_failure(lambda: validate_periods([valid[0], valid[0]], expected))
    expect_failure(lambda: validate_periods([(expected[0], 0.0)], [expected[0]]))
    expect_failure(lambda: validate_periods([(expected[0], math.nan)], [expected[0]]))
    assert validate_schema({"date", "ret"}, {"date", "ret"}) == "ok"
    assert validate_schema({"date", "ret", "new"}, {"date", "ret"}) == "warn_ignore_extra"
    expect_failure(lambda: validate_schema({"date"}, {"date", "ret"}))
    expect_failure(lambda: treasury_return(1980, 1, -1.0, "canonical"))


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "ppg-index-methodology/0.1"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def market_archive(url: str, expected_hash: str) -> dict[str, float]:
    archive = fetch(url)
    if hashlib.sha256(archive).hexdigest() != expected_hash:
        raise ValueError(f"unreviewed JKP revision at {url}")
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        names = [name for name in bundle.namelist() if name.endswith(".csv")]
        if len(names) != 1:
            raise ValueError("JKP archive must contain exactly one CSV")
        rows = csv.DictReader(io.StringIO(bundle.read(names[0]).decode("utf-8-sig")))
        return {row["date"]: float(row["ret"]) for row in rows}


def online_revision_check() -> None:
    legacy = market_archive(JKP_LEGACY_URL, JKP_LEGACY_HASH)
    current = market_archive(JKP_CURRENT_URL, JKP_CURRENT_HASH)
    overlap = sorted(set(legacy) & set(current))
    differences = [current[date] - legacy[date] for date in overlap]
    absolute = sorted(abs(value) for value in differences)
    worst = max(overlap, key=lambda date: abs(current[date] - legacy[date]))
    percentile_95 = absolute[round((len(absolute) - 1) * 0.95)]
    assert overlap[0] == "1926-01-31" and overlap[-1] == "2023-12-31"
    assert len(overlap) == 1176 and all(value != 0.0 for value in differences)
    assert abs(statistics.mean(absolute) - 0.00012331690169601326) < 1e-15
    assert abs(statistics.median(absolute) - 0.00005405547945136133) < 1e-15
    assert abs(percentile_95 - 0.0004497492168461306) < 1e-15
    assert worst == "1933-03-31"
    assert abs(absolute[-1] - 0.0026240090280681555) < 1e-15

    fred = csv.DictReader(
        io.StringIO(
            fetch("https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS").decode("utf-8-sig")
        )
    )
    yields = {
        row["observation_date"][:7]: float(row["TB3MS"])
        for row in fred
        if row["TB3MS"] not in {"", "."}
    }

    def component(source: dict[str, float]) -> float:
        wealth = 1.0
        base = None
        for date in sorted(value for value in source if "1980-01-01" <= value <= "2023-12-31"):
            year, month, _ = map(int, date.split("-"))
            rf = treasury_return(year, month, yields[date[:7]], "canonical")
            wealth *= 1.0 + source[date] + rf
            if date == "1980-03-31":
                base = wealth
        if base is None:
            raise ValueError("market revision source is missing the base quarter")
        return 100.0 * wealth / base

    legacy_component = component(legacy)
    current_component = component(current)
    assert abs(legacy_component - 13824.292525389112) < 1e-9
    assert abs(current_component - 14132.56321637093) < 1e-9
    drift = 100.0 * (current_component / legacy_component - 1.0)
    assert abs(drift - 2.2299201960293003) < 1e-12
    print("ok  online JKP vintage comparison reproduces 1,176 months and 2.229920% drift")


def main() -> int:
    try:
        actual = sensitivity_csv()
        expected = (SENSITIVITY / "expected-results.csv").read_text(encoding="utf-8")
        if actual != expected:
            raise ValueError("sensitivity results differ from the reviewed fixture")
        test_rebasing_and_inflation()
        test_revision_evidence()
        test_edge_policies()
        if "--online-revisions" in sys.argv[1:]:
            online_revision_check()
    except Exception as error:
        print(f"methodology validation failed: {error}", file=sys.stderr)
        return 1
    print("ok  8 sensitivity variants reproduce the reviewed table")
    print("ok  rebasing and common-deflator invariants hold")
    print("ok  revision evidence and 10 edge-policy assertions pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
