"""Command-line interface for acquiring, building, and checking PPG."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from ppg_index import __version__


def _path(value: str) -> Path:
    return Path(value).expanduser()


def _current_year() -> int:
    return datetime.now(UTC).year


def _fetch(args: argparse.Namespace) -> int:
    from ppg_index.sources import SnapshotError, SourceValidationError, acquire_snapshot

    try:
        snapshot = acquire_snapshot(
            args.cache_dir,
            end_year=args.end_year,
            retrieved_at=args.retrieved_at,
            accept_revision=args.accept_revision,
        )
    except (OSError, SnapshotError, SourceValidationError) as error:
        print(f"ppg fetch failed: {error}", file=sys.stderr)
        return 1
    print(snapshot)
    return 0


def _build(args: argparse.Namespace) -> int:
    from ppg_index.publication import build_artifacts, publish_artifacts
    from ppg_index.validation import PPGError

    try:
        publication = build_artifacts(args.snapshot_dir)
        summary = publish_artifacts(args.output_dir, publication.artifacts)
    except (OSError, ValueError, PPGError) as error:
        print(f"ppg build failed: {error}", file=sys.stderr)
        return 1
    print(
        f"built {summary.rows} quarters through {summary.latest_quarter} "
        f"from snapshot {summary.snapshot_id}"
    )
    return 0


def _check(args: argparse.Namespace) -> int:
    from ppg_index.publication import build_artifacts
    from ppg_index.validation import PPGError, validate_artifact_directory

    try:
        expected = build_artifacts(args.snapshot_dir)
        actual = validate_artifact_directory(args.artifact_dir)
        for name, data in expected.artifacts.files().items():
            if (args.artifact_dir / name).read_bytes() != data:
                raise PPGError(f"artifact differs from reproducible build: {name}")
        if actual != expected.summary:
            raise PPGError("artifact summary differs from reproducible build")
    except (OSError, ValueError, PPGError) as error:
        print(f"ppg check failed: {error}", file=sys.stderr)
        return 1
    print(
        f"ok: {actual.rows} quarters through {actual.latest_quarter}; all canonical artifacts agree"
    )
    return 0


def _update(args: argparse.Namespace) -> int:
    from ppg_index.publication import build_artifacts, publish_artifacts
    from ppg_index.sources import acquire_snapshot
    from ppg_index.validation import PPGError

    try:
        snapshot = acquire_snapshot(
            args.cache_dir,
            end_year=args.end_year,
            retrieved_at=args.retrieved_at,
            accept_revision=args.accept_revision,
        )
        publication = build_artifacts(snapshot)
        summary = publish_artifacts(args.output_dir, publication.artifacts)
    except (OSError, ValueError, PPGError) as error:
        print(f"ppg update failed: {error}", file=sys.stderr)
        return 1
    print(
        f"updated local candidate through {summary.latest_quarter} from "
        f"snapshot {summary.snapshot_id}; review before publication"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ppg",
        description="Build and validate the Portfolio-Paycheck Gap Index.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("fetch", help="Retrieve and cache canonical source snapshots.")
    fetch.add_argument("--cache-dir", type=_path, default=Path("data/cache"))
    fetch.add_argument("--end-year", type=int, default=_current_year())
    fetch.add_argument(
        "--retrieved-at",
        help="Override retrieval timestamp with a timezone-aware ISO 8601 value.",
    )
    fetch.add_argument(
        "--accept-revision",
        action="store_true",
        help="Accept changed values in periods shared with the current snapshot.",
    )
    fetch.set_defaults(handler=_fetch)

    build = commands.add_parser("build", help="Build index artifacts from cached snapshots.")
    build.add_argument("--snapshot-dir", type=_path, default=Path("data"))
    build.add_argument("--output-dir", type=_path, default=Path("public/data"))
    build.set_defaults(handler=_build)

    check = commands.add_parser("check", help="Validate snapshots, calculations, and artifacts.")
    check.add_argument("--snapshot-dir", type=_path, default=Path("data"))
    check.add_argument("--artifact-dir", type=_path, default=Path("public/data"))
    check.set_defaults(handler=_check)

    update = commands.add_parser(
        "update", help="Fetch, build, and check without publishing automatically."
    )
    update.add_argument("--cache-dir", type=_path, default=Path("data/cache"))
    update.add_argument("--output-dir", type=_path, default=Path("build/update"))
    update.add_argument("--end-year", type=int, default=_current_year())
    update.add_argument("--retrieved-at")
    update.add_argument("--accept-revision", action="store_true")
    update.set_defaults(handler=_update)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)
