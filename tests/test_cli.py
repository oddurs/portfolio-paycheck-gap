from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from ppg_index import __version__
from ppg_index.cli import main


def test_version_is_installed_package_version() -> None:
    assert __version__ == "0.2.0.dev0"


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


@pytest.mark.parametrize("command", ["build", "check", "update"])
def test_scaffolded_commands_fail_explicitly(
    command: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([command]) == 2
    assert "implementation is pending" in capsys.readouterr().err


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
