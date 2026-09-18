.PHONY: artifacts check format golden-update lint methodology-check package roadmap setup source-check test

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

golden-update:
	$(UV) run python scripts/update_golden.py --accept

package:
	$(UV) build

artifacts:
	$(UV) run ppg build --snapshot-dir data --output-dir public/data

check:
	cairn check
	cairn render --check
	$(UV) run ruff check .
	$(UV) run ruff format --check .
	$(UV) run pytest
	$(UV) run ppg check --snapshot-dir data --artifact-dir public/data
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
