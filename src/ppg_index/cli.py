"""Command-line interface for acquiring, building, and checking PPG."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from ppg_index import __version__

Command = Callable[[argparse.Namespace], int]


def _pending(command: str) -> Command:
    def run(_: argparse.Namespace) -> int:
        print(
            f"ppg {command}: command surface is ready; implementation is pending in v0.2",
            file=sys.stderr,
        )
        return 2

    return run


def _path(value: str) -> Path:
    return Path(value).expanduser()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ppg",
        description="Build and validate the Portfolio-Paycheck Gap Index.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("fetch", help="Retrieve and cache canonical source snapshots.")
    fetch.add_argument("--cache-dir", type=_path, default=Path("data/cache"))
    fetch.set_defaults(handler=_pending("fetch"))

    build = commands.add_parser("build", help="Build index artifacts from cached snapshots.")
    build.add_argument("--snapshot-dir", type=_path, default=Path("data/cache/current"))
    build.add_argument("--output-dir", type=_path, default=Path("public/data"))
    build.set_defaults(handler=_pending("build"))

    check = commands.add_parser("check", help="Validate snapshots, calculations, and artifacts.")
    check.add_argument("--snapshot-dir", type=_path, default=Path("data/cache/current"))
    check.add_argument("--artifact-dir", type=_path, default=Path("public/data"))
    check.set_defaults(handler=_pending("check"))

    update = commands.add_parser(
        "update", help="Fetch, build, and check without publishing automatically."
    )
    update.add_argument("--cache-dir", type=_path, default=Path("data/cache"))
    update.add_argument("--output-dir", type=_path, default=Path("public/data"))
    update.set_defaults(handler=_pending("update"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)
