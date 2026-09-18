from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_NETWORK_MODULES = {"http", "requests", "urllib"}


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def test_network_imports_are_absent_from_pure_modules() -> None:
    package = Path(__file__).parents[1] / "src" / "ppg_index"
    for filename in ("calculation.py", "rendering.py", "validation.py"):
        assert imported_roots(package / filename).isdisjoint(FORBIDDEN_NETWORK_MODULES)
