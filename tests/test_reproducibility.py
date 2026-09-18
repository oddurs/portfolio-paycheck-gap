from __future__ import annotations

import socket
from dataclasses import replace
from pathlib import Path

import pytest

from ppg_index.calculation import calculate_ppg
from scripts.update_golden import build_golden
from tests.test_calculation import canonical_inputs

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests/fixtures/golden/ppg-calculation.csv"


def test_raw_snapshot_to_full_history_matches_golden_with_network_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("offline reproduction attempted network access")

    monkeypatch.setattr(socket, "socket", reject_network)
    assert build_golden() == GOLDEN.read_bytes()


def test_wrong_quarter_join_is_detected_by_reference_values() -> None:
    market, treasury, paycheck = canonical_inputs()
    shifted = [
        replace(item, value=paycheck[index - 1].value)
        if index and item.value is not None and item.quarter <= "2025-Q3"
        else item
        for index, item in enumerate(paycheck)
    ]
    canonical = calculate_ppg(market, treasury, paycheck)
    wrong = calculate_ppg(market, treasury, shifted)
    canonical_q2 = next(item for item in canonical.observations if item.quarter == "1980-Q2")
    wrong_q2 = next(item for item in wrong.observations if item.quarter == "1980-Q2")
    assert f"{canonical_q2.ppg:.6f}" == "114.257990"
    assert f"{wrong_q2.ppg:.6f}" != "114.257990"


def test_omitting_return_distributions_changes_reviewed_result() -> None:
    market, treasury, paycheck = canonical_inputs()
    without_distributions = [
        replace(item, excess_return=item.excess_return - 0.002)
        if "1980-01" <= item.month <= "1980-09"
        else item
        for item in market
    ]
    canonical = calculate_ppg(market, treasury, paycheck)
    wrong = calculate_ppg(without_distributions, treasury, paycheck)
    canonical_q3 = next(item for item in canonical.observations if item.quarter == "1980-Q3")
    wrong_q3 = next(item for item in wrong.observations if item.quarter == "1980-Q3")
    assert f"{canonical_q3.ppg:.6f}" == "124.847450"
    assert abs(canonical_q3.ppg - wrong_q3.ppg) > 1


def test_rebase_and_ratio_identities_hold_exhaustively() -> None:
    result = calculate_ppg(*canonical_inputs())
    ratios = [item.market_value / item.paycheck_value for item in result.observations]
    base_index = next(
        index for index, item in enumerate(result.observations) if item.quarter == "1980-Q1"
    )
    for index, item in enumerate(result.observations):
        assert item.ppg == pytest.approx(100 * ratios[index] / ratios[base_index])

    for alternate_base in range(len(result.observations)):
        rebased = [100 * ratio / ratios[alternate_base] for ratio in ratios]
        assert rebased[alternate_base] == pytest.approx(100)
        for index in range(1, len(rebased)):
            assert rebased[index] / rebased[index - 1] == pytest.approx(
                ratios[index] / ratios[index - 1]
            )
