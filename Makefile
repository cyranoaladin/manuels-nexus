.PHONY: setup referentiel harvest verify ruff similarity coverage accents chapter test

PY := .venv/bin/python
CHAP ?= 1NSI-TYPES-CONSTRUITS

setup:
	python3 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt
	@which pdflatex >/dev/null || echo "ATTENTION : pdflatex manquant (texlive-full)"
	@which pandoc   >/dev/null || echo "ATTENTION : pandoc manquant (apt install pandoc)"
	@test -d corpus_nsi/.git -o -f corpus_nsi/README.md || echo "ATTENTION : submodule corpus_nsi non initialisé"

referentiel:
	$(PY) scripts/convert_programme_yaml.py

harvest:
	$(PY) scripts/harvest_nsi.py --chap $(CHAP)

verify:
	$(PY) scripts/verify_python.py --chap $(CHAP)

ruff:
	$(PY) scripts/verify_python.py --chap $(CHAP)   # ruff intégré ; cible dédiée pour lisibilité CI

similarity:
	$(PY) scripts/similarity_check.py --chap $(CHAP)

coverage:
	$(PY) scripts/coverage_report.py --chap $(CHAP)

accents:
	@! grep -rnE '\\\\(textsc|title=)\{[^}]*(Definition|Theoreme|Propriete|Methode|Bareme|Evaluation|Corrige de|frequente|estimes|Reussite)' gabarits chapitres --include='*.tex' --include='*.cls' \
	  || (echo 'FAIL R10 : libellés sans accents détectés' && exit 1)
	@echo "accents OK"

chapter:
	$(PY) scripts/assemble.py --chap $(CHAP) --variant complet

test:
	$(PY) -m pytest tests/ -q
