.PHONY: setup db crawl ingest index verify similarity coverage chapter check-latex test

PY := .venv/bin/python
CHAP ?= 1SPE-SUITES
SRC ?=

setup:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt
	@which pdflatex >/dev/null || echo "ATTENTION : pdflatex introuvable (installer texlive-full)"
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
	@for f in $$(git diff --name-only --cached -- '*.tex' 2>/dev/null || find chapitres -name '*.tex'); do \
	  echo "compile $$f"; $(PY) -c "import sys;sys.path.insert(0,'scripts')" ; done
	$(PY) scripts/assemble.py --chap $(CHAP) --variant complet || true

chapter:
	$(PY) scripts/assemble.py --chap $(CHAP) --variant complet

test:
	$(PY) -m pytest tests/ -q
