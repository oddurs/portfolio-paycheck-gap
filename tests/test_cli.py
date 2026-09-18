from __future__ import annotations

import subprocess
import sys

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


@pytest.mark.parametrize("command", ["fetch", "build", "check", "update"])
def test_scaffolded_commands_fail_explicitly(
    command: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([command]) == 2
    assert "implementation is pending" in capsys.readouterr().err
