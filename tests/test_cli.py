from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from ppg_index import __version__
from ppg_index.cli import main


def test_version_is_installed_package_version() -> None:
    assert __version__ == "0.2.0"


@pytest.mark.parametrize("command", ["fetch", "build", "check", "update"])
def test_each_command_has_help(command: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ppg_index", command, "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout


def test_fetch_reports_created_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    snapshot = tmp_path / "snapshots" / "abc"

    def fake_acquire(*args: object, **kwargs: object) -> Path:
        return snapshot

    monkeypatch.setattr("ppg_index.sources.acquire_snapshot", fake_acquire)
    assert main(["fetch", "--cache-dir", str(tmp_path), "--end-year", "2026"]) == 0
    assert capsys.readouterr().out.strip() == str(snapshot)


def test_update_builds_a_reviewable_local_candidate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    snapshot = tmp_path / "cache/snapshots/abc"
    summary = SimpleNamespace(latest_quarter="2025-Q3", snapshot_id="abc")
    publication = SimpleNamespace(artifacts=object())
    monkeypatch.setattr("ppg_index.sources.acquire_snapshot", lambda *args, **kwargs: snapshot)
    monkeypatch.setattr("ppg_index.publication.build_artifacts", lambda path: publication)
    monkeypatch.setattr(
        "ppg_index.publication.publish_artifacts",
        lambda path, artifacts: summary,
    )
    assert main(["update", "--cache-dir", str(tmp_path / "cache")]) == 0
    output = capsys.readouterr().out
    assert "review before publication" in output
    assert "2025-Q3" in output
