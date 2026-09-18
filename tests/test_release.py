from __future__ import annotations

import hashlib
from pathlib import Path

from ppg_index import __version__
from ppg_index.rendering import METHODOLOGY_VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_release_versions_are_frozen() -> None:
    assert __version__ == "0.2.0"
    assert METHODOLOGY_VERSION == "0.1"
    notes = (ROOT / "releases/v0.2.0.md").read_text()
    assert "1979 Q1 through 2025 Q3" in notes
    assert "stale" in notes
    assert "CC BY-NC 4.0" in notes


def test_release_artifact_checksums() -> None:
    files = {
        "ppg.csv": ROOT / "public/data/ppg.csv",
        "latest.json": ROOT / "public/data/latest.json",
        "ppg.svg": ROOT / "public/data/ppg.svg",
        "provenance.json": ROOT / "public/data/provenance.json",
        "v0.1.md": ROOT / "methodology/v0.1.md",
        "manifest.json": ROOT / "data/snapshots/4156e87c2524a9ce/manifest.json",
    }
    lines = (ROOT / "releases/v0.2.0-SHA256SUMS").read_text().splitlines()
    declared = dict(line.split("  ", 1)[::-1] for line in lines)
    assert set(declared) == set(files)
    for name, path in files.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == declared[name]
