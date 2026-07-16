.PHONY: setup db crawl ingest index verify similarity coverage chapter check-latex specimen test

PY := .venv/bin/python
CHAP ?= 1SPE-SUITES
SRC ?=

setup:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt
	@which lualatex >/dev/null || echo "ATTENTION : lualatex introuvable (installer texlive-full)"
	@echo "Puis : cp .env.example .env && make db"

db:
	psql "$$DATABASE_URL" -f db/schema.sql
	$(PY) scripts/load_referentiel.py

crawl:
	$(PY) scripts/crawl.py $(if $(SRC),--src $(SRC))

ingest:
	$(PY) scripts/ingest.py

index:
	$(PY) scripts/index.py

verify:
	$(PY) scripts/verify_sympy.py --chap $(CHAP)

similarity:
	$(PY) scripts/similarity_check.py --chap $(CHAP)

coverage:
	$(PY) scripts/coverage_report.py --chap $(CHAP)

check-latex:
	$(PY) scripts/check_latex.py

chapter:
	$(PY) scripts/assemble.py --chap $(CHAP) --variant complet

specimen:
	mkdir -p build/specimen
	TEXINPUTS=gabarits: lualatex -interaction=nonstopmode -halt-on-error -output-directory=build/specimen gabarits/specimen.tex
	PYTHONPATH=scripts $(PY) -c "from pathlib import Path; from pdf_integrity import verify_pdf; raise SystemExit(verify_pdf(Path('build/specimen/specimen.pdf'), Path('build/specimen/specimen.log')))"

test:
	$(PY) -m pytest tests/ -q
