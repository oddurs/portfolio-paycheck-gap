.PHONY: check methodology-check roadmap source-check

check:
	cairn check
	cairn render --check
	python3 scripts/run_reference_notebook.py
	python3 scripts/run_methodology_tests.py
	python3 scripts/check_methodology_docs.py
	git diff --check
	git diff --cached --check

roadmap:
	cairn render

source-check:
	python3 scripts/verify_source_samples.py
	python3 scripts/run_methodology_tests.py --online-revisions

methodology-check:
	python3 scripts/run_reference_notebook.py
	python3 scripts/run_methodology_tests.py
	python3 scripts/check_methodology_docs.py
