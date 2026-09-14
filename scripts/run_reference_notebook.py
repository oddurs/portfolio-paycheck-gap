#!/usr/bin/env python3
"""Execute the reference notebook using only the Python standard library."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "ppg_reference.ipynb"


def main() -> int:
    document = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    if document.get("nbformat") != 4:
        print("reference notebook must use nbformat 4", file=sys.stderr)
        return 1

    namespace: dict[str, object] = {
        "__name__": "__ppg_reference_notebook__",
        "PROJECT_ROOT": ROOT,
    }
    code_cells = 0
    try:
        for index, cell in enumerate(document.get("cells", []), start=1):
            if cell.get("cell_type") != "code":
                continue
            code_cells += 1
            source = "".join(cell.get("source", []))
            exec(compile(source, f"{NOTEBOOK.name}:cell-{index}", "exec"), namespace)
    except Exception as error:
        print(f"reference notebook failed: {error}", file=sys.stderr)
        return 1

    monthly = namespace.get("monthly_rows")
    quarterly = namespace.get("quarterly_rows")
    if not isinstance(monthly, list) or len(monthly) != 9:
        print("reference notebook did not retain nine monthly rows", file=sys.stderr)
        return 1
    if not isinstance(quarterly, list) or len(quarterly) != 3:
        print("reference notebook did not retain three quarterly rows", file=sys.stderr)
        return 1
    print(f"ok  executed {code_cells} code cells with standard-library Python")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
