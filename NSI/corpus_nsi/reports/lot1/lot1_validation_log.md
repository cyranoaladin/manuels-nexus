# Lot 1 validation log

Venv: /tmp/nsi_lot1_venv

## git status -sb

```text
## lot1/substance-gouvernance
 M qa_gate_policy.md
 M reports/lot1/lot1_validation_log.md
 M scripts/check_drive_enrichment_traceability.py
?? nsi-enseignement/
?? scrapping_NSI/audit_reconciliation_report.md
?? scrapping_NSI/dossier_technique_nsi.pdf
?? scrapping_NSI/migration_registry.json
?? scrapping_NSI/ressources_nsi_centralisees/
?? scrapping_NSI/ressources_nsi_extraites/
?? scrapping_NSI/ressources_nsi_extraites_v2/
?? scrapping_NSI/sqlite_data
```
exit=0

## git log -2 --format privacy-safe

```text
commit 4dd97b64ad533b1ebed87b98829cc17015e9c6c2
Author: Alaeddine Ben Rhouma <redacted>
Date: Mon Jun 29 00:12:53 2026 +0100

    Sécuriser le lot 1 substance gouvernance

commit 5a959110a2191cc0937b7818b4b97a43fecb9f06
Author: NSI Corpus QA <redacted>
Date: Sun Jun 28 22:02:54 2026 +0100

    Actualiser les preuves après stabilisation CI

```
exit=0

## test ! -d dist

```text
dist absent
```
exit=0

## python -m pytest -q

```text
........................................................................ [ 32%]
........................................................................ [ 64%]
...................................................................... [ 96%]
........                                                                 [100%]
=============================== warnings summary ===============================
tests/test_archive_portability_modes.py::ArchivePortabilityModesTest::test_source_clean_mode_does_not_require_git_bundle
  /usr/lib/python3.12/tarfile.py:2274: DeprecationWarning: Python 3.14 will, by default, filter extracted tar archives and reject files or modify their metadata. Use the filter argument to control this behavior.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
222 passed, 1 warning, 2 subtests passed in 63.58s (0:01:03)
```
exit=0

## ruff check .

```text
All checks passed!
```
exit=0

## ruff check direct Lot 1 modules

```text
All checks passed!
```
exit=0

## mypy --strict Lot 1 modules

```text
Success: no issues found in 3 source files
```
exit=0

## git diff 05fa3c8..HEAD -- 03_progressions premiere terminale 02_modeles_documents

```text
```
exit=0

## make judge U=P05

```text
test -n "P05"
python scripts/substance_judge.py --unit "P05" --level premiere --offline-fixture "tests/fixtures/substance_judge/P05.json" --output "01_build_reports/P05_substance_review.json"
verdict écrit : 01_build_reports/P05_substance_review.json
python scripts/check_substance_anchors.py "01_build_reports/P05_substance_review.json" --repo-root .
=== Vérification de substance — unité P05 (premiere) ===
juge: offline-fixture  auteur: codex-authoring-agent

🟠 P-TABLE-01: needs_content
    - preuve cours        : absente
    - preuve entraînement : absente
    - preuve correction   : absente
      · 1 alerte(s) scientifique(s) signalée(s)

🟠 P-TABLE-02: needs_content
    - preuve cours        : absente
    - preuve entraînement : absente
    - preuve correction   : absente
      · 1 alerte(s) scientifique(s) signalée(s)

=== Bilan ===
validées (effectif) : 0
needs_content       : 2
BLOCKER             : 0
verdicts dégradés   : 0
```
exit=0

## Grep-Garde

```text
```
raw_exit=1
interpreted_exit=0 (empty output expected)

## python scripts/check_status_promotion_guard.py

```text
check_status_promotion_guard: PASS (0 promotion positive)
```
exit=0

## python scripts/check_no_private_data.py

```text
check_no_private_data: PASS
```
exit=0
