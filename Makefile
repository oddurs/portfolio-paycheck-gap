.PHONY: check format lint methodology-check package roadmap setup source-check test

UV := uv

setup:
	$(UV) sync --locked --all-groups

format:
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

lint:
	$(UV) run ruff check .
	$(UV) run ruff format --check .

test:
	$(UV) run pytest

package:
	$(UV) build

check:
	cairn check
	cairn render --check
	$(UV) run ruff check .
	$(UV) run ruff format --check .
	$(UV) run pytest
	$(UV) run python scripts/run_reference_notebook.py
	$(UV) run python scripts/run_methodology_tests.py
	$(UV) run python scripts/check_methodology_docs.py
	git diff --check
	git diff --cached --check

roadmap:
	cairn render

source-check:
	$(UV) run python scripts/verify_source_samples.py
	$(UV) run python scripts/run_methodology_tests.py --online-revisions

methodology-check:
	$(UV) run python scripts/run_reference_notebook.py
	$(UV) run python scripts/run_methodology_tests.py
	$(UV) run python scripts/check_methodology_docs.py
