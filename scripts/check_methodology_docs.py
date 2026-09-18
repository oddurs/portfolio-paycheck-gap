#!/usr/bin/env python3
"""Check that the published v0.1 methodology is complete and internally linked."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METHODOLOGY = ROOT / "methodology"
DOCUMENTS = [
    ROOT / "README.md",
    METHODOLOGY / "README.md",
    METHODOLOGY / "v0.1.md",
    METHODOLOGY / "data-dictionary-v0.1.md",
    METHODOLOGY / "CHANGELOG.md",
]

REQUIRED_SECTIONS = {
    "README.md": [
        "## Project status",
        "## Validate",
        "## Data use",
    ],
    "methodology/v0.1.md": [
        "## 1. Purpose",
        "## 2. Scope",
        "## 3. Canonical sources",
        "## 4. Calculation",
        "## 5. Validation and failure behavior",
        "## 6. Publication and provenance",
        "## 7. Rights and required notices",
        "## 8. Independent implementation checklist",
        "## 9. Limitations",
    ],
    "methodology/data-dictionary-v0.1.md": [
        "## Raw JKP market input",
        "## Raw Treasury input",
        "## Raw BLS paycheck input",
        "## Monthly calculation fields",
        "## Quarterly calculation fields",
        "## Public observation row",
        "## Public metadata record",
    ],
    "methodology/CHANGELOG.md": ["## v0.1 — 2026-09-13"],
}

EXPECTED_FIELDS = {
    "location",
    "name",
    "freq",
    "weighting",
    "direction",
    "n_stocks",
    "n_stocks_min",
    "date",
    "ret",
    "observation_date",
    "TB3MS",
    "series_id",
    "year",
    "period",
    "value",
    "footnote",
    "month",
    "excess_return",
    "annual_discount_yield_percent",
    "calendar_days",
    "bill_term_days",
    "bill_price",
    "treasury_return",
    "market_return",
    "market_wealth",
    "quarter",
    "quarter_end",
    "market_value",
    "paycheck_value",
    "market_component",
    "paycheck_component",
    "ppg",
    "methodology_version",
    "generated_at",
    "latest_quarter",
    "stale",
    "market_retrieved_at",
    "market_sha256",
    "treasury_retrieved_at",
    "treasury_sha256",
    "paycheck_retrieved_at",
    "paycheck_sha256",
    "source_notice",
}


def local_links(document: Path, text: str) -> list[Path]:
    targets: list[Path] = []
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text, flags=re.DOTALL):
        target = match.group(1).strip().split("#", 1)[0]
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        targets.append((document.parent / target).resolve())
    return targets


def main() -> int:
    errors: list[str] = []
    contents: dict[str, str] = {}
    for document in DOCUMENTS:
        if not document.is_file():
            errors.append(f"missing document: {document.relative_to(ROOT)}")
            continue
        text = document.read_text(encoding="utf-8")
        key = document.relative_to(ROOT).as_posix()
        contents[key] = text
        for target in local_links(document, text):
            if not target.exists():
                errors.append(
                    f"broken local link in {document.relative_to(ROOT)}: {target.relative_to(ROOT)}"
                )

    for filename, sections in REQUIRED_SECTIONS.items():
        text = contents.get(filename, "")
        for section in sections:
            if section not in text:
                errors.append(f"{filename} lacks required section {section!r}")

    dictionary = contents.get("methodology/data-dictionary-v0.1.md", "")
    missing_fields = sorted(field for field in EXPECTED_FIELDS if f"`{field}`" not in dictionary)
    if missing_fields:
        errors.append(f"data dictionary lacks fields: {', '.join(missing_fields)}")

    for filename, text in contents.items():
        if re.search(r"\b(?:TODO|TBD|FIXME)\b", text, flags=re.IGNORECASE):
            errors.append(f"{filename} contains an unresolved placeholder")

    if errors:
        for error in errors:
            print(f"methodology docs: {error}", file=sys.stderr)
        return 1
    print(f"ok  {len(DOCUMENTS)} published methodology documents and all local links")
    print(f"ok  {len(EXPECTED_FIELDS)} input, intermediate, output, and metadata fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
