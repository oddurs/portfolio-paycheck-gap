"""Offline orchestration and guarded publication of canonical artifacts."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .calculation import CalculationResult, calculate_ppg, parse_normalized_inputs
from .rendering import ArtifactSet, render_artifacts
from .sources import SnapshotError, resolve_current, verify_snapshot
from .validation import ArtifactSummary, PPGError, validate_artifact_directory, validate_artifacts

ARTIFACT_NAMES = {"ppg.csv", "latest.json", "ppg.svg", "provenance.json"}


@dataclass(frozen=True, slots=True)
class PublicationResult:
    calculation: CalculationResult
    artifacts: ArtifactSet
    summary: ArtifactSummary


def resolve_snapshot(path: Path) -> Path:
    """Accept either a snapshot directory or a cache root with current.json."""

    if (path / "manifest.json").is_file():
        return path
    current = resolve_current(path)
    if current is None:
        raise SnapshotError(f"no snapshot manifest or current.json beneath {path}")
    return current


def _pinned_generated_at(cache_root: Path) -> str | None:
    pointer = cache_root / "current.json"
    if not pointer.is_file():
        return None
    try:
        value = json.loads(pointer.read_bytes()).get("artifact_generated_at")
    except (OSError, json.JSONDecodeError, AttributeError) as error:
        raise PPGError("current snapshot pointer is malformed") from error
    if value is not None and not isinstance(value, str):
        raise PPGError("artifact_generated_at must be an ISO 8601 string")
    return value


def build_artifacts(
    snapshot_path: Path,
    *,
    generated_at: str | None = None,
) -> PublicationResult:
    """Build every artifact offline from a checksum-verified snapshot."""

    pinned = (
        None if (snapshot_path / "manifest.json").is_file() else _pinned_generated_at(snapshot_path)
    )
    generated_at = generated_at or pinned or datetime.now(UTC).replace(microsecond=0).isoformat()
    snapshot = resolve_snapshot(snapshot_path)
    manifest = verify_snapshot(snapshot)
    normalized = snapshot / "normalized"
    try:
        inputs = parse_normalized_inputs(
            (normalized / "market.csv").read_bytes(),
            (normalized / "treasury.csv").read_bytes(),
            (normalized / "paycheck.csv").read_bytes(),
        )
    except OSError as error:
        raise PPGError(f"cannot read normalized inputs from {snapshot}") from error
    calculation = calculate_ppg(*inputs)
    artifacts = render_artifacts(calculation, manifest, generated_at)
    summary = validate_artifacts(artifacts)
    return PublicationResult(calculation, artifacts, summary)


def _quarter_ordinal(quarter: str) -> int:
    try:
        year = int(quarter[:4])
        number = int(quarter[-1])
    except (TypeError, ValueError) as error:
        raise PPGError(f"invalid artifact quarter: {quarter!r}") from error
    if len(quarter) != 7 or quarter[4:6] != "-Q" or number not in {1, 2, 3, 4}:
        raise PPGError(f"invalid artifact quarter: {quarter!r}")
    return year * 4 + number - 1


def _existing_period(output_dir: Path) -> str | None:
    latest = output_dir / "latest.json"
    if not latest.exists():
        return None
    try:
        value = json.loads(latest.read_bytes())["observation_period"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise PPGError("existing latest.json is malformed; refusing to overwrite") from error
    if not isinstance(value, str):
        raise PPGError("existing latest.json has no observation period")
    return value


def publish_artifacts(output_dir: Path, artifacts: ArtifactSet) -> ArtifactSummary:
    """Validate and atomically replace a complete artifact directory."""

    summary = validate_artifacts(artifacts)
    if output_dir.exists() and not output_dir.is_dir():
        raise PPGError(f"artifact output is not a directory: {output_dir}")
    if output_dir.exists():
        unexpected = {item.name for item in output_dir.iterdir()} - ARTIFACT_NAMES
        if unexpected:
            raise PPGError(
                f"artifact directory contains unexpected files: {', '.join(sorted(unexpected))}"
            )
    previous_period = _existing_period(output_dir)
    if previous_period is not None and _quarter_ordinal(summary.latest_quarter) < _quarter_ordinal(
        previous_period
    ):
        raise PPGError(
            f"refusing to replace {previous_period} artifacts with stale "
            f"{summary.latest_quarter} input"
        )

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}-", dir=output_dir.parent))
    backup = output_dir.with_name(f".{output_dir.name}.previous")
    try:
        for name, data in artifacts.files().items():
            (staging / name).write_bytes(data)
        validate_artifact_directory(staging)
        if backup.exists():
            raise PPGError(f"publication backup already exists: {backup}")
        if output_dir.exists():
            os.replace(output_dir, backup)
        try:
            os.replace(staging, output_dir)
        except BaseException:
            if backup.exists() and not output_dir.exists():
                os.replace(backup, output_dir)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return validate_artifact_directory(output_dir)
