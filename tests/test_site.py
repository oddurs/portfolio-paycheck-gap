"""Contract tests for the generated, dependency-free public site."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INDEX = PUBLIC / "index.html"
STYLESHEET = PUBLIC / "assets" / "site.css"
HTML = INDEX.read_text(encoding="utf-8")
CSS = STYLESHEET.read_text(encoding="utf-8")
LATEST = json.loads((PUBLIC / "data" / "latest.json").read_text(encoding="utf-8"))
with (PUBLIC / "data" / "ppg.csv").open(encoding="utf-8", newline="") as handle:
    LATEST_ROW = list(csv.DictReader(handle))[-1]


class SiteDocument(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.references: list[tuple[str, str]] = []
        self.label_references: list[str] = []
        self.tags: list[str] = []
        self.images: list[dict[str, str | None]] = []
        self.html_language: str | None = None
        self.viewport = False

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        attrs = dict(attributes)
        self.tags.append(tag)
        if identifier := attrs.get("id"):
            self.ids.add(identifier)
        if tag == "html":
            self.html_language = attrs.get("lang")
        if tag == "meta" and attrs.get("name") == "viewport":
            self.viewport = True
        if tag in {"a", "link"} and (href := attrs.get("href")):
            self.references.append((tag, href))
        if tag == "img":
            self.images.append(attrs)
            if source := attrs.get("src"):
                self.references.append((tag, source))
        if labelled_by := attrs.get("aria-labelledby"):
            self.label_references.extend(labelled_by.split())


def parse_site() -> SiteDocument:
    document = SiteDocument()
    document.feed(HTML)
    return document


def test_committed_page_matches_fresh_deterministic_build() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_site.py"), "--check"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_page_headline_and_components_match_canonical_artifacts() -> None:
    expected = (
        LATEST["observation_period"].replace("-", " "),
        f"{LATEST['value']:,.1f}",
        f"{LATEST['changes']['quarter_over_quarter_percent']:+.1f}%",
        f"{LATEST['changes']['year_over_year_percent']:+.1f}%",
        f"{float(LATEST_ROW['market_component']):,.1f}",
        f"{float(LATEST_ROW['paycheck_component']):,.1f}",
        str(LATEST["methodology_version"]),
        str(LATEST["snapshot_id"]),
    )
    for value in expected:
        assert value in HTML

    state = "stale" if LATEST["stale"] else "current"
    assert f'data-state="{state}"' in HTML
    assert f"status-note-{state}" in HTML


def test_page_has_semantic_and_accessible_structure() -> None:
    document = parse_site()

    assert document.html_language == "en"
    assert document.viewport
    assert document.tags.count("main") == 1
    assert document.tags.count("h1") == 1
    assert "nav" in document.tags
    assert "figure" in document.tags
    assert "figcaption" in document.tags
    assert "#main" in {reference for _, reference in document.references}
    assert set(document.label_references) <= document.ids
    assert document.images
    for image in document.images:
        assert image.get("alt")
        assert image.get("width")
        assert image.get("height")


def test_local_links_exist_and_internal_anchors_resolve() -> None:
    document = parse_site()

    for _, reference in document.references:
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc:
            continue
        if parsed.fragment and not parsed.path:
            assert parsed.fragment in document.ids
            continue
        target = (PUBLIC / unquote(parsed.path)).resolve()
        assert target.is_relative_to(PUBLIC.resolve())
        assert target.is_file(), reference
        if parsed.fragment and parsed.path == "index.html":
            assert parsed.fragment in document.ids


def test_frontend_has_no_runtime_or_remote_asset_dependency() -> None:
    document = parse_site()

    assert "script" not in document.tags
    for tag, reference in document.references:
        if tag in {"img", "link"}:
            assert not urlsplit(reference).scheme
    assert "@import" not in CSS
    assert "url(" not in CSS


def test_responsive_focus_reduced_motion_and_print_rules_are_present() -> None:
    assert ":focus-visible" in CSS
    assert "@media (max-width: 52rem)" in CSS
    assert "@media (max-width: 38rem)" in CSS
    assert "@media (prefers-reduced-motion: reduce)" in CSS
    assert "@media print" in CSS
