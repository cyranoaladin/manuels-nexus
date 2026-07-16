.PHONY: setup referentiel harvest verify ruff similarity coverage accents chapter test gates-corpus gates-corpus-strict lot-gates

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
	$(PY) scripts/gates_corpus/check_accents_contenu.py
	@echo "accents OK"

chapter:
	$(PY) scripts/assemble.py --chap $(CHAP) --variant complet

gates-corpus:
	$(PY) scripts/gates_corpus/check_eleve_no_corrige.py
	$(PY) scripts/gates_corpus/check_ascii_code.py
	$(PY) scripts/gates_corpus/check_td_corrige_alignment.py --chap $(CHAP)
	$(PY) scripts/gates_corpus/check_no_placeholders.py
	$(PY) scripts/gates_corpus/check_differentiation_quality.py --chap $(CHAP)
	$(PY) scripts/gates_corpus/check_qcm_schema.py --chap $(CHAP)
	$(PY) scripts/gates_corpus/check_sql_query_result_consistency.py
	$(PY) scripts/gates_corpus/check_boyer_moore_trace_consistency.py

lot-gates:
	@echo "=== make verify ==="
	$(PY) scripts/verify_python.py --chap $(CHAP)
	@echo "=== make accents ==="
	@! grep -rnE '\\\\(textsc|title=)\{[^}]*(Definition|Theoreme|Propriete|Methode|Bareme|Evaluation|Corrige de|frequente|estimes|Reussite)' gabarits chapitres --include='*.tex' --include='*.cls' \
	  || (echo 'FAIL R10 : libellés sans accents détectés' && exit 1)
	$(PY) scripts/gates_corpus/check_accents_contenu.py
	$(PY) scripts/gates_corpus/check_ascii_code.py
	@echo "accents OK"
	@echo "=== gates-corpus-strict ==="
	$(PY) scripts/gates_corpus/check_eleve_no_corrige.py
	$(PY) scripts/gates_corpus/check_td_corrige_alignment.py --chap $(CHAP) --strict
	$(PY) scripts/gates_corpus/check_no_placeholders.py
	$(PY) scripts/gates_corpus/check_differentiation_quality.py --chap $(CHAP)
	$(PY) scripts/gates_corpus/check_qcm_schema.py --chap $(CHAP) --strict
	$(PY) scripts/gates_corpus/check_sql_query_result_consistency.py
	$(PY) scripts/gates_corpus/check_boyer_moore_trace_consistency.py
	$(PY) scripts/gates_corpus/check_console_trace.py --chap $(CHAP)
	@echo "=== ALL LOT GATES PASSED ==="

gates-corpus-strict:
	$(PY) scripts/gates_corpus/check_eleve_no_corrige.py
	$(PY) scripts/gates_corpus/check_ascii_code.py
	$(PY) scripts/gates_corpus/check_td_corrige_alignment.py --chap $(CHAP) --strict
	$(PY) scripts/gates_corpus/check_no_placeholders.py
	$(PY) scripts/gates_corpus/check_differentiation_quality.py --chap $(CHAP)
	$(PY) scripts/gates_corpus/check_qcm_schema.py --chap $(CHAP) --strict
	$(PY) scripts/gates_corpus/check_sql_query_result_consistency.py
	$(PY) scripts/gates_corpus/check_boyer_moore_trace_consistency.py

test:
	$(PY) -m pytest tests/ -q
